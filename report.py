#!/usr/bin/env python
import os
import csv
import datetime
from stravalib.client import Client
from stravalib.model import Activity
from db import ChallengeDB
from model import Run, Runner

# Reuired environment
MONGODB_URI = os.environ["MONGODB_URI"]
DATABASE_NAME = os.environ["DATABASE_NAME"]

now = datetime.datetime.now()
timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
report_postfix = now.strftime("%Y%m%d_%H%M%S")
print("Report timestamp:", timestamp)

ChallengeDB.init(MONGODB_URI, DATABASE_NAME)


runs = ChallengeDB.find_run()

def gen_run_report(report_path):
    runs = ChallengeDB.find_run()
    with open(report_path, 'w', newline='') as csvfile:
        fieldnames = ["timestamp"] + list(runs[0].to_doc().keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for run in runs:
            row = run.to_doc()
            row["timestamp"] = timestamp
            writer.writerow(row)
    print("Total Runs:", len(runs))
    print("Generated report to", report_path)

def gen_runner_report(report_path):
    runners = ChallengeDB.find_runner()
    with open(report_path, 'w', newline='') as csvfile:
        fieldnames = ["timestamp","_id", "displayname", "intania", "createdAt"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for runner in runners:
            row = runner.to_doc()
            row["timestamp"] = timestamp
            row = {key:row[key] for key in fieldnames}
            writer.writerow(row)
    print("Total Runners:", len(runners))
    print("Generated report to", report_path)

def main():
    runner_report_path = "runner_report_%s.csv" % (report_postfix)
    run_report_path = "run_report_%s.csv" % (report_postfix)
    gen_runner_report(runner_report_path)
    gen_run_report(run_report_path)

if __name__ == '__main__':
    main()