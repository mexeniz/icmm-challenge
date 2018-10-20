from stravalib.client import Client
from stravalib.model import Activity
import csv
import datetime
from pymongo import MongoClient
import datetime
from db import ChallengeDB
from model import Runner
import os

CLIENT_ID = os.environ["STRAVA_CLIENT_ID"]
CLIENT_SECRET = os.environ["STRAVA_CLIENT_SECRET"]

MONGODB_URI = os.environ["MONGODB_URI"]
DATABASE_NAME = os.environ["DATABASE_NAME"]

user_csv_path = "data/auth_data.csv"
club_csv_path = "data/intania_clubs.csv"

# Load user auth from csv
code_dict = {}
with open(user_csv_path, newline='') as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
        code_dict[row["user_id"]] = (row["code"], row["user_displayname"])
        
users = []
for user_id, tup in code_dict.items():
    access_token = Client().exchange_code_for_token(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, code=tup[0])
    user_displayname = tup[1]
    user = Runner(user_id, user_displayname, None, tup[0], access_token)
    print("ID:", user_id, "Name:", user_displayname)
    users.append(user)

# Load club id from csv
club_dict = {} # Map id -> intania
with open(club_csv_path, newline='') as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
        print("Intania:", row["intania"], "ID:", row["club_id"])
        club_dict[row["club_id"]] = row["intania"]

# Get all users from MongoDb
ChallengeDB.init(MONGODB_URI, DATABASE_NAME)
mongo_users = ChallengeDB.find_runner()
mongo_users_dict = {}
for user in mongo_users:
    mongo_users_dict[user.id] = user

# Find intania for
for user in users:
	
    # User already has basic data in the database
    if user.id in mongo_users_dict and mongo_users_dict[user.id].intania and mongo_users_dict[user.id].intania != "":
        print(user.displayname, "already completed, skip...")
        continue

    client = Client(access_token=user.access_token)
    athlete = client.get_athlete()
    joined_clubs = athlete.clubs
    for club in joined_clubs:
#         print("id:", club.id, "Club name:", club.name)
        club_id = str(club.id)
        if club_id in club_dict:
            user.intania = club_dict[club_id]
            break

    if user.intania:
        print(user.displayname, "Intania %s" % (user.intania))
    else:
        print(user.displayname, "not found intania, skip...")

    # Save to MongoDb
    ChallengeDB.insert_runner(user)

