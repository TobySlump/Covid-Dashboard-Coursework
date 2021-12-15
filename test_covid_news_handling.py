from covid_news_handling import remove_punctuation
from covid_news_handling import news_API_request
from covid_news_handling import update_news

def test_remove_punctuation():
    test_string = remove_punctuation("test : * string ^")
    assert("test string")

def test_news_API_request():
    articles = news_API_request()
    assert isinstance(articles, list)

def test_update_news():
    articles = update_news()
    assert isinstance(articles, list)



