# Author
# Praneet Kumar, B.Tech CSE
# NIT Silchar, Class of 2019

from selenium import webdriver
from datetime import datetime
from datetime import timedelta
import time
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys


# ----------------  USER INPUT  ---------------- #

Source_Airport_Code = 'del'         # Enter only the airport code and not the name.
Destination_Airport_Code = 'ixl'

DOJ = '02/10/2018'                  # dd/mm/yyyy

Flexible_Dates = 2
''' Set to 0 if you are travelling only on a fixed date. If your dates are flexible,
enter the required number (> 0) and the script will also crawl the dates ahead of the DOJ. Eg. if DOJ = 02/10/2018 and 
Flexible_Dates = 2, the script will also crawl 03/10/2018 and 04/10/2018. '''

Class = 'E'                         # E : Economy, B : Business

Adults = '1'                        # Max 9 passengers
Children = '0'
Infants = '0'

Threshold_Price = 2500
''' Enter the total threshold value. Eg. if you are 2 passengers and you want the
price for each passenger to be a min of 2500, enter 5000 and not 2500. '''

mobile_number_input = ''                    # Your way2sms mobile number/username
password_input = ''                         # Your way2sms password
receiving_number_input = ''                 # The mobile number on which you want the text to be delivered.

Time_Interval = 15                          # In minutes. Crawls again after the given time interval.


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

        driver.quit()

        # -------------------------  SEND TEXT  ---------------------------- #

        if min_price <= Threshold_Price:

            message_input = "Flight prices dropped to Rs." + str(min_price) + " for " + day + "-" + month + "-" + year
            print(message_input)

            os.startfile('E:\Backup\My Music\Bhojpuri\Chhalakata Hamro Jawaniya.mp3')   # Play music from your PC

            driver = webdriver.Chrome('E:\Python\chromedriver.exe')
            url = 'http://www.way2sms.com'
            driver.get(url)
            try:
                WebDriverWait(driver, 20).until(  # Explicit wait to ensure that page has fully loaded
                    EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Dummy text"))
                )
            except:
                pass

            username = driver.find_element_by_id('username')
            password = driver.find_element_by_id('password')

            username.send_keys(mobile_number_input)
            password.send_keys(password_input)
            password.send_keys(Keys.RETURN)

            send_sms = driver.find_element_by_xpath('//a[@href="' + "javascript:loadSMSPage('sendSMS');" + '"]');
            send_sms.click()

            frame = driver.find_element_by_id('frame')
            driver.switch_to.frame(frame)

            receiving_number = driver.find_element_by_id('mobile')
            message_box = driver.find_element_by_id('message')
            send = driver.find_element_by_id('Send')

            receiving_number.send_keys(receiving_number_input)
            message_box.send_keys(message_input)
            send.click()
            try:
                WebDriverWait(driver, 20).until(  # Explicit wait to ensure that page has fully loaded
                    EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Dummy text"))
                )
            except:
                pass

            exit()

    time.sleep(60*Time_Interval)
