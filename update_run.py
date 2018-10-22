#!/usr/bin/env python
import os
import datetime
from stravalib.client import Client
from stravalib.model import Activity
from db import ChallengeDB
from model import Run, Runner

CLIENT_ID = os.environ["STRAVA_CLIENT_ID"]
CLIENT_SECRET = os.environ["STRAVA_CLIENT_SECRET"]

MONGODB_URI = os.environ["MONGODB_URI"]
DATABASE_NAME = os.environ["DATABASE_NAME"]

CHALLENGE_START_DATE = datetime.datetime(2018, 10, 18, 17, 0)
CHALLENGE_END_DATE = datetime.datetime(2019, 1, 11, 17, 0)

def main():
    ChallengeDB.init(MONGODB_URI, DATABASE_NAME)
    # Read all runners that have intania from DB
    print("Get all runners from db")
    runners = ChallengeDB.find_runner()
    n_runner = len(runners)
    print("Total runners: %d" % (n_runner))
    # For each runners get their activities
    runs = []
    for idx, runner in enumerate(runners):
        if runner.intania is None:
            print("Skip runner with None intania: id=%s displayname='%s'" % (runner.id, runner.displayname))
            continue
        client = Client(access_token=runner.access_token)
        activities = client.get_activities(after=CHALLENGE_START_DATE, before=CHALLENGE_END_DATE)
        print("Get activities: idx=%d/%d id=%s displayname='%s' intania:'%s'" % (idx, n_runner-1, runner.id, runner.displayname, runner.intania))
        for act in activities:
            if act.type != Activity.RUN:
                continue
            run = Run.from_activity(act, runner.intania)
            # Try to save activity to DB
            if ChallengeDB.find_one_run({"_id":run.id}) is None:
                # New run activity
                ChallengeDB.insert_run(run)
            runs.append(run)
    print("Total run activities: %d" % (len(runs)))

if __name__ == '__main__':
    main()
