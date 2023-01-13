import re
import getpass
import platform
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
from datetime import datetime

today = datetime.today().date()
day_of_month = today.day
print(day_of_month)

options = Options()
options.headless = True
driver = webdriver.Firefox(options=options)

system = platform.system()
count = 0
count_left = 0
userdata = ["name", "pass", "consist", "n"]
url_filter = ["types", "object_type", "rent", "square_meters", "rooms", "n"]


def clear_screen():
    switcher = {
        "Darwin": subprocess.run('clear', shell=True),
        "Windows": subprocess.run('cls', shell=True),
        "Linux": subprocess.run('clear', shell=True)
    }
    return switcher.get(system)


def start_up():
    global userdata
    print(system)
    print("\nWelcome, this script is made to make it easier to look for apartment without actually "
          "having to go in on the web page.\n")
    print("Also the settings are ment to be persistent so you can add this as a automatic service\n"
          "i would recommend to put it on 2am every day as new apartments get added att 1am\n")

    clear_screen()

    if userdata[3] != "x":
        try:
            for_login = open("userdata.txt", "r", encoding='utf-8')
            userdata[3] = for_login.readlines()[2]
            for_login.close()
        except IndexError:
            userdata[3] = "n"
        except FileNotFoundError:
            userdata[3] = "n"

    if userdata[3] == "n":

        print("I will not check your login. So wright it correctly or it wont work")
        userdata[0] = input("Personnummer eller E-post:\n")
        # TODO: add encryption
        userdata[1] = getpass.getpass(prompt="Lösenord:\n")
        userdata[2] = input("Spara användardata: Y/n\n") or "y"

        if userdata[2] == "y":
            print("Makes the file")

            user_file = open("userdata.txt", "wt", encoding='utf-8')
            for line in userdata:
                user_file.writelines(line + "\n")

            user_file.close()
            print("sparat")
    else:

        for_login = open("userdata.txt", "r", encoding='utf-8')
        userdata = [re.sub(r'\n', '', i) for i in for_login.readlines()]
        for_login.close()

    login()


def login():
    global userdata
    driver.get('https://nya.boplats.se/framelogin?loginfailed=&amp;complete=true')

    driver.find_element(By.XPATH, "//*[@id=\"username\"]").send_keys(userdata[0])

    driver.find_element(By.XPATH, "//*[@id=\"password\"]").send_keys(userdata[1])

    driver.find_element(By.XPATH, "//*[@id=\"loginform-submit\"]").click()

    # checking if valid userdata
    if check_login():

        # boplats doesn't let you have more than 5 ongoing apartments so if its 5 it skips looking
        if check_counter():
            filter_funktion()
            print("scriptet går igenom hemsidorna. detta kan ta ett liten stund")
            search_and_destroy()

    else:
        # looping back to ask for new userdata y/n are reserved
        userdata = "x"
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
    global count, count_left
    bol = False
    driver.get('https://nya.boplats.se/minsida/ansokta')
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    # the only objects that use class removebutton is the actually applied apartments
    count = len(soup.find_all(class_='removebutton'))
    count_left = 5 - count
    print("Mängder sökta lägenheter " + str(count) + "\nkvar att söka " + str(count_left))
    if int(count) != 5:
        bol = True

    return bol


def filter_funktion():
    global url_filter
    if url_filter[4] != "x":
        try:
            for_filter = open("filterdata.txt", "r", encoding='utf-8')
            url_filter[4] = for_filter.readlines()[4]
            for_filter.close()
        except IndexError:
            url_filter[4] = "n"
        except FileNotFoundError:
            url_filter[4] = "n"

    if url_filter[4] == "n":
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
        url_filter[0] = input("standard är 0\n"
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
        url_filter[0] = housing_types[int(url_filter[0])]
        url_filter[1] = input("standard är 1000000\nHyra (max) kr: ") or "1000000"
        url_filter[2] = input("standard är 5\nBoarea (min) kvadrat meter: ") or "5"
        url_filter[3] = input("standard är 1\nAntal rum (min) ") or "1"
        url_filter[4] = input("standard är y\nSpara val y/n: ") or "y"

        if url_filter[4] == "y":
            print("Makes the file")
            filter_file = open("filterdata.txt", "wt", encoding='utf-8')
            for line in url_filter:
                filter_file.writelines(line + "\n")
            filter_file.close()
            print("sparat")
    # reading the saved filter data from before
    else:
        filter_file = open("filterdata.txt", "r", encoding='utf-8')
        url_filter = [re.sub(r'\n', '', i) for i in filter_file.readlines()]
        filter_file.close()


def search_and_destroy():
    global url_filter, count_left
    link_list = []
    new_link_list = []
    procent = []

    url_filter = "https://nya.boplats.se/sok?types=1hand" \
                 "&objecttype=" + url_filter[0] + \
                 "&rent=" + url_filter[1] + \
                 "&squaremeters=" + url_filter[2] + \
                 "&rooms=" + url_filter[3] + \
                 "&filterrequirements=on"

    driver.get(url_filter)

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
            if len(numbers) >= 2:
                procent.append(numbers[1]/numbers[0])
                new_link_list.append(link)
                """bool = True
    if bool == True:
        combined = list(zip(new_link_list, procent))
        combined.sort(key=lambda x: x[1], reverse=True)"""
# TODO: more testing most be done 
    i = 0
    for link in new_link_list:
        if i == count_left:
            break
        else:
            print("söker till lägenheten: " + link)
            driver.get(link)
            driver.find_element(By.XPATH, "//*[@id=\"large-apply-button\"]").click()
        i = +1
    if not new_link_list:
        print("Det finns inget att söka")
    print(new_link_list)


start_up()
driver.quit()
