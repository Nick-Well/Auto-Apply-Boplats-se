import re
import getpass
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup



options = Options()
options.headless = True
driver = webdriver.Firefox(options=options)


for_login_ram = "n"
userdata = ["name", "pass", "consist"]
filter = ["types", "objecttype", "rent", "squaremeters", "rooms"]

#clear screan
subprocess.run('clear', shell=True)  # for Unix-based systems
subprocess.run('cls', shell=True)  # for Windows

def start_up():
    global userdata 
    global for_login_ram
    print("\nWelcome this script is made to make it easier to look for apartment without actually "
          "having to go in on the web page.\n")
    print("Also the settings are ment to be persistent so you can add this as a automatic service\n"
          "i would recommend to put it on 2am every day as new apartments get added att 1am\n")
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
            user_file.writelines(userdata[0] + "\n")
            user_file.writelines(userdata[1] + "\n")
            user_file.writelines(userdata[2] + "\n")
            user_file.close()

            # open and read the file after the appending:
            user_file = open("userdata.txt", "r", encoding='utf-8')
            print(user_file.readlines())
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
        
        #boplats doesnt let you have more then 5 ongoing apartments so if its 5 it skipps looking
        if check_counter():
            #TODO: working progress
            filter_funktion()
    else:
        #looping back to ask for new userdata y/n are resurved
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
    filter = ["types", "objecttype", "rent", "squaremeters", "rooms"]
    print("1.accessibilityAdapted\n 2.communityAccommodation\n 3.cooperativeLease\n 4.newProduction\n 5.noTenure\n 6.retirementHome\n 7.senior\n 8.shortTimeLease\n 9.student\n")
    filter[0] = input("0.normal\n")
    filter[1] = input("Hyra (max):\n")
    filter[2] = input("Spara användardata: Y/n\n") or "y"
    filter[3] = input("Personnummer eller E-post:\n")
    print(filter)
    #work
    # TODO: will return the array for the filter to the funktion that will scrape the apartments


def search_and_destroy():
    driver.get("https://nya.boplats.se/sok?types=1hand&objecttype="+"filter[0]"+"&rent="+"filter[1]"+"&squaremeters="+"filter[2]"+"&rooms="+"filter[3]"+"&filterrequirements=on")


start_up()
driver.quit()
