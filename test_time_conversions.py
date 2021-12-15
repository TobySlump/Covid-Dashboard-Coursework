from time_conversions import hhmm_to_seconds
from time_conversions import current_time_hhmm

def test_hhmm_to_seconds():
    seconds = hhmm_to_seconds("2:30")
    assert seconds == 150*60

def test_current_time():
    seconds = current_time_hhmm()
    assert isinstance(seconds, str)
