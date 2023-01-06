# Import the webdriver and By classes from the selenium module
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import re
import getpass

# Set the username and password to empty strings

userdata = ["name","pass","consist"]
options = Options()
options.headless = True
# Create a new Firefox webdriver
driver = webdriver.Firefox(options=options)

def startUp():
    print("\nWelcome this script is made to make it easier to look for apartment without actually "
          "having to go in on the web page.\n")
    print("Also the settings are ment to be persistent so you can add this as a automatic service\n"
          "i would recommend to put it on 2am every day as new apartments get added att 1am\n")

    forLogin = open("userdata.txt", "r")
    print(forLogin.readlines()[2])
    forLogin.close()

    if forLogin == "n":
        print("I will not check your login. So wright it correctly or it wont work")
        userdata[0] = input("Personnummer eller E-post:\n")
        # add encryption
        userdata[1] = getpass.getpass(prompt="Lösenord:\n")
        userdata[2] = input("Spara användardata: Y/n\n")or "y"
        if userdata[2] == "y":
            print("Makes the file")

            userFile = open("userdata.txt", "wt")
            userFile.writelines(userdata[0])
            userFile.writelines(userdata[1])
            userFile.writelines(userdata[2])
            userFile.close()

            # open and read the file after the appending:
            userFile = open("userdata.txt", "r")
            print(userFile.readlines())
            userFile.close()
            print("sparat")

    print(userdata)


def login():
    # Navigate to the login page

    driver.get('https://nya.boplats.se/framelogin?loginfailed=&amp;complete=true')

    # Find the username field and send the specified keys (empty in this case)
    driver.find_element(By.XPATH, "//*[@id=\"username\"]").send_keys(userdata[0])

    # Find the password field and send the specified keys (empty in this case)
    driver.find_element(By.XPATH, "//*[@id=\"password\"]").send_keys(userdata[1])

    # Find the login button and click it
    driver.find_element(By.XPATH, "//*[@id=\"loginform-submit\"]").click()

    if checkCounter() is True:
        lookForApartment()

def checkCounter():
    bol = False
    driver.get('https://nya.boplats.se/minsida/ansokta')
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Find the first p element with the 'story' class

    clean = soup.find("span", class_="application-count")

    # Print the contents of the p element
    count = int(re.sub('[\W_]+', " ", clean.text))
    print("Mängder sökta som är fortfarande sökande " + count)
    if count != 5:
        bol = True

    return bol

def lookForApartment():
    #make an array for changing the settings for the filter
    driver.get('https://nya.boplats.se/sok?types=1hand&objecttype=alla&rent=7000&squaremeters=40&rooms=3')
    print("look")


startUp()
driver.quit()
