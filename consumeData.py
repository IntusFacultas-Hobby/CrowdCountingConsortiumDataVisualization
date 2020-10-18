import csv
import sys
# import django
# os.environ["DJANGO_SETTINGS_MODULE"] = 'protestdata.settings'
# django.setup()

file_name = sys.argv[1]
year = sys.argv[2]

print(f"Consuming: {sys.argv[1]} {sys.argv[2]}")


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


with open(f'{sys.argv[2]}/{sys.argv[1]}.csv', 'r') as fin, open(f'{sys.argv[2]}Filtered/{sys.argv[1]}.csv', 'w') as fout:
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
