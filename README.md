# Protest Data

This is intended to consume the protest data found at https://sites.google.com/view/crowdcountingconsortium/view-download-the-data?authuser=0
and filter for US-based BLM/anti-police brutality related protests, then display data visualization graphs and provide basic filtering.

**Note:** This is not representative of my normal style of coding or attention to detail. This was a quick bodge project.

## Setup

It's highly recommended you use `virtualenv`. If you aren't familiar with this technology, please refer to the documentation here:
https://virtualenv.pypa.io/en/latest/

### Requirements:

- Sqlite==3.x
- Python==3.6.x
- pip==20.2.4
- django==3.1.2
- django-webpack-loader==0.6.0
- djangorestframework==3.12.1
- django-environ>=0.4.5

### Steps

Perform the following steps in the console of your choice. I used Bash.

1. Activate your virtualenv if you're using one.
2. Change env.example to `.env`, **change the secret key**, then source your .env by entering the command `source .env`
3. Run `pip install -r requirements.txt`
4. Run `python manage.py migrate`
5. Run `python manage.py stagedata --start 2019 --end 2020`
6. In another command window, `cd` into the `public` directory, and run `npm install`
7. In the same command window, run `npm run serve` from the `public` directory
8. In the original command window, run `python manage.py runserver`
9. Open a browser and visit localhost:8000

## Data Ingest Instructions

This project can handle any set of years of data, assuming the data follows the following format:

The CSV must have the headers in the following order:

- CityTown
- Location
- County
- StateTerritory
- Country
- Date
- EstimateText
- EstimateLow
- BestGuess
- EstimateHigh
- AdjustedLow
- AdjustedHigh
- Actor
- Claim
- Pro(2)/Anti(1)
- EventType
- ReportedArrests
- ReportedParticipantInjuries
- ReportedPoliceInjuries
- ReportedPropertyDamage
- TownsCities
- Events
- Source1
- Source2
- Source3
- Misc.

And the CSV files must be in the root directory of the project, by year, named by month. Ergo

```
public/...
core/...
protestdata/...
2018/
    January.csv
    February.csv
    March.csv
```

At which point, you can run `python manage.py stagedata --start 2018 --end 2020` with the years updated to match
the timeframe you wish to injest.

**What to do if you experience an error**: Since the dataset is manually entered, sometimes we find some odd
numbers showing up in numerical columns. If you experience an error similar to:

```
django\db\models\fields\__init__.py", line 1774, in get_prep_value
    return int(value)
ValueError: invalid literal for int() with base 10: 'see above'
```

You'll need to go into `core/management/commands/stagedata.py`, `line 60` and add the offending data to the blacklist.

## Usage

This tool will allow you to filter the consumed data points by almost any available field, as well as filter out
results that have blank (ergo no data) fields as need be.

The graphing function will produce a graph based on the current filters you have inputed (keep in mind that blank
values can screw up the graph, so you'll probably want to filter those out if your graphs aren't working as expected.
I could fix this if I wasn't just bodging this together, but its 2:30 AM and I'm tired.)
