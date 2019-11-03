#!/usr/bin/env python
import argparse
import os

from stravalib.client import Client
from stravalib.model import Activity

from db import ChallengeSqlDB
from model2 import User

import time

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
        
        if not user.credentials:
            print("Skip runner with empty credentials: id=%s displayname='%s %s'" %
                  (user.strava_id, user.first_name, user.last_name))
            continue
        
        refresh_token = None
        for cred in user.credentials:
            if cred.strava_client == CLIENT_ID:
                refresh_token = cred.strava_refresh
        if refresh_token is None:
            print("Skip runner with empty credentials for client_id=%s : id=%s displayname='%s %s'" %
                  (CLIENT_ID, user.strava_id, user.first_name, user.last_name))
            continue
        
        print('Found refresh_token for the user ...')

        client = Client()
        # Get new access token
        refresh_response = client.refresh_access_token(
            client_id=CLIENT_ID, 
            client_secret=CLIENT_SECRET, 
            refresh_token=refresh_token)
        # Set up user's access token and ready to fetch Strava data
        client.access_token = refresh_response['access_token']

        # stravalib.exc.RateLimitExceeded
        try:
            athlete = client.get_athlete()
        except Exception as e:
            print('Error: failed to fetch Strava profile')
            print(e)
            continue
        joined_clubs = athlete.clubs

        if not (user.clubs is None or not user.clubs):
            print("%s %s is in '%s' club, skip club update..." % 
                (user.first_name, user.last_name, user.clubs[0].name))
        elif joined_clubs is None:
            print("Error: failed to fetch clubs for %s %s, skip club update..." % 
                (user.first_name, user.last_name))
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
            print('Error: failed to update user entity: id=%d displayname=%s %s' % 
                (user.id, athlete.firstname, athlete.lastname))
            print(e)

        time.sleep(0.2)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    main()

