"""This module gets all headlines containing a keyword from a news API"""

import json
import requests
import logging

removed_articles = []
FORMAT= '%(levelname)s: %(asctime)s %(message)s'
logging.basicConfig(filename='log.log',format = FORMAT,level=logging.DEBUG)

def remove_punctuation(line: str) -> str:
    """Removes punctuation from a given string"""
    punctuation = '!"#$%&`()*+,./:;'
    for symbol in punctuation:
        line = line.replace(symbol, ' ')
    return line

def news_API_request(covid_terms = "Covid COVID-19 coronavirus") -> list:
    """Gets all news articles from API with key words in them"""

    base_url = "https://newsapi.org/v2/everything?"

    with open("config.json", 'r', encoding = 'UTF-8') as my_file:
        data = json.load(my_file)
        api_key = data["API_key"]

    covid_articles = []

    for term in covid_terms.split(" "):
        try:
            complete_url = base_url + "apiKey=" + api_key + "&q=" + term
            response = requests.get(complete_url)
            
            news_dict = response.json()
            articles = news_dict['articles']
            logging.info("News API request")
        except:
            logging.error("News API request failed")

        for article in articles:
            if article not in covid_articles:
                covid_articles.append(article)

    return  covid_articles

def add_removed_article(removed_headline: str):
    """Add an article headline to a list of removed headlines"""

    removed_articles.append(removed_headline)

def remove_deleted_articles(covid_articles: list) -> list:
    """Removes articles user has removed from the list"""
    for article in covid_articles:
        if article['title'] in removed_articles:
            covid_articles.remove(article)
    return covid_articles

def update_news() -> list:
    """Returns a list of all articles relating to the keywords,
    does not return articles that have been removed"""
    all_articles = news_API_request()
    all_articles = remove_deleted_articles(all_articles)

    return all_articles

news_API_request()
