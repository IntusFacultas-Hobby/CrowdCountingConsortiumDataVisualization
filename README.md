# Protest Data

This is intended to consume the protest data found at https://sites.google.com/view/crowdcountingconsortium/view-download-the-data?authuser=0
and filter for US-based BLM/anti-police brutality related protests, then display data visualization graphs and provide basic filtering.

## Setup

It's highly recommended you use `virtualenv`. If you aren't familiar with this technology, please refer to the documentation here:
https://virtualenv.pypa.io/en/latest/

### Requirements:

Python==3.6.X
pip==20.2.4
django==3.1.2
django-webpack-loader==0.6.0
djangorestframework==3.12.1
django-environ>=0.4.5

### Steps

Perform the following steps in the console of your choice. I used Bash.

**Note:** If you want to update the data available, simple add folders by year, with .csv files with appropriate names
(ergo: January, February, March, etc.)

1. Activate your virtualenv if you're using one.
2. Change env.example to `.env`, **change the secret key**, then source your .env by entering the command `source .env`
3. Run `pip install -r requirements.txt`
4. Run `python manage.py migrate`
