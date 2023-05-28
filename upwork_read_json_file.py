import json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (TimeoutException,)

#this script reads data from a json file in the upworkDataFile
#the data is then parsed appropriately to extract counsellor page details
# the parsed data is then used by the webcrawler to cycle through various pages on the site
#extract certain data and finally save it to a csv file

#this script was also setup and run on a linux environment so certain configurations may not work


PATH='/snap/bin/geckodriver'
driver=webdriver.Firefox(service=Service(PATH))

f=open('./upworkDataFile/counselor_directory.json')
file_contents=f.read()
parsed_json=json.loads(file_contents)

textReviewCount=0
videoReviewCount=0

videoReviews=list()
textReviews=list()
totalReviews=list()

messaging=list()
liveChat=list()
phone=list()
video=list()

names=list()
urls=list()
ids=list()
slugs=list()
licensing=list()
clinicalApproach=list()

df=pd.DataFrame()

for i in parsed_json['response']['data']:
    slug=i['slug']
    url=f"https://www.betterhelp.com/{slug}/"

    driver.get(url=url)
    try:
        WebDriverWait(driver,2).until(
            EC.presence_of_element_located((By.ID,'404'))
        )
    except Exception as e:
        print('****')
    finally:
        urls.append(url)
        names.append(i['full_name'])
        slugs.append(slug)
        ids.append(i['id'])

        try:
            WebDriverWait(driver,3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR,'.fa-video'))
            )
        except TimeoutException:
            video.append('No')
        finally:
            video.append('Yes')
    
        #messaging
        try:
            WebDriverWait(driver,3).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR,'.fa-comments'))
            )
        except TimeoutException:
            messaging.append('No')
        finally:
            messaging.append('Yes')
    
        #phoneService
        try:
            WebDriverWait(driver,3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR,'.fa-phone'))
            )
        except TimeoutException:
            phone.append('No')
        finally:
            phone.append('Yes')

        #live_chat_service
        try:
            WebDriverWait(driver,3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR,'.fa-solid'))
            )
        except TimeoutException:
            liveChat.append('No')
        finally:
            liveChat.append('Yes')
        
        
        #finding video and text review counts
        
        try:
            WebDriverWait(driver,3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR,'#video-testimonials'))   
            )
        except TimeoutException:
            videoReviewCount=0
        finally:
            videoReviewCount=len(driver.find_elements(By.CSS_SELECTOR,'#video-testimonials'))
        #finding text testimonials
        try:
            WebDriverWait(driver,3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR,'div.testimonial:nth-child(2) > div:nth-child(1)'))
            )
        except TimeoutException:
            textReviewCount=0
        finally:
            textReviewCount=len(driver.find_elements(By.CSS_SELECTOR,'div.testimonial:nth-child(2) > div:nth-child(1)'))
        
        licensing.append(i['pretty_license_text'])
        clinicalApproach.append(i['clinical_approaches'][0:len(i['clinical_approaches'])-1])
        
        videoReviews.append(videoReviewCount)
        textReviews.append(textReviewCount)
        totalReviews.append(videoReviewCount+textReviewCount)
        
        print(f'Licensing:{len(licensing)}')

df['ID']=pd.Series(ids)
df['Slug']=pd.Series(slugs)
df['Url']=pd.Series(urls)
df['Name']=pd.Series(names)
df['Video Review Count']=pd.Series(videoReviews)
df['Text Review Count']=pd.Series(textReviews)
df['Total Review Count']=pd.Series(totalReviews)
df['Messaging Service']=pd.Series(messaging)
df['Live Chat Service']=pd.Series(liveChat)
df['Phone Service']=pd.Series(phone)
df['Video Service']=pd.Series(video)
df['Licensing']=pd.Series(licensing)
df['Clinical Approaches']=pd.Series(clinicalApproach)

df.to_csv('./upworkDataFile/final.csv')

driver.close()

f.close()