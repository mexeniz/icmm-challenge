#!/usr/bin/env python
import argparse
import csv
import datetime
import os

from stravalib.client import Client
from stravalib.model import Activity

from db import ChallengeSqlDB
from model2 import User


CLIENT_ID = os.environ["STRAVA_CLIENT_ID"]
CLIENT_SECRET = os.environ["STRAVA_CLIENT_SECRET"]

MYSQL_HOST = os.environ["MYSQL_HOST"]
MYSQL_USERNAME = os.environ["MYSQL_USERNAME"]
MYSQL_PASSWORD = os.environ["MYSQL_PASSWORD"]
MYSQL_DB_NAME = os.environ["MYSQL_DB_NAME"]

def main():
    ChallengeSqlDB.init(MYSQL_HOST, MYSQL_USERNAME,
                        MYSQL_PASSWORD, MYSQL_DB_NAME)

    print("Get all runners from db")
    users = ChallengeSqlDB.get_all_users()

    # Load club id from csv
    intania_clubs = ChallengeSqlDB.get_all_intania_clubs()
    # Map strava_id -> club.id
    intania_clubs_dict = {}
    for intania_club in intania_clubs:
        intania_clubs_dict[intania_club.strava_id] = intania_club

    # Find intania for
    for user in users:
        # User already has basic data in the database
        print("User: strava_id=%s displayname='%s %s'" % 
            (user.strava_id, user.first_name, user.last_name))
        access_token = user.credentials[0].strava_token
        client = Client(access_token=access_token)
        athlete = client.get_athlete()
        joined_clubs = athlete.clubs

        if not (user.clubs is None or not user.clubs):
            print("%s %s is in '%s' club, skip club update..." % 
                (user.first_name, user.last_name, user.clubs[0].name))
        else:
            for club in joined_clubs:
        #         print("id:", club.id, "Club name:", club.name)
                club_strava_id = str(club.id)
                if club_strava_id in intania_clubs_dict :
                    # update in database
                    intania_club = intania_clubs_dict[club_strava_id]
                    print('Update intania club (%s) for %s %s' % (intania_club.name, user.first_name, user.last_name))
                    ChallengeSqlDB.update_user_intania(user.id, intania_club.id)

        # Update first & last name
        try:
            ChallengeSqlDB.update_user_name(user.id, athlete.firstname, athlete.lastname)
        except Exception as e:
            print('Failed to update user entity: id=%d displayname=%s %s' % 
                (user.id, athlete.firstname, athlete.lastname))
            print(e)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    main()

