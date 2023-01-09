
# fetch https://www.harriscomputer.com/news/tag/news/page/1 up to 9

import requests
from bs4 import BeautifulSoup
import os
import json

url = 'https://velasoftwaregroup.com/news/'

articles = []
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
posts = soup.find_all('article', class_='post')
for post in posts:
    article = {}
    a_tag = post.find('a')
    article["title"] = a_tag.find('h4').text
    article["link"] = a_tag['href']
    article["date"] = post.find('span', class_='entry-date').text.strip()
    article_soup = BeautifulSoup(requests.get(article["link"]).text, 'html.parser')
    article["content"] = article_soup.find('div', class_='entry-content').decode_contents()
    articles.append(article)
    print(article)

with open('fetchedArticles.json', 'w') as f:
    json.dump(articles, f)