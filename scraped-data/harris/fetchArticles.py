
# fetch https://www.harriscomputer.com/news/tag/news/page/1 up to 9

import requests
from bs4 import BeautifulSoup
import os
import json

# Set the base URL and the maximum number of pages to crawl
base_url = 'https://www.harriscomputer.com/news/tag/news/page/'
max_pages = 9

articles = []
# Crawl the pages
for page in range(1, max_pages + 1):
    url = f'{base_url}{page}/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    h2_tags = soup.find_all('h2', class_='pwr-post-item__title')
    for h2_tag in h2_tags:
        article = {}
        article["title"] = h2_tag.text
        a_tag = h2_tag.find_parent('a')
        article["link"] = a_tag['href']
        article_soup = BeautifulSoup(requests.get(article["link"]).text, 'html.parser')
        # find all p and span tags in #hs_cos_wrapper_post_body until #French is found
        p_tags = article_soup.find(id="hs_cos_wrapper_post_body").find_all(["p", "span", "a"])
        paragraphs = []
        for p in p_tags:
            if p.get("id") == "French":
                break
            paragraphs.append(p.decode_contents())
        article["content"] = "".join(paragraphs)
        articles.append(article)
        print(article)

with open('fetchedArticles.json', 'w') as f:
    json.dump(articles, f)