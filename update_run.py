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

def main():
    ChallengeDB.init(MONGODB_URI, DATABASE_NAME)
    # 1. Read all runners that have intania from DB
    print("Get all runners from db")
    runners = ChallengeDB.find_runner()
    print("Total runners: %d" % (len(runners)))
    # 2. Each runners get their activities
    runs = []
    for runner in runners:
        if runner.intania is None:
            print("Skip runner with None intania: id=%s name='%s %s'" % (runner.id, runner.firstname, runner.lastname))
            continue
        client = Client(access_token=runner.access_token)
        activities = client.get_activities(after=CHALLENGE_START_DATE)
        for act in activities:
            if act.type != Activity.RUN:
                continue
            run = Run.from_activity(act, runner.intania)
            runs.append(run)
    # 3. Convert activities that are RUN to Run object
    print("Total run activities: %d" % (len(runs)))
    # 4. Insert runs to database
    for run in runs:
        if ChallengeDB.find_one_run({"id":run.id}) is None:
            # New run activity
            print("Found new activity: id=%s athlete_id=%s intania=%s" % (run.id, run.athlete_id, run.intania))
            ChallengeDB.insert_run(run)

if __name__ == '__main__':
    main()