"""This module contains the backend for the index file"""

from flask import Flask, render_template, request
from werkzeug.utils import redirect
import logging
import json
from covid_data_handler import covid_API_request, process_covid_csv_data,\
    parse_csv_data, schedule_covid_updates, scheduler
from covid_news_handling import add_removed_article, \
    update_news, remove_deleted_articles
from time_conversions import hhmm_to_seconds, current_time_hhmm

app = Flask(__name__)
FORMAT= '%(levelname)s: %(asctime)s %(message)s'
logging.basicConfig(filename='log.log',format = FORMAT,level=logging.DEBUG)
scheduled_updates = []
cases_in_last_week, current_hospital_cases, number_of_deaths, \
    local_cases_in_last_week = 0,0,0,0
news_articles_list = []

def update_complete(update_label: str):
    """Removes an update from the list when it has been executed"""

    for update in scheduled_updates:
        if update['title'] == update_label:
            scheduled_updates.remove(update)

def process_local_data():
    """Calls the functions to process the local covid data
     from covid_data_handler.py"""

    global local_cases_in_last_week
    local_cases_in_last_week = \
    process_covid_csv_data(parse_csv_data("api_data.csv"))[0]

def process_national_data():
    """Calls the functions to process the national covid data
     from covid_data_handler.py"""

    global cases_in_last_week, current_hospital_cases, number_of_deaths
    cases_in_last_week, current_hospital_cases, number_of_deaths = \
    process_covid_csv_data(parse_csv_data("api_data.csv"))

def update_news_list():
    """Updates the list of news articles"""

    global news_articles_list
    news_articles_list = update_news()

def repeat_update(event: dict):
    """Sets the update to repeat every 24 hours"""

    time_till_update = int(event['time']) + (3600*24)

    if event['updating'] == "data and news":
        e_1,e_2 = schedule_covid_updates(time_till_update, event['title'])
        e_3 = scheduler.enter(time_till_update,2,process_local_data)
        e_4 = scheduler.enter(time_till_update+1,2,process_national_data)

        e_5 = scheduler.enter(time_till_update,1,update_news_list)
        e_6 = scheduler.enter(time_till_update, 3, repeat_update, (event,))

    elif event['updating'] == "news":
        e_1 = scheduler.enter(time_till_update,1,update_news_list)
        e_2 = scheduler.enter(time_till_update, 3, repeat_update, (event,))

    elif event['updating'] == "data":
        e_1,e_2 = schedule_covid_updates(time_till_update, event['title'])
        e_3 = scheduler.enter(time_till_update,2,process_local_data)
        e_4 = scheduler.enter(time_till_update+1,2,process_national_data)

        e_5 = scheduler.enter(time_till_update, 3, repeat_update, (event,))

    else:
        logging.error("An invalid function was attmepted to repeat")

@app.route('/index')
def index():
    """Sends the index.html file the variables it wants
    and deals with user interaction with the website"""

    notif = request.args.get('notif')
    remove_update = request.args.get('update_item')
    update_time = request.args.get('update')
    update_label = request.args.get('two')
    repeat_checkbox = request.args.get('repeat')
    data_checkbox = request.args.get('covid-data')
    news_checkbox = request.args.get('news')

    if notif:
        global news_articles_list
        add_removed_article(notif)
        news_articles_list = remove_deleted_articles(news_articles_list)
        logging.info("Article removed from list")

    try:
        if remove_update:
            for update in scheduled_updates:
                if update['title'] == remove_update:
                    for events in range(0,5):
                        scheduler.cancel(update['events'][events])
                    scheduled_updates.remove(update)

    except:
        for update in scheduled_updates:
            if update['title'] == remove_update:
                scheduled_updates.remove(update)

    if data_checkbox and news_checkbox:

        time_till_update = hhmm_to_seconds(update_time) \
            - hhmm_to_seconds(current_time_hhmm())

        e_1,e_2 = schedule_covid_updates(time_till_update, update_label)
        e_3 = scheduler.enter(time_till_update,2,process_local_data)
        e_4 = scheduler.enter(time_till_update+1,2,process_national_data)

        e_5 = scheduler.enter(time_till_update,1,update_news_list)

        e_6 = scheduler.enter(time_till_update,2,\
            update_complete,(update_label,))

        scheduler_dict = {'title': update_label,
        'content': 'Update covid data and news articles in ' + \
            str(time_till_update) + ' seconds',
        'time': str(hhmm_to_seconds(update_time)),
        'events' : [e_1,e_2,e_3,e_4,e_5],
        'updating':'data and news'}

        if repeat_checkbox:
            repeat_update(scheduler_dict)
            scheduler_dict['content'] = 'Update covid data and news articles in ' \
            + str(time_till_update) + ' seconds, repeats every 24 hours'

        if scheduler_dict not in scheduled_updates:
            scheduled_updates.append(scheduler_dict)

        logging.info("Covid data and news update scheduled")

    elif data_checkbox:

        time_till_update = hhmm_to_seconds(update_time) \
            - hhmm_to_seconds(current_time_hhmm())

        e_1,e_2 = schedule_covid_updates(time_till_update, update_label)
        e_3 = scheduler.enter(time_till_update,2,process_local_data)
        e_4 = scheduler.enter(time_till_update+1,2,process_national_data)

        e_5 = scheduler.enter(time_till_update,2,\
            update_complete,(update_label,))

        scheduler_dict = {'title': update_label,
        'content': 'Update covid data in ' + \
            str(time_till_update) + ' seconds',
        'time': str(hhmm_to_seconds(update_time)),
        'events' : [e_1,e_2,e_3,e_4],
        'updating':'data'}

        if repeat_checkbox:
            repeat_update(scheduler_dict)
            scheduler_dict['content'] = 'Update covid data in ' + \
            str(time_till_update) + ' seconds, repeat every 24 hours'

        if scheduler_dict not in scheduled_updates:
            scheduled_updates.append(scheduler_dict)

        logging.info("Covid data update scheduled")

    elif news_checkbox:

        time_till_update = hhmm_to_seconds(update_time) \
            - hhmm_to_seconds(current_time_hhmm())

        e_1 = scheduler.enter(time_till_update,1,update_news_list)
        e_2 = scheduler.enter(time_till_update,2,\
            update_complete,(update_label,))

        scheduler_dict = {'title': update_label,
        'content': 'Update news in ' + str(time_till_update) + ' seconds',
        'time': str(hhmm_to_seconds(update_time)),
        'events': e_1,
        'updating':'news'}

        if repeat_checkbox:
            repeat_update(scheduler_dict)
            scheduler_dict['content'] = 'Update news in ' + str(time_till_update) + \
            ' seconds, repeats every 24 hours' 

        if scheduler_dict not in scheduled_updates:
            scheduled_updates.append(scheduler_dict)

        logging.info("Covid news update scheduled")

    some_articles = []
    try:
        for index in range(0,4):
            some_articles.append(news_articles_list[index])
    except:
        some_articles = news_articles_list

    with open("config.json", 'r', encoding = 'UTF-8') as my_file:
        data = json.load(my_file)
        title = data["Title"]
        image = data["Image"]

    scheduler.run(blocking=False)
    return render_template("index.html",
    image = image,
    favicon = 'static/images/covid_image_2.png',
    title = title,

    location = "Exeter",
    local_7day_infections = int(local_cases_in_last_week),

    nation_location = "England",
    national_7day_infections = int(cases_in_last_week),

    hospital_cases = "Current Hospital Cases: " + str(current_hospital_cases),
    deaths_total = "Total Deaths: " + str(number_of_deaths),
    news_articles = some_articles,
    updates = scheduled_updates)

@app.route('/')
def home():
    return redirect('/index')

if __name__ == '__main__':
    """Gets initial covid numbers and runs website"""

    try:
        Data = covid_API_request('England', 'nation')
    except:
        logging.error("Couldn't access covid API")
    cases_in_last_week, current_hospital_cases, number_of_deaths = \
    process_covid_csv_data(parse_csv_data("api_data.csv"))

    try:
        Data = covid_API_request('Exeter', 'ltla')
    except:
        logging.error("Couldn't access covid API")
    local_cases_in_last_week = \
    process_covid_csv_data(parse_csv_data("api_data.csv"))[0]

    try:
        news_articles_list = update_news()
    except:
        logging.error("Couldn't access news API")

    try:
        app.run()
    except:
        logging.error("App module couldn't start")
