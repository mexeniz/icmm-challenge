from stravalib.client import Client
from stravalib.model import Activity
import csv

AUTH_DATA_PATH = "./data/auth_data.csv"
CLUB_DATA_PATH = "./data/intania_clubs.csv"

CLIENT_ID = ""
CLIENT_SECRET = ""

MONGODB_URI = ""
DATABASE_NAME = ""


def main():
    auth_dict = {}
    with open(AUTH_DATA_PATH, newline='') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            auth_dict[row["user_id"]] = (row["code"], row["user_displayname"])
            print("Name:",row["user_displayname"], "Code:", row["code"])
    
    csv_path = "./intania_clubs.csv"
    club_dict = {} # Map id -> intania
    with open(CLUB_DATA_PATH, newline='') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            print("Intania:", row["intania"], "ID:", row["club_id"])
            club_dict[row["club_id"]] = row["intania"]

if __name__ == '__main__':
    main()