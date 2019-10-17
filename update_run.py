#!/usr/bin/env python
import datetime
import os
import time

from stravalib.client import Client
from stravalib.model import Activity

from db import ChallengeSqlDB
from model2 import Run, User

CLIENT_ID = os.environ["STRAVA_CLIENT_ID"]
CLIENT_SECRET = os.environ["STRAVA_CLIENT_SECRET"]

MYSQL_HOST = os.environ["MYSQL_HOST"]
MYSQL_USERNAME = os.environ["MYSQL_USERNAME"]
MYSQL_PASSWORD = os.environ["MYSQL_PASSWORD"]
MYSQL_DB_NAME = os.environ["MYSQL_DB_NAME"]

CHALLENGE_START_DATE = datetime.datetime(2019, 10, 1, 17, 0)
CHALLENGE_END_DATE = datetime.datetime(2019, 10, 31, 17, 0)


def main():
    ChallengeSqlDB.init(MYSQL_HOST, MYSQL_USERNAME,
                        MYSQL_PASSWORD, MYSQL_DB_NAME)
    # Read all runners that have intania from DB
    print("Get all runners from db")
    users = ChallengeSqlDB.get_all_users()
    n_user = len(users)
    print("Total runners: %d" % (n_user))
    # For each runners get their activities
    runs = []
    for idx, user in enumerate(users):
        if user.clubs is None or not user.clubs:
            print("Skip runner with None intania: id=%s displayname='%s %s'" %
                  (user.strava_id, user.first_name, user.last_name))
            continue
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
        
        intania = user.clubs[0].intania
        time.sleep(0.2)
        activities = client.get_activities(
            after=CHALLENGE_START_DATE, before=CHALLENGE_END_DATE)
        print("Get activities: idx=%d/%d id=%s displayname='%s %s' intania:'%d'" %
              (idx, n_user - 1, user.strava_id, user.first_name, user.last_name, intania))
        n_run = 0
        for act in activities:
            if act.type != Activity.RUN:
                continue
            n_run += 1
            run = Run.from_activity(act, user.id)
            # Try to save activity to DB
            try:
                if ChallengeSqlDB.get_run_by_strava_id(run.strava_id) is None:
                    # New run activity
                    ChallengeSqlDB.insert_run(run)
            except Exception as e:
                # print('Inserting %s' % (run.name.decode('latine-').encode('utf8')))
                ChallengeSqlDB.insert_run(run)

            runs.append(run)
        print('Got run acitivities: %d' % (n_run))
    print("Total run activities: %d" % (len(runs)))


if __name__ == '__main__':
    main()
