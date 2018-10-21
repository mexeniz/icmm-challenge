#!/usr/bin/env python
from stravalib.client import Client
from stravalib.model import Activity
import csv
import argparse
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

DEFAULT_USER_CSV_PATH = "data/auth_data.csv"
DEFAULT_CLUB_CSV_PATH = "data/intania_clubs.csv"

def main():

    # Load user auth from csv
    code_dict = {}
    with open(args.auth_data, newline='') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            code_dict[row["user_id"]] = (row["code"], row["user_displayname"], row["token"])
            
    users = []
    for user_id, tup in code_dict.items():
        code = tup[0]
        user_displayname = tup[1]
        token = tup[2]
        user = Runner(user_id, user_displayname, None, code, token)
        print("ID:", user_id, "Name:", user_displayname)
        users.append(user)

    # Load club id from csv
    club_dict = {} # Map id -> intania
    with open(args.club_data, newline='') as csv_file:
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


        if user.id in mongo_users_dict:
            # User is in DB
            if user.intania:
                # Found intania for user
                print(user.displayname, "Intania %s" % (user.intania))
                ChallengeDB.update_one_runner_intania(user)
            else:
                print(user.displayname, "not found intania, skip...")
        else:
            # New authenticated user
            # Save to MongoDb
            ChallengeDB.insert_runner(user)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--auth-data", help="Auth data csv", action="store",
                        default=DEFAULT_USER_CSV_PATH, dest="auth_data", type=str)
    parser.add_argument("--club-data", help="Intania club data csv", action="store",
                        default=DEFAULT_CLUB_CSV_PATH, dest="club_data", type=str)
    args = parser.parse_args()
    main()

