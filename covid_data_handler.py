"""This module contains the functionality for the user interface"""

import sched
import time
from uk_covid19 import Cov19API
import logging

scheduler = sched.scheduler(time.time, time.sleep)
FORMAT= '%(levelname)s: %(asctime)s %(message)s'
logging.basicConfig(filename='log.log',format = FORMAT, level=logging.DEBUG)

def parse_csv_data(csv_filename: str) -> list:
    """opens file named in csv_filename"""

    with open(csv_filename, 'r', encoding = 'UTF-8') as my_file:
        data = my_file.readlines()
        logging.info('Opened covid csv file')

    for index,element in enumerate(data):
        data[index] = element.replace("\n","")

    return data

def process_covid_csv_data(covid_csv_data: list) -> int:
    """returns the cases in the last week,
    the current hospital cases and number of deaths"""

    line_count = 0
    cases_in_last_week = 0
    current_hospital_cases = 0
    number_of_deaths = 0
    cases_starting_index = 0

    have_found_cases_last_week = False
    found_number_of_deaths = False

    for line in covid_csv_data:

        elements_in_line = line.split(",")
        try:
            elements_in_line[5]
        except IndexError:
            break

        try:
            if line_count > 0 and elements_in_line[5] != "" \
                and have_found_cases_last_week is False:
                current_hospital_cases = elements_in_line[5]
                have_found_cases_last_week = True
        except IndexError:
            print("no hospital cases found")

        try:
            if line_count > 1 and elements_in_line[6] != "":
                if cases_starting_index == 0:
                    cases_starting_index = line_count

                elif cases_starting_index + 7 >= line_count :
                    cases_in_last_week += int(elements_in_line[6])
                    #print(elements_in_line[6])
        except IndexError:
            print("no cases found")

        try:
            if line_count > 0 and elements_in_line[4] != "" \
                and found_number_of_deaths is False:
                number_of_deaths = elements_in_line[4]
                found_number_of_deaths = True
        except IndexError:
            print("no deaths found")

        line_count += 1

    return cases_in_last_week, \
        int(current_hospital_cases), int(number_of_deaths)

def covid_API_request(location = 'Exeter', location_type = 'ltla') -> list:
    """retrieves the covid data from the API"""

    logging.info("Covid data API request")

    location_filter = [
    'areaType='+location_type,
    'areaName='+location]

    cases_and_deaths = {
    "areaCode": "areaCode",
    "areaName": "areaName",
    "areaType": "areaType",
    "date": "date",

    "cumDailyNsoDeathsByDeathDate": "cumDailyNsoDeathsByDeathDate",
    "hospitalCases": "hospitalCases",
    "newCasesBySpecimenDate": "newCasesBySpecimenDate"}

    api = Cov19API(filters=location_filter, structure=cases_and_deaths)
    data = api.get_json()

    #print(api.last_update)
    #print(time.gmtime())

    api.get_csv(save_as="api_data.csv")

    return data

def schedule_covid_updates(update_interval: int, update_name = "") \
    -> sched.Event:
    """schedules updates for the csv file"""

    e_1 = scheduler.enter(update_interval,1,covid_API_request)

    e_2 = scheduler.enter(update_interval+1,1,\
        covid_API_request,('England','nation',))

    return e_1,e_2

def test_process_covid_csv_data ():
    """checks that the data is processed to the right values"""
    last7days_cases , current_hospital_cases , total_deaths \
        = process_covid_csv_data ( parse_csv_data ("nation_21-10-28.csv"))
    assert last7days_cases == 240299
    assert current_hospital_cases == 7019
    assert total_deaths == 141544

def test_parse_csv_data ():
    """checks if file is right length"""
    data = parse_csv_data ("nation_21-10-28.csv")
    assert len ( data ) == 639

Data = covid_API_request('Exeter', 'ltla')
a,b,c = process_covid_csv_data(parse_csv_data("api_data.csv"))

test_process_covid_csv_data()
