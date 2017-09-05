# Author
# Praneet Kumar, B.Tech CSE
# NIT Silchar, Class of 2019

from selenium import webdriver
from datetime import datetime
from datetime import timedelta
import Send_Text
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# ----------------  USER INPUT  ---------------- #

Source_Airport_Code = 'ixs'         # Enter only the airport code and not the name.
Destination_Airport_Code = 'del'

DOJ = '03/12/2017'                  # dd/mm/yyyy

Flexible_Dates = 1
''' Set to 0 if you are travelling only on a fixed date. If your dates are flexible,
enter the required number (> 0) and the script will also crawl the dates ahead of the DOJ. Eg. if DOJ = 03-12-2017 and 
Flexible_Dates = 2, the script will also crawl 04-12-2017 and 05-12-2017. '''

Class = 'E'                         # E : Economy, B : Business

Adults = '1'                        # Max 9 passengers
Children = '0'
Infants = '0'

Threshold_Price = 6000
''' Enter the total threshold value. Eg. if you are 2 passengers and you want the
price for each passenger to be a min of 2500, enter 5000 and not 2500. '''

Time_Interval = 1                   # In minutes. Crawls again after the given time interval.


# --------------- DO NOT CHANGE --------------- #

min_price = 1000000                 # Initialize variables
count = 0
count1 = 0
price_list = []


# ---------------- CHECK FOR VALID INPUT CONDITIONS ----------------- #

if (int(Adults) + int(Children) + int(Infants)) > 9:
    print('Sorry, only 9 passengers are allowed at max.')
    exit()

if Flexible_Dates < 0:
    print("Sorry, only positive integer values are accepted for flexible dates.")
    exit()

if int(Flexible_Dates) != Flexible_Dates:
    print("Sorry, only positive integer values are accepted for flexible dates.")
    exit()

if int(Adults) < 0 or int(Children) < 0 or int(Infants) < 0 or (int(Adults) + int(Children) + int(Infants)) == 0:
    print("Sorry, check your passenger count once again.")
    exit()

if Class is 'E':
    COT = 'Economy'
elif Class is 'B':
    COT = 'Business'
else:
    print('Sorry, wrong class of travel entered.')
    exit()

date = datetime.strptime(DOJ, "%d/%m/%Y").date()
print("\n-----------------------  BAAP (Best Available Air Price) -----------------------\n")
print("You searched for...\n")

while count1 is 0:
    for j in range(0, Flexible_Dates + 1):
        new_date = str(date + timedelta(days=j))
        year = new_date[0:4]
        month = new_date[5:7]
        day = new_date[8:10]

        # -----------------------  GENERATE URL -------------------------- #

        url = 'https://www.cleartrip.com/flights/results?from=' + Source_Airport_Code.upper() + '&to=' + \
              Destination_Airport_Code.upper() + '&depart_date=' + day + "/" + month + "/" + year + '&adults=' + \
              Adults + '&childs=' + Children + '&infants=' + Infants + '&class=' + COT + \
              '&airline=&carrier=&intl=&sd=&page=loaded'

        # -------------------- INITIALIZE CHROMEDRIVER ------------------- #

        driver = webdriver.Chrome('E:\Python\chromedriver.exe')
        driver.set_window_position(-10000, 0)
        driver.get(url)
        try:
            WebDriverWait(driver, 60).until(  # Explicit wait to ensure that page has fully loaded
                EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Flexible with dates?"))
            )
        except:
            pass

        # -------------------- PRINT THE INPUT DATA -------------------- #

        for i in driver.find_elements_by_class_name('truncate'):     # Minor crawler which prints journey details
            print(i.text)
            count += 1
            if count is 2:
                count = 0
                break

        # ----------------------  CRAWLER  ------------------- #

        for i in driver.find_elements_by_xpath(
                "//th[contains(@id,'BaggageBundlingTemplate')]/span"):  # Add all the prices to an array
            val = str(i.get_attribute('data-pr'))
            price_list.append(val)
        length = len(price_list)

        for i in range(0, length):  # Find minimum price.
            if int(price_list[i]) <= min_price:
                min_price = int(price_list[i])
        if min_price is 1000000:
            print("\nSorry, check your airport codes or DOJ once again.")
            exit()

        if Class is 'E':
            print("Class : Economy")
        elif Class is 'B':
            print("Class : Business")

        print("\nCheapest price : ₹" + str(min_price) + "\n")  # Print minimum price

        driver.quit()  # Quit the browser

        # -----------------------  SEND TEXT  ------------------- #

        if min_price <= Threshold_Price:
            q = Send_Text.sms('username', 'password')
            message = "Flight prices dropped to Rs." + str(min_price) + " for " + day + "-" + month + "-" + year
            print(message)
            q.send('7086831381', message)
            n = q.msgSentToday()
            q.logout()
            exit()

    time.sleep(60*Time_Interval)