#!/usr/bin/env python
import os
import csv
import datetime
import argparse
from stravalib.client import Client
from stravalib.model import Activity
from db import ChallengeDB
from model import Run, Runner

# Reuired environment
MONGODB_URI = os.environ["MONGODB_URI"]
DATABASE_NAME = os.environ["DATABASE_NAME"]

DEFAULT_OUTPUT_DIR = "./"

STRING_TIME_FORMAT = "%Y-%b-%d %H:%M:%S"

now = datetime.datetime.now()
timestamp = now.strftime(STRING_TIME_FORMAT)
report_prefix = now.strftime("%Y%m%d_%H%M%S")
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
            row["startDate"] = row["startDate"].strftime(STRING_TIME_FORMAT)
            row["startDateLocal"] = row["startDateLocal"].strftime(STRING_TIME_FORMAT)
            row["createdAt"] = row["createdAt"].strftime(STRING_TIME_FORMAT)
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
            row["createdAt"] = row["createdAt"].strftime(STRING_TIME_FORMAT)
            row = {key:row[key] for key in fieldnames}
            writer.writerow(row)
    print("Total Runners:", len(runners))
    print("Generated report to", report_path)

def main():
    output_dir = args.output_dir
    os.makedirs(output_dir, exist_ok=True)
    runner_report_name = "%s_runner_report.csv" % (report_prefix)
    run_report_name = "%s_run_report.csv" % (report_prefix)

    runner_report_path = os.path.join(output_dir, runner_report_name)
    gen_runner_report(runner_report_path)
    run_report_path = os.path.join(output_dir, run_report_name)
    gen_run_report(run_report_path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", help="Output directory for reports", action="store",
                        default=DEFAULT_OUTPUT_DIR, dest="output_dir", type=str)
    args = parser.parse_args()
    main()