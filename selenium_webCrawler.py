#importing dependencies
from selenium import webdriver
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import pandas as pd

# input zip_code and distance_radius
zip_code = 98012 #input("Enter Your Zip Code : ")
distance_radious = 3 #input("Enter Radious of the Search : ")

#Web Url
main_url = ("https://www.tred.com/buy?body_style=&distance="+str(distance_radious)+"&exterior_color_id=&make=&miles_max=100000&miles_min=0&model=&page_size=24&price_max=100000&price_min=0&query=&requestingPage=buy&sort=desc&sort_field=updated&status=active&year_end=2022&year_start=1998&zip="+str(zip_code))

#Web Driver
driver = webdriver.Chrome(executable_path=r'C:\Users\Adeem Akhtar\Anaconda3\envs\DVizTest\Lib\site-packages\chromedriver_chrome\chromedriver.exe')

#Function to search all the posts on the overall page

def search_products(pram ,pram_url):
    # driver = webdriver.Firefox(executable_path=r'C:\Users\Adeem Akhtar\Anaconda3\envs\DVizTest\Lib\site-packages\geckodriver_firefox\geckodriver.exe')
    driver.get(pram_url)

    # Dynamic page scroller
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(3)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # Extracting all the div containing card posts
    containers = driver.find_elements_by_class_name(str(pram))
    return containers

posts = search_products('card', main_url)
print("Total Posts: ", len(posts))

#Extracting web links to get the summaries and other details of the individua post
links = []
for eli in posts:
    post_card = eli.find_element_by_class_name('grid-box-container')
    link_card = post_card.find_elements_by_tag_name('a')
    if(len(link_card)>0):
        links.append(link_card[0].get_property('href'))
print(links)
driver.close()

#----------------------------------------------------------------------------------
#Visiting Each Post WebPage to Extract Data
cols=['Name', 'Price','Vehicle Summary', 'Vehicle Options']
output_df = pd.DataFrame(columns=cols)

for post_url in links:
    driver = webdriver.Chrome(executable_path=r'C:\Users\Adeem Akhtar\Anaconda3\envs\DVizTest\Lib\site-packages\chromedriver_chrome\chromedriver.exe')
    driver.get(post_url)

    # Car Price

    try:
        prices = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'price-box'))
        )
        car_price = prices.find_element_by_xpath('//*[@id="header-box"]/div/div/div[2]/div/div/h2')
        price = car_price.text

    except:
        driver.close()
        continue

    # Car Name

    try:
        names = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'vdp-content'))
        )
        car_name = names.find_element_by_xpath('//*[@id="react"]/div/div/div[2]/div[5]/div[2]/div/h1[1]')
        name_split = car_name.text
        name_split = name_split.split()
        name = ' '.join(name_split[1:-2])

    except:
        driver.close()
        continue

    # Car Summary
    vehicle_summary = []

    try:
        summary_tables = WebDriverWait(driver, 3).until(
            EC.presence_of_all_elements_located((By.ID, 'summary-table'))
        )
        car_summary_table = summary_tables[1].find_element_by_tag_name('tbody')
        car_summary_table_th = car_summary_table.find_elements_by_tag_name('th')
        car_summary_table_td = car_summary_table.find_elements_by_tag_name('td')
        vehicle_summary = []
        for th, td in zip(car_summary_table_th[1:], car_summary_table_td):
            vehicle_summary.append(th.text + td.text)

    except:
        driver.close()
        continue

    # Option table
    vehicle_options = []

    try:
        option_tables = WebDriverWait(driver, 3).until(
            EC.presence_of_all_elements_located((By.ID, 'options-table'))
        )
        car_option_table = option_tables[0].find_element_by_tag_name('tbody')
        car_option_td = car_option_table.find_elements_by_tag_name('td')
        for td in car_option_td:
            vehicle_options.append(td.text)

    except:
        driver.close()
        continue

    #print(options)

    Data = [[name, price, vehicle_summary, vehicle_options]]
    print(Data[0])
    temp_row_df = pd.DataFrame(Data, columns=cols)
    output_df = output_df.append(temp_row_df)

    driver.close()

output_df.to_excel("Scraped_Data_File.xlsx", sheet_name='Sheet_name_1', index=False)

