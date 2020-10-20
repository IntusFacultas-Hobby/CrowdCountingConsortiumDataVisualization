from django.core.management.base import BaseCommand, CommandError
from difflib import SequenceMatcher
from core.models import DataPoint
import csv
import os
import datetime


class BadDataFormat(Exception):
    pass


CITY = 0
LOCATION = 1
COUNTY = 2
STATE = 3
DATE = 5
ESTIMATE_LOW = 7
ESTIMATE_BEST = 8
ESTIMATE_HIGH = 9
ADJUSTED_LOW = 10
ADJUSTED_HIGH = 11
ACTOR = 12
CLAIM = 13
EVENT_TYPE = 15
REPORTED_ARREST = 16
REPORTED_PARTICIPANT_INJURIES = 17
REPORTED_POLICE_INJURIES = 18
REPORTED_PROPERTY_DAMAGE = 19
SOURCE_1 = 22
SOURCE_2 = 23
SOURCE_3 = 24

CUT_OFF = .85


class Command(BaseCommand):
    help = 'Stages available data found in folders. Defaults to data for 2019 and 2020'

    def add_arguments(self, parser):
        parser.add_argument('--start', nargs=1, type=int, default=2019)
        parser.add_argument('--end', nargs=1, type=int, default=2020)

    def parse_date(self, date: str):
        # seriously, changing date formats in the middle is just annoying.

        try:
            # most dates are in MM/DD/YYYY format
            return datetime.datetime.strptime(date, "%m/%d/%Y").strftime("%Y-%m-%d")
        except ValueError:
            # except some are in "YYYY-MM-DD" format cuz of course
            try:
                return datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m-%d")
            except ValueError as e:
                # at this point who knows.
                raise e

    def sanitize_values(self, value: str):
        # sometimes when they lack data they leave it blank. Sometimes they input N/A.
        # Sometimes they input unknown number. sometimes they input numerous. Who knows at this point

        #
        blacklist = ["N/A", "", "unknown number",
                     "numerous", "see above", "a few", "unknown",
                     'unclear', "several", "unspecified", "few", "some",
                     "a number", 'more than a dozen', '']
        value = value.strip()
        if value is not None and value not in blacklist:
            return value
        return None

    def filterData(self, month: str, year: int):
        print(f"Consuming: {month} {year}")

        def check_claim(value):
            valid_claims = [
                "CIVIL RIGHTS", "BLACKLIVESMATTER",
                "BLACK LIVES MATTER", "POLICE BRUTALITY", "AGAINST POLICE BRUTALITY",
                "POLICE VIOLENCE", "AGAINST POLICE VIOLENCE", "BREONNA TAYLOR",
                "GEORGE FLOYD", "JUSTICE",
                "ANTIRACISM", "ANTI-RACISM",
                "RACIAL JUSTICE",
                "AGAINST RACISM",
                "DEFUND THE POLICE", "DEFUNDING POLICE",
                "BLACK LIVES LOST", "ABOLISHING THE POLICE",
                "RACIAL PROFILING",
            ]

            for claim in valid_claims:
                if claim in value:
                    return True
            return False

        if not os.path.isdir("./Filtered"):
            os.mkdir("./Filtered")
        if not os.path.isdir(f"./Filtered/{year}"):
            os.mkdir(f"./Filtered/{year}")
        with open(f'{year}/{month}.csv', 'r') as fin, open(f"excludedValues.txt", "w+") as exc, open(f'Filtered/{year}/{month}.csv', 'w', newline="") as fout:
            valid_countries = ["US", "USA"]
            COUNTRY_COLUMN = 4
            CLAIM_COLUMN = 13
            writer = csv.writer(fout, delimiter=",")
            row_count = 0
            for row in csv.reader(fin):
                numToAlpha = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                if row_count == 0:
                    # verify the csv is in the appropriate format
                    if row[CITY] != 'CityTown':
                        DataPoint.objects.all().delete()
                        raise BadDataFormat(
                            f"Column {numToAlpha[CITY]} expected to be 'CityTown' found '{row[CITY]}'. Rolling back data consumption.")
                    if row[LOCATION] != 'Location':
                        DataPoint.objects.all().delete()
                        raise BadDataFormat(
                            f"Column {numToAlpha[LOCATION]} expected to be 'Location' found '{row[LOCATION]}'. Rolling back data consumption.")
                    if row[COUNTY] != 'County':
                        DataPoint.objects.all().delete()
                        raise BadDataFormat(
                            f"Column {numToAlpha[COUNTY]} expected to be 'County' found '{row[COUNTY]}'. Rolling back data consumption.")
                    if row[STATE] != 'StateTerritory':
                        DataPoint.objects.all().delete()
                        raise BadDataFormat(
                            f"Column {numToAlpha[STATE]} expected to be 'StateTerritory' found '{row[STATE]}'. Rolling back data consumption.")
                    if row[DATE] != 'Date':
                        DataPoint.objects.all().delete()
                        raise BadDataFormat(
                            f"Column {numToAlpha[DATE]} expected to be 'Date' found '{row[DATE]}'. Rolling back data consumption.")
                    if row[ESTIMATE_LOW] != 'EstimateLow':
                        DataPoint.objects.all().delete()
                        raise BadDataFormat(
                            f"Column {numToAlpha[ESTIMATE_LOW]} expected to be 'EstimateLow' found '{row[ESTIMATE_LOW]}'. Rolling back data consumption.")
                    if row[ESTIMATE_BEST] != 'BestGuess':
                        DataPoint.objects.all().delete()
                        raise BadDataFormat(
                            f"Column {numToAlpha[ESTIMATE_BEST]} expected to be 'BestGuess' found '{row[ESTIMATE_BEST]}'. Rolling back data consumption.")
                    if row[ESTIMATE_HIGH] != 'EstimateHigh':
                        DataPoint.objects.all().delete()
                        raise BadDataFormat(
                            f"Column {numToAlpha[ESTIMATE_HIGH]} expected to be 'EstimateHigh' found '{row[ESTIMATE_HIGH]}'. Rolling back data consumption.")
                    if row[ADJUSTED_LOW] != 'AdjustedLow':
                        DataPoint.objects.all().delete()
                        raise BadDataFormat(
                            f"Column {numToAlpha[ADJUSTED_LOW]} expected to be 'AdjustedLow' found '{row[ADJUSTED_LOW]}'. Rolling back data consumption.")
                    if row[ADJUSTED_HIGH] != 'AdjustedHigh':
                        DataPoint.objects.all().delete()
                        raise BadDataFormat(
                            f"Column {numToAlpha[ADJUSTED_HIGH]} expected to be 'AdjustedHigh' found '{row[ADJUSTED_HIGH]}'. Rolling back data consumption.")
                    if row[ACTOR] != 'Actor':
                        DataPoint.objects.all().delete()
                        raise BadDataFormat(
                            f"Column {numToAlpha[ACTOR]} expected to be 'Actor' found '{row[ACTOR]}'. Rolling back data consumption.")
                    if row[CLAIM] != 'Claim':
                        DataPoint.objects.all().delete()
                        raise BadDataFormat(
                            f"Column {numToAlpha[CLAIM]} expected to be 'Claim' found '{row[CLAIM]}'. Rolling back data consumption.")
                    if row[EVENT_TYPE] != 'EventType':
                        DataPoint.objects.all().delete()
                        raise BadDataFormat(
                            f"Column {numToAlpha[EVENT_TYPE]} expected to be 'EventType' found '{row[EVENT_TYPE]}'. Rolling back data consumption.")
                    if row[REPORTED_ARREST] != 'ReportedArrests':
                        DataPoint.objects.all().delete()
                        raise BadDataFormat(
                            f"Column {numToAlpha[REPORTED_ARREST]} expected to be 'ReportedArrests' found '{row[REPORTED_ARREST]}'. Rolling back data consumption.")
                    if row[REPORTED_PARTICIPANT_INJURIES] != 'ReportedParticipantInjuries':
                        DataPoint.objects.all().delete()
                        raise BadDataFormat(
                            f"Column {numToAlpha[REPORTED_PARTICIPANT_INJURIES]} expected to be 'ReportedParticipantInjuries' found '{row[REPORTED_PARTICIPANT_INJURIES]}'. Rolling back data consumption.")
                    if row[REPORTED_POLICE_INJURIES] != 'ReportedPoliceInjuries':
                        DataPoint.objects.all().delete()
                        raise BadDataFormat(
                            f"Column {numToAlpha[REPORTED_POLICE_INJURIES]} expected to be 'ReportedPoliceInjuries' found '{row[REPORTED_POLICE_INJURIES]}'. Rolling back data consumption.")
                    if row[REPORTED_PROPERTY_DAMAGE] != 'ReportedPropertyDamage':
                        DataPoint.objects.all().delete()
                        raise BadDataFormat(
                            f"Column {numToAlpha[REPORTED_PROPERTY_DAMAGE]} expected to be 'ReportedPropertyDamage' found '{row[REPORTED_PROPERTY_DAMAGE]}'. Rolling back data consumption.")
                    if row[SOURCE_1] != 'Source1':
                        DataPoint.objects.all().delete()
                        raise BadDataFormat(
                            f"Column {numToAlpha[SOURCE_1]} expected to be 'Source1' found '{row[SOURCE_1]}'. Rolling back data consumption.")
                    if row[SOURCE_2] != 'Source2':
                        DataPoint.objects.all().delete()
                        raise BadDataFormat(
                            f"Column {numToAlpha[SOURCE_2]} expected to be 'Source2' found '{row[SOURCE_2]}'. Rolling back data consumption.")
                    if row[SOURCE_3] != 'Source3':
                        DataPoint.objects.all().delete()
                        raise BadDataFormat(
                            f"Column {numToAlpha[SOURCE_3]} expected to be 'Source3' found '{row[SOURCE_3]}'. Rolling back data consumption.")

                    row_count += 1
                    continue
                valid = check_claim(row[CLAIM_COLUMN].upper())
                if row[COUNTRY_COLUMN].upper() in valid_countries and valid:
                    writer.writerow(row)
                else:
                    exc.write(f"{row[CLAIM_COLUMN]}\n")

        print("Done")

    def handle(self, *args, **options):

        # clobbering database
        print("Clobbering old database")
        DataPoint.objects.all().delete()

        # columns

        # months for iterating
        months = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December"
        ]
        try:
            start_year = options["start"][0]
        except TypeError:
            start_year = 2019
        try:
            end_year = options["end"][0]
        except TypeError:
            end_year = 2020
        for year in range(start_year, end_year + 1):
            for month in months:
                try:
                    self.filterData(month, year)
                except FileNotFoundError as e:
                    print(f"Could not find {year}/{month}.csv. Continuing.")
        for year in os.scandir("./Filtered"):
            for month in os.scandir(year):
                with open(os.path.abspath(month), "r") as fin:
                    for row in csv.reader(fin):
                        dp = DataPoint.objects.create(
                            city=row[CITY],
                            location=row[LOCATION],
                            county=row[COUNTY],
                            state=row[STATE],
                            date=self.parse_date(row[DATE]),
                            estimate_low=self.sanitize_values(
                                row[ESTIMATE_LOW]),
                            estimate_best=self.sanitize_values(
                                row[ESTIMATE_BEST]),
                            estimate_high=self.sanitize_values(
                                row[ESTIMATE_HIGH]),
                            adjusted_low=self.sanitize_values(
                                row[ADJUSTED_LOW]),
                            adjusted_high=self.sanitize_values(
                                row[ADJUSTED_HIGH]),
                            actor=row[ACTOR],
                            claim=row[CLAIM],
                            event_type=row[EVENT_TYPE],
                            reported_arrests=self.sanitize_values(
                                row[REPORTED_ARREST]),
                            reported_participant_injuries=self.sanitize_values(
                                row[REPORTED_PARTICIPANT_INJURIES]),
                            reported_police_injuries=self.sanitize_values(
                                row[REPORTED_POLICE_INJURIES]),
                            reported_property_damage=self.sanitize_values(row[
                                REPORTED_PROPERTY_DAMAGE])
                        )
                        sources = []
                        if row[SOURCE_1]:
                            sources.append(row[SOURCE_1])
                        if row[SOURCE_2]:
                            sources.append(row[SOURCE_2])
                        if row[SOURCE_3]:
                            sources.append(row[SOURCE_3])
                        dp.save_sources(sources)
                        dp.save()
