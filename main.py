import re
import getpass
import platform
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup


options = Options()
options.headless = True
# TODO: make in invisible
driver = webdriver.Firefox()
# options=options test without

system = platform.system()

userdata = ["name", "pass", "consist", "n"]
filter = ["types", "object_type", "rent", "square_meters", "rooms", "n"]


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
            search_and_destroy()

    else:
        # looping back to ask for new userdata y/n are resurved
        userdata = "x"
        print("login failed name or password was wrong")
        start_up()


def check_login():
    try:
        driver.find_element(By.XPATH, "/html/body/div[1]/div/div[5]/div[1]/div[1]/span[1]")
    except NoSuchElementException:
        return False
    return True


def check_counter():
    bol = False
    driver.get('https://nya.boplats.se/minsida/ansokta')
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    clean = soup.find("span", class_="application-count")

    count = re.sub('[\W_]+', "", clean.text)
    print("Mängder sökta lägenheter " + count)
    # TODO: 5
    if int(count) != 6:
        bol = True

    return bol


def filter_funktion():
    global filter
    if filter[4] != "x":
        try:
            for_filter = open("filterdata.txt", "r", encoding='utf-8')
            filter[4] = for_filter.readlines()[4]
            for_filter.close()
        except IndexError:
            filter[4] = "n"
        except FileNotFoundError:
            filter[4] = "n"

    if filter[4] == "n":
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
        filter[0] = input("standard är 0\n"
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
        filter[0] = housing_types[int(filter[0])]
        filter[1] = input("standard är 1000000\nHyra (max) kr: ") or "1000000"
        filter[2] = input("standard är 5\nBoarea (min) kvadrat meter: ") or "5"
        filter[3] = input("standard är 1\nAntal rum (min) ") or "1"
        filter[4] = input("standard är y\nSpara val y/n: ") or "y"

        if filter[4] == "y":
            print("Makes the file")
            filter_file = open("filterdata.txt", "wt", encoding='utf-8')
            for line in filter:
                filter_file.writelines(line + "\n")
            filter_file.close()

        print("sparat")
    else:
        filter_file = open("filterdata.txt", "r", encoding='utf-8')
        filter = [re.sub(r'\n', '', i) for i in filter_file.readlines()]
        filter_file.close()


def search_and_destroy():
    global filter
    url_filter = "https://nya.boplats.se/sok?types=1hand" \
                 "&objecttype="+filter[0] +\
                 "&rent="+filter[1] +\
                 "&squaremeters="+filter[2] +\
                 "&rooms="+filter[3] +\
                 "&filterrequirements=on"

    driver.get(url_filter)

    # TODO: take all links from the page.
    # TODO: open one take out the information(how meny days intill dead line)
    # TODO: remove all except the ones that have dead line in one day. so import the day(time).
    #  and if one day take out where in the qeu you are. sort the list with highest "chans"
    #  proceed by pressing apply on all intill the counter is 5


start_up()
# driver.quit()
