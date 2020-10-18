from django.core.management.base import BaseCommand, CommandError
from core.models import DataPoint
import csv
import os
import datetime


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

        blacklist = ["N/A", "", "unknown number", "numerous", "see above"]
        if value is not None and value not in blacklist:
            return value
        return None

    def filterData(self, month: str, year: int):
        print(f"Consuming: {month} {year}")

        def check_claim(value):
            valid_claims = [
                "CIVIL RIGHTS", "BLACKLIVESMATTER",
                "BLACK LIVES MATTER", "POLICE BRUTALITY",
                "POLICE VIOLENCE", "BREONNA TAYLOR",
                "GEORGE FLOYD", "JUSTICE"
            ]
            for claim in valid_claims:
                if claim in value:
                    return True
            return False
        if not os.path.isdir("./Filtered"):
            os.mkdir("./Filtered")
        if not os.path.isdir(f"./Filtered/{year}"):
            os.mkdir(f"./Filtered/{year}")
        with open(f'{year}/{month}.csv', 'r') as fin, open(f'Filtered/{year}/{month}.csv', 'w', newline="") as fout:
            valid_countries = ["US", "USA"]
            COUNTRY_CLAIM = 4
            CLAIM_COLUMN = 13
            writer = csv.writer(fout, delimiter=",")
            row_count = 0
            for row in csv.reader(fin):
                if row_count == 0:
                    row_count += 1
                    continue
                if row[COUNTRY_CLAIM].upper() in valid_countries and check_claim(row[CLAIM_COLUMN].upper()):
                    writer.writerow(row)

        print("Done")

    def handle(self, *args, **options):

        # clobbering database
        print("Clobbering old database")
        DataPoint.objects.all().delete()

        # columns
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
        start_year = options["start"][0]
        end_year = options["end"][0]
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
