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
driver = webdriver.Firefox()
# options=options test without

system = platform.system()

for_login_ram = "n"
userdata = ["name", "pass", "consist"]
filter = ["types", "objecttype", "rent", "squaremeters", "rooms"]


def clear_screen():
    switcher = {
        "Darwin": subprocess.run('clear', shell=True),
        "Windows": subprocess.run('cls', shell=True),
        "Linux": subprocess.run('clear', shell=True)
    }
    return switcher.get(system)


def start_up():
    global userdata 
    global for_login_ram
    print(system)
    print("\nWelcome, this script is made to make it easier to look for apartment without actually "
          "having to go in on the web page.\n")
    print("Also the settings are ment to be persistent so you can add this as a automatic service\n"
          "i would recommend to put it on 2am every day as new apartments get added att 1am\n")
    clear_screen()
    if for_login_ram != "x":
        try:
            for_login = open("userdata.txt", "r", encoding='utf-8')
            for_login_ram = for_login.readlines()[2]
            for_login.close()
        except IndexError:
            for_login_ram = "n"
        except FileNotFoundError:
            for_login_ram = "n"

    if for_login_ram == "n":
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
    global for_login_ram
    driver.get('https://nya.boplats.se/framelogin?loginfailed=&amp;complete=true')

    driver.find_element(By.XPATH, "//*[@id=\"username\"]").send_keys(userdata[0])

    driver.find_element(By.XPATH, "//*[@id=\"password\"]").send_keys(userdata[1])

    driver.find_element(By.XPATH, "//*[@id=\"loginform-submit\"]").click()
    
    # checking if valid userdata
    if check_login():
        
        # boplats doesn't let you have more than 5 ongoing apartments so if its 5 it skips looking
        if check_counter():
            # TODO: working progress
            search_and_destroy(filter_funktion())

    else:
        # looping back to ask for new userdata y/n are resurved
        for_login_ram = "x"
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
    if int(count) != 5:
        bol = True

    return bol


def filter_funktion():
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
    filter[0] = input("standard är 0\nTyp av lägenhet. nr:"
                      "0.NORMAL\n"
                      "1.accessibility Adapted\n"
                      "2.community Accommodation\n"
                      "3.cooperative Lease\n"
                      "4.new Production\n"
                      "5.no Tenure\n"
                      "6.retirement Home\n"
                      "7.senior\n"
                      "8.short Time Lease\n"
                      "9.student\n") or 0
    filter[0] = housing_types[int(filter[0])]
    filter[1] = input("standard är 1000000\nHyra (max) kr:") or "1000000"
    filter[2] = input("standard är 5\nBoarea (min) kvadrat meter:") or "5"
    filter[3] = input("standard är 1\nAntal rum (min) ") or "1"

    filter_file = open("filterdata.txt", "wt", encoding='utf-8')
    for line in userdata:
        filter_file.writelines(line + "\n")
    filter_file.close()

    print("sparat")
    print(filter)
    return filter



def search_and_destroy(filter):
    url_filter = "https://nya.boplats.se/sok?types=1hand&objecttype="\
                + filter[0]+"&rent="+filter[1]+"&squaremeters="+filter[2]+"&rooms="+filter[3]+"&filterrequirements=on"
    driver.get(url_filter)


start_up()
# driver.quit()
