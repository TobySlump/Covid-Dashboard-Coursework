from covid_data_handler import parse_csv_data
from covid_data_handler import process_covid_csv_data
from covid_data_handler import covid_API_request
from covid_data_handler import schedule_covid_updates
from covid_data_handler import scheduler
import sched


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

def test_covid_API_request():
    data = covid_API_request()
    assert isinstance(data, dict)

def test_schedule_update():
    e_1, e_2 = schedule_covid_updates(update_interval = 5, update_name = "update test")
    assert isinstance(e_1, sched.Event)
    assert isinstance(e_2, sched.Event)
    scheduler.run()
    #can see covid API requests in log file
