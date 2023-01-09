
# fetch https://jonassoftware.com/category/acquisitions and find all h2.entry-title tags and extract the child a tag href attribute. Then paginate though all the pages with the url format https://jonassoftware.com/category/acquisitions/page/2/ and so on.

import requests
from bs4 import BeautifulSoup
import os
import json

acqTerms = ['acquires', 'acquisition']

# Set the base URL and the maximum number of pages to crawl
base_url = 'https://www.csisoftware.com/category/press-releases/'
max_pages = 21

articles = []
# Crawl the pages
for page in range(1, max_pages + 1):
    url = f'{base_url}/page/{page}'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    h2_tags = soup.find_all('h2', class_='sfnewsTitle')
    for h2_tag in h2_tags:
        article = {}
        a_tag = h2_tag.find('a')
        article["title"] = a_tag.text
        article["link"] = a_tag['href']
        article["date"] = h2_tag.find_next_sibling('div').text.strip()
        # if article["text"] includes any of the acqTerms
        if any(acqTerm in article["title"].lower() for acqTerm in acqTerms):
            #  removing ../ parts from article["link"]
            article["link"] = article["link"].replace("../", "")
            # turn relative url article["link"] into absolute url
            article["link"] = os.path.join(base_url, article["link"])
            article_soup = BeautifulSoup(requests.get(article["link"]).text, 'html.parser')
            print (article["link"])
            article["content"] = article_soup.find('div', class_='sfnewsContent sfcontent').decode_contents()
            articles.append(article)
            print(article)

with open('fetchedArticles.json', 'w') as f:
    json.dump(articles, f)