Introduction:
The 'user_interface.py' module contains the backend to the website created in the 'index.html' file. It uses functionality
from 'covid_data_handler.py' and 'covid_news_handling.py' to display current covid statistics and headlines containing covid
keywords.

Running:
Run the 'user_interface.py' module to start the web application, the website will then be hosted at http://127.0.0.1:5000/
Once on the website, updates to the covid data and news articles can be scheduled for any chosen time.
While running, a 'log.log' file will be created or amended if already created, this log file will track events occurring 
whilst the application is open.

Configuration:
The 'config.json' file contains data that can be easily changed by the user. It contains the following

API Key - Used to access the news API, the user should register for their own key and use that
Title - The title displayed on the Dashboard
Image - The image displayed with the title
Default_Location - If no location is specified this is the location that will be shown
Default_Location_Type - If no location type is specified this will be used 

Testing:
There are 3 testing files that test that functions return the right values or atleast the right data types if the
value cannot be predicted beforehand. These test fucntions can be run from the command prompt.

Links:
GitHub repository - https://github.com/TobySlump/Covid-Dashboard-Coursework
Covid API link - https://publichealthengland.github.io/coronavirus-dashboard-api-python-sdk/
News API link - https://newsapi.org/

These modules were written by Toby Slump, University of Exeter