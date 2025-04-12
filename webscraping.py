#Author: Praneeth Sai Ummadisetty
# Date: 04-08-2025
# Description: This program is used to get the info from the internet about individual stocks and send it to predictor
#This is a testing file where we are trying new methods to retrieve data from the web

# from urllib.request import urlopen
#
# url = "http://olympus.realpython.org/profiles/aphrodite"
# page = urlopen(url)
# print(page)
# url_Content = page.read()
# print(url_Content)
# html = url_Content.decode("utf-8")
# title = html.find("<title>") + len("<title>")
# endTitle = html.find("</title")
# print(title,endTitle)
# finalTitle = html[title:endTitle]
# print(finalTitle)
# print(html)

#Scraping using BeautifulSoup
'''
import urllib.robotparser
import requests
from bs4 import BeautifulSoup
import certifi
import ssl

url = "https://finance.yahoo.com/quote/AAPL/news"
ssl_context = ssl.create_default_context(cafile=certifi.where())
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64"}
response = requests.get(url, headers=headers, verify=certifi.where() )
soup = BeautifulSoup(response.text, "html.parser")
articles = soup.select("li.js-stream-content")
print(f"\n Latest news for Apple(AAPL):\n" + "-"*40)
print(articles)
for article in articles[:5]:
    print(article)
    title_tag = article.find("h3")
    link_tag = article.find("a", href=True)

    if title_tag and link_tag:
        title = title_tag.text.strip()
        link = "https://finance.yahoo.com" + link_tag["href"]
        print(f"\n{title}\n{link}")
'''

#Scraping using Selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
url = "https://finance.yahoo.com/quote/AAPL/news"
driver.get(url)
time.sleep(3)
articles = driver.find_elements(By.CSS_SELECTOR, "li.js-stream-content")
print(f"\nLatest news for Apple (AAPL):\n" + "-"*40)
for article in articles[:5]:  # Limit to top 5 news items
    try:
        title = article.find_element(By.TAG_NAME, "h3").text.strip()
        link = article.find_element(By.TAG_NAME, "a").get_attribute("href")
        print(f"\n📰 {title}\n🔗 {link}")
    except:
        continue

driver.quit()


# rp = urllib.robotparser.RobotFileParser()
# rp.set_url("https://finance.yahoo.com/robots.txt")
# rp.read()
#
# # Check if you're allowed to scrape a URL
# print(rp.can_fetch("*", "https://finance.yahoo.com/quote/AAPL/news"))
