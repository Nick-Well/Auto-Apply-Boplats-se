import re
import getpass
import platform
import subprocess
import time
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException

from bs4 import BeautifulSoup

today = datetime.today().date()
day_of_month = today.day

options = Options()
options.add_argument("-headless")
driver = webdriver.Firefox(options=options)

system = platform.system()


class UserData:
    def __init__(self, name, password, consist):
        self.name = name
        self.password = password
        self.consist = consist

    def __iter__(self):
        self.index = 0
        return self

    def __next__(self):
        if self.index == 0:
            result = self.name
        elif self.index == 1:
            result = self.password
        elif self.index == 2:
            result = self.consist
        else:
            raise StopIteration
        self.index += 1
        return result

    def __getitem__(self, index):
        if index == 0:
            return self.name
        elif index == 1:
            return self.password
        elif index == 2:
            return self.consist
        else:
            raise IndexError

    @classmethod
    def from_file(cls, file_path):
        with open(file_path, 'r') as f:
            data = [re.sub(r'\n', '', i) for i in f.readlines()]
            return cls(*data)


class UrlFilter:
    _instance = None

    def __init__(self, object_type, rent, square_meters, rooms, consist):
        self.object_type = object_type
        self.rent = rent
        self.square_meters = square_meters
        self.rooms = rooms
        self.consist = consist

    def __getitem__(self, index):
        if index == 0:
            return self.object_type
        elif index == 1:
            return self.rent
        elif index == 2:
            return self.square_meters
        elif index == 3:
            return self.rooms
        elif index == 4:
            return self.consist
        else:
            raise IndexError

    def __setitem__(self, index, value):
        if index == 0:
            self.object_type = value
        elif index == 1:
            self.rent = value
        elif index == 2:
            self.square_meters = value
        elif index == 3:
            self.rooms = value
        elif index == 4:
            self.consist = value
        else:
            raise IndexError

    @classmethod
    def from_file(cls, filename):
        with open(filename) as f:
            data = [line.strip() for line in f]
        return cls.get_instance(*data)

    @classmethod
    def get_instance(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = cls(*args, **kwargs)
        return cls._instance


class Counters:
    _instance = None

    def __init__(self, count, count_left):
        self.count = count
        self.count_left = count_left

    def __getitem__(self, index):
        if index == 0:
            return self.count
        elif index == 1:
            return self.count_left
        else:
            raise IndexError

    def __setitem__(self, index, value):
        if index == 0:
            self.count = value
        elif index == 1:
            self.count_left = value
        else:
            raise IndexError


def clear_screen():
    switcher = {
        "Darwin": subprocess.run('clear', shell=True),
        "Windows": subprocess.run('cls', shell=True),
        "Linux": subprocess.run('clear', shell=True)
    }
    return switcher.get(system)


def start_up():
    userdata = ["name", "pass", "consist"]
    user = UserData(*userdata)
    clear_screen()
    print("\nWelcome, this script is made to make it easier to look for apartment without actually "
          "having to go in on the web page.\n")
    print("Also the settings are ment to be persistent so you can add this as a automatic service\n"
          "I would recommend to put it on 2am every day as new apartments get added att 1am.\n")
    time.sleep(10)
    clear_screen()
    if user.consist != "x":
        try:
            for_login = open("userdata.txt", "r", encoding='utf-8')
            user.consist = for_login.readlines()[2]
            for_login.close()
        except IndexError:
            user.consist = "n"
        except FileNotFoundError:
            user.consist = "n"

    if user.consist == "n":

        print("I will not check your login. So wright it correctly or it wont work")
        user.name = input("Personnummer eller E-post:\n")
        user.password = getpass.getpass(prompt="Lösenord:\n")
        user.consist = input("Spara användardata: Y/n\n") or "y"

        if user.consist == "y":
            print("Makes the file")

            user_file = open("userdata.txt", "wt", encoding='utf-8')
            for line in user:
                user_file.writelines(line + "\n")

            user_file.close()
            print("sparat")
    else:
        user = UserData.from_file('userdata.txt')

    login(user)


def login(user):
    driver.get('https://nya.boplats.se/framelogin?loginfailed=&amp;complete=true')

    driver.find_element(By.XPATH, "//*[@id=\"username\"]").send_keys(user.name)

    driver.find_element(By.XPATH, "//*[@id=\"password\"]").send_keys(user.password)

    driver.find_element(By.XPATH, "//*[@id=\"loginform-submit\"]").click()

    # checking if valid userdata
    if check_login():

        # boplats doesn't let you have more than 5 ongoing apartments so if its 5 it skips looking
        if check_counter():
            filter_funktion()

    else:
        # looping back to ask for new userdata y/n are reserved
        user.consist = "x"
        print("login failed name or password was wrong")
        start_up()


def check_login():
    # being sneaky and taking somthing that is only visible wen logged in
    try:
        driver.find_element(By.XPATH, "/html/body/div[1]/div/div[5]/div[1]/div[1]/span[1]")
    except NoSuchElementException:
        return False
    return True


def check_counter():
    bol = False
    driver.get('https://nya.boplats.se/minsida/ansokta')
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    # the only objects that use class removebutton is the actually applied apartments
    Counters.count = len(soup.find_all(class_='removebutton'))
    Counters.count_left = 5 - Counters.count
    if Counters.count != 5:
        print("Activa sökningar för lägenheter: " + str(Counters.count)
              + "\nkvar att söka: " + str(Counters.count_left) + "\n")
        bol = True
    elif Counters.count_left == 0:
        print("Du har sökt max antal lägenheter för idag.")
    return bol


def filter_funktion():
    url_filter = ["object_type", "rent", "square_meters", "rooms", "consist"]
    poll_filters = UrlFilter(*url_filter)
    if poll_filters[4] != "x":
        try:
            for_filter = open("filterdata.txt", "r", encoding='utf-8')
            poll_filters[4] = for_filter.readlines()[4]
            for_filter.close()
        except IndexError:
            poll_filters[4] = "n"
        except FileNotFoundError:
            poll_filters[4] = "n"

    if poll_filters[4] == "n":
        housing_types = {
            0: "normal",
            1: "accessibilityAdapted",
            2: "communityAccommodation",
            3: "cooperativeLease",
            4: "newProduction",
            5: "noTenure",
            6: "retirementHome",
            7: "senior",
            8: "shortTimeLease",
            9: "student"
        }
        object_type_number = input("standard är 0\n"
                                   "0.NORMAL\n"
                                   "1.accessibility Adapted\n"
                                   "2.community Accommodation\n"
                                   "3.cooperative Lease\n"
                                   "4.new Production\n"
                                   "5.no Tenure\n"
                                   "6.retirement Home\n"
                                   "7.senior\n"
                                   "8.short Time Lease\n"
                                   "9.student\nTyp av lägenhet. nr:\n") or 0
        poll_filters.object_type = housing_types[object_type_number]
        poll_filters.rent = input("standard är 1000000\nHyra (max) kr: ") or "1000000"
        poll_filters.square_meters = input("standard är 5\nBoarea (min) kvadrat meter: ") or "5"
        poll_filters.rooms = input("standard är 1\nAntal rum (min) ") or "1"
        poll_filters.consist = input("standard är y\nSpara val y/n: ") or "y"

        if poll_filters.consist == "y":
            print("Makes the file")
            filter_file = open("filterdata.txt", "wt", encoding='utf-8')
            for line in poll_filters:
                filter_file.writelines(line + "\n")
            filter_file.close()
            print("sparat")
        search_and_destroy(poll_filters)
    # reading the saved filter data from before
    else:
        poll_filters = UrlFilter.from_file('filterdata.txt')
        print("Scriptet går igenom hemsidorna. Detta kan ta ett liten stund.")
        search_and_destroy(poll_filters)


def search_and_destroy(url_filters):
    link_list = []
    new_link_list = []
    procent = []

    url = "https://nya.boplats.se/sok?types=1hand" \
          "&objecttype=" + url_filters.object_type + \
          "&rent=" + url_filters.rent + \
          "&squaremeters=" + url_filters.square_meters + \
          "&rooms=" + url_filters.rooms + \
          "&filterrequirements=on"
    driver.get(url)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    # scrape for links
    for link in soup.find_all('a', class_="search-result-link"):
        href = link['href']
        link_list.append(href)
    # going through all the links
    for link in link_list:
        driver.get(link)
        element = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[6]"
                                                "/div/div/div/div/div/div[1]"
                                                "/div/div[2]/div[3]/p[5]/span[2]")
        cleaned_text = int(re.sub('[a-zA-Z\W_]', "", element.text))
        # singel out: one day deadline
        if cleaned_text == day_of_month:
            applicant = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[6]"
                                                      "/div/div/div/div/div/div[1]"
                                                      "/div/div[2]/div[4]/div[2]/p"
                                                      "/span/strong/a")
            text = applicant.text
            numbers = re.findall(r'\d+', text)
            # if you have applied there will only be one number so
            # checking if there's 2 gives you the option,
            # only to make a list that have apartment that you can apply too
            if len(numbers) == 2:
                procent.append(int(numbers[1]) / int(numbers[0]))
                new_link_list.append(link)
                combined = list(zip(new_link_list, procent))
                combined.sort(key=lambda x: x[1])
    clear_screen()
    i = 0
    for link in new_link_list:
        if i == Counters.count_left:
            break
        else:
            print("söker till lägenheten: " + link)
            driver.get(link)
            driver.find_element(By.XPATH, "//*[@id=\"large-apply-button\"]").click()
        i = i + 1
    if not new_link_list:
        print("Det finns inget att söka")
    print("har sökt: " + str(i) + " lägenheter")


start_up()
driver.quit()
