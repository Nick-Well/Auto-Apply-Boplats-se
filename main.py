from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import re
import getpass

options = Options()
options.headless = True
driver = webdriver.Firefox(options=options)



userdata = ["name", "pass", "consist"]


def start_up():
    global userdata
    print("\nWelcome this script is made to make it easier to look for apartment without actually "
          "having to go in on the web page.\n")
    print("Also the settings are ment to be persistent so you can add this as a automatic service\n"
          "i would recommend to put it on 2am every day as new apartments get added att 1am\n")

    try:
        for_login = open("userdata.txt", "r")
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

            user_file = open("userdata.txt", "wt")
            user_file.writelines(userdata[0] + "\n")
            user_file.writelines(userdata[1] + "\n")
            user_file.writelines(userdata[2] + "\n")
            user_file.close()

            # open and read the file after the appending:
            user_file = open("userdata.txt", "r")
            print(user_file.readlines())
            user_file.close()
            print("sparat")
    else:
        for_login = open("userdata.txt", "r")
        userdata = [re.sub(r'\n', '', i) for i in for_login.readlines()]
        for_login.close()
    login()


def login():

    driver.get('https://nya.boplats.se/framelogin?loginfailed=&amp;complete=true')

    driver.find_element(By.XPATH, "//*[@id=\"username\"]").send_keys(userdata[0])

    driver.find_element(By.XPATH, "//*[@id=\"password\"]").send_keys(userdata[1])

    driver.find_element(By.XPATH, "//*[@id=\"loginform-submit\"]").click()
    if check_login():
        if check_counter():
            look_for_apartment()
    else:
        for_login_ram = "n"
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

    # Find the first p element with the 'story' class

    clean = soup.find("span", class_="application-count")

    # Print the contents of the p element
    count = re.sub('[\W_]+', "", clean.text)
    print("Mängder sökta lägenheter " + count)
    if int(count) != 5:
        bol = True

    return bol


def look_for_apartment():
    filter = ["type", "rent", "square", "room"]
    driver.get('https://nya.boplats.se/sok?types=1hand&objecttype=alla&rent=7000&squaremeters=40&rooms=3')
    print(filter)
    #work
    # TODO: make an array for changing the settings for the filter


start_up()
driver.quit()
