#!/usr/bin/env python
from datetime import datetime
import os
import time

from stravalib.client import Client
from stravalib.model import Activity

from db import ChallengeSqlDB
from model2 import Run, User

CLIENT_ID = os.environ["STRAVA_CLIENT_ID"]
CLIENT_SECRET = os.environ["STRAVA_CLIENT_SECRET"]
SERVICE_TYPE = os.environ["SERVICE_TYPE"]

MYSQL_HOST = os.environ["MYSQL_HOST"]
MYSQL_USERNAME = os.environ["MYSQL_USERNAME"]
MYSQL_PASSWORD = os.environ["MYSQL_PASSWORD"]
MYSQL_DB_NAME = os.environ["MYSQL_DB_NAME"]

ACT_START_DATE = os.getenv("ACT_START_DATE", '2019-10-01T17:00:00Z')
ACT_END_DATE = os.getenv("ACT_END_DATE", '2020-01-12T17:00:00Z')

CHALLENGE_START_DATE = datetime.strptime(ACT_START_DATE, "%Y-%m-%dT%H:%M:%SZ")
CHALLENGE_END_DATE = datetime.strptime(ACT_END_DATE, "%Y-%m-%dT%H:%M:%SZ")

def main():
    ChallengeSqlDB.init(MYSQL_HOST, MYSQL_USERNAME,
                        MYSQL_PASSWORD, MYSQL_DB_NAME)
    print("Challenge start date:", CHALLENGE_START_DATE)
    print("Challenge end date:", CHALLENGE_END_DATE)
    # Read all runners that have intania from DB
    print("Get all runners from db")

    if SERVICE_TYPE.lower() == 'ranger' :
        print("Service type: %s" % ('RANGER'))
        users = ChallengeSqlDB.get_all_ranger_users()
    else:
        print("Service type: %s" % ('INTANIA'))
        users = ChallengeSqlDB.get_all_intania_users()
    n_user = len(users)
    print("Total runners: %d" % (n_user))
    # For each runners get their activities
    runs = []
    for idx, user in enumerate(users):
        # if user.clubs is None or not user.clubs:
        #     print("Skip runner with None intania: id=%s displayname='%s %s'" %
        #           (user.strava_id, user.first_name, user.last_name))
        #     continue
        if not user.credentials:
            print("Skip runner with empty credentials: id=%s displayname='%s %s'" %
                  (user.strava_id, user.first_name, user.last_name))
            continue

        user_cred = None
        refresh_token = None
        strava_user_code = None
        for cred in user.credentials:
            if cred.strava_client == CLIENT_ID:
                user_cred = cred
                refresh_token = cred.strava_refresh
        if refresh_token is None:
            print("Skip runner with empty credentials for client_id=%s : id=%s displayname='%s %s'" %
                  (CLIENT_ID, user.strava_id, user.first_name, user.last_name))
            continue
        else:
            strava_user_code = cred.strava_code
    
        print('Found refresh_token for the user ...')
        
        try:
            client = Client()
            code_response = client.exchange_code_for_token(
                client_id=CLIENT_ID, 
                client_secret=CLIENT_SECRET, 
                code=strava_user_code
            )

            current_time = time.time()
            if code_response['expires_at'] > current_time:
                # Token does not expire
                client.access_token = code_response['access_token']
                if code_response['refresh_token'] != user_cred.strava_token:
                    # Refresh token is changed
                    ChallengeSqlDB.update_credentail_token(
                        CLIENT_ID,
                        code_response['access_token'],  
                        code_response['refresh_token'], 
                        cred.strava_code)
                    
            else:
                print('Token expired, refresh a token...')
                # Get new access token
                refresh_response = client.refresh_access_token(
                    client_id=CLIENT_ID, 
                    client_secret=CLIENT_SECRET, 
                    refresh_token=code_response['refresh_token'])
                # Set up user's access token and ready to fetch Strava data
                client.access_token = refresh_response['access_token']

        except Exception as e:
            print(e)
            continue

        if user.clubs:
            intania = user.clubs[0].intania
        else:
            intania = 0

        if user.registration and user.registration.foundation:
            ranger_team = user.registration.foundation.name
        else:
            ranger_team = None

        time.sleep(0.25)
        activities = client.get_activities(
            after=CHALLENGE_START_DATE, before=CHALLENGE_END_DATE)
        print("Get activities: idx=%d/%d id=%s displayname='%s %s' intania='%s' ranger='%s'" %
              (idx + 1, n_user, user.strava_id, user.first_name, user.last_name, intania, ranger_team))
        n_run = 0

        try:
            for act in activities:
                if act.type not in [Activity.RUN, Activity.WALK]:
                    continue
                n_run += 1
                run = Run.from_activity(act, user.id)
                # Try to save activity to DB
                try:
                    if ChallengeSqlDB.get_run_by_strava_id(run.strava_id) is None:
                        # New run activity
                        ChallengeSqlDB.insert_run(run)
                except Exception as e:
                    ChallengeSqlDB.insert_run(run)

            runs.append(run)
        except Exception as e:
            print(e)
        print('Got run acitivities: %d' % (n_run))
    print("Total run activities: %d" % (len(runs)))


if __name__ == '__main__':
    main()