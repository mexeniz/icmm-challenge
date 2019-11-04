#!/usr/bin/env python
import argparse
import csv
import datetime
import os
import pytz

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from stravalib.client import Client
from stravalib.model import Activity

from db import ChallengeSqlDB
from model2 import Run, User

DEFAULT_SCOPE = ["https://spreadsheets.google.com/feeds",
                 "https://www.googleapis.com/auth/drive"]


class ChallengeSpread():

    def __init__(self, credentials_path):
        self.credentials = ServiceAccountCredentials.from_json_keyfile_name(
            credentials_path, DEFAULT_SCOPE)
        self.gc = gspread.authorize(self.credentials)

    def __get_sheet(self, spread_key, sheet_name):
        spread_sheet = self.gc.open_by_key(spread_key)
        return spread_sheet.worksheet(sheet_name)

    def update_summary_run(self, spread_key, sheet_name, run_data):
        print("Updating run spreadsheet: %s" % (sheet_name))
        # element in run_data : [intania, distance]
        worksheet = self.__get_sheet(spread_key, sheet_name)

        cell_list = worksheet.range("A2:E%d" % (len(run_data) + 1))
        for idx, cell in enumerate(cell_list):
            i = int(idx / 5)
            j = idx % 5
            if j == 0:
                print(run_data[i])
                # Insert row number
                element = i + 1
            else:
                element = run_data[i][j - 1]
            cell.value = element

        # Update in batch
        worksheet.update_cells(cell_list, "USER_ENTERED")

    def update_runner(self, spread_key, sheet_name, runner_data):
        print("Updating runner spreadsheet: %s" % (sheet_name))
        # element in runner_data : [no., displayname, intania]
        worksheet = self.__get_sheet(spread_key, sheet_name)

        cell_list = worksheet.range("A2:D%d" % (len(runner_data)))
        for idx, cell in enumerate(cell_list):
            i = int(idx / 4)
            j = idx % 4
            if j == 0:
                # Insert row number
                element = i + 1
            else:
                element = runner_data[i][j - 1]
            cell.value = element

        # Update in batch
        worksheet.update_cells(cell_list, "USER_ENTERED")


# Reuired environment
TIME_STRING_FORMAT = "%Y-%m-%d %H:%M:%S"

DEFAULT_OUTPUT_DIR = "./"

MYSQL_HOST = os.environ["MYSQL_HOST"]
MYSQL_USERNAME = os.environ["MYSQL_USERNAME"]
MYSQL_PASSWORD = os.environ["MYSQL_PASSWORD"]
MYSQL_DB_NAME = os.environ["MYSQL_DB_NAME"]

ChallengeSqlDB.init(MYSQL_HOST, MYSQL_USERNAME,
                    MYSQL_PASSWORD, MYSQL_DB_NAME)


def update_runner_spread_intania(challenge_spread, spread_key, sheet_name):
    users = ChallengeSqlDB.get_all_intania_users()
    runner_data = []
    for user in users:
        if user.clubs:
            intania = user.clubs[0].intania
        else:
            intania = "N/A"
        runner_data.append((user.first_name, user.last_name, intania))

    challenge_spread.update_runner(spread_key, sheet_name, runner_data)


def update_run_spread_intania(challenge_spread, spread_key, sheet_name):
    rows = ChallengeSqlDB.get_summary_intania_distance()
    run_data = []
    for row in rows:
        # row.total_distance type is Decimal
        run_data.append(
            (row.intania, int(row.total_distance) / 1000.0, row.total_user, row.total_run)
        )
    
    challenge_spread.update_summary_run(spread_key, sheet_name, run_data)


def update_run_spread_ranger(challenge_spread, spread_key, sheet_name):
    rows = ChallengeSqlDB.get_summary_ranger_distance()
    run_data = []
    for row in rows:
        # row.total_distance type is Decimal
        run_data.append(
            (row.name, int(row.total_distance)/ 1000.0, row.total_user, row.total_run)
        )
    challenge_spread.update_summary_run(spread_key, sheet_name, run_data)


def upload_reports(drive_cleint_config, token_path, folder_id, report_paths):
    g_auth = GoogleAuth()
    g_auth.LoadClientConfigFile(drive_cleint_config)
    g_auth.LoadCredentialsFile(token_path)
    drive = GoogleDrive(g_auth)

    for report_path in report_paths:
        with open(report_path, "r") as file:
            title = os.path.basename(file.name)
            file_drive = drive.CreateFile({
                "title": title,
                "parents": [{"kind": "drive#fileLink", "id": folder_id}]
            })
            file_drive.SetContentString(file.read())
            file_drive.Upload()
            print("Upload file: %s" % (title))


def gen_run_report(timestamp, report_path):
    runs = ChallengeSqlDB.get_all_runs()
    with open(report_path, "w", newline="") as csvfile:
        fieldnames = ["timestamp",
                      "start_date",
                      "start_date_local",
                      "strava_id",
                      "name",
                      "distance",
                      "moving_time",
                      "elapsed_time",
                      "elev_high",
                      "elev_low",
                      "total_elevation_gain",
                      "manual",
                      "promo_comment",
                      "promo_multiplier",
                      "user_strava_id",
                      "user_first_name",
                      "user_last_name",
                      "user_intania",
                      "user_ranger",
                      "created_at"
                      ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        n_run = 0
        for run in runs:
            row = vars(run)
            row["timestamp"] = timestamp
            row["start_date"] = row["start_date"].strftime(TIME_STRING_FORMAT)
            row["start_date_local"] = row["start_date_local"].strftime(
                TIME_STRING_FORMAT)
            row["created_at"] = row["created_at"].strftime(TIME_STRING_FORMAT)

            # Customise user info
            user = run.user
            row["user_strava_id"] = user.strava_id
            row["user_first_name"] = user.first_name
            row["user_last_name"] = user.last_name
            if user.clubs:
                row["user_intania"] = user.clubs[0].intania
            else:
                row["user_intania"] = ""

            if user.registration and user.registration.foundation:
                row["user_ranger"] = user.registration.foundation.name
            else:
                row["user_ranger"] = ""

            # Filter only wanted fields
            row = {key: row[key] for key in fieldnames if key in row}
            writer.writerow(row)

            n_run += 1

    print("Total Runs:", n_run)
    print("Generated report to", report_path)


def gen_runner_report(timestamp, report_path):
    users = ChallengeSqlDB.get_all_users()
    with open(report_path, "w", newline="") as csvfile:
        fieldnames = ["timestamp", "id",  "strava_id", "first_name",
                      "last_name", "intania", "ranger", "created_at"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        n_user = 0
        for user in users:
            row = vars(user)
            row["timestamp"] = timestamp
            row["created_at"] = row["created_at"].strftime(TIME_STRING_FORMAT)

            # Customise intania and ranger fields
            if user.clubs:
                row["intania"] = user.clubs[0].intania
            else:
                row["intania"] = ""

            if user.registration and user.registration.foundation:
                row["ranger"] = user.registration.foundation.name
            else:
                row["ranger"] = ""

            # Filter only wanted fields
            row = {key: row[key] for key in fieldnames if key in row}
            writer.writerow(row)

            n_user += 1

    print("Total Runners:", n_user)
    print("Generated report to", report_path)


def main():
    if args.time_zone:
        tz = pytz.timezone(args.time_zone)
        now = datetime.datetime.now(tz)
    else:
        now = datetime.datetime.now()

    timestamp = now.strftime(TIME_STRING_FORMAT)
    report_prefix = now.strftime("%Y%m%d_%H%M%S")
    print("Report timestamp:", timestamp)

    output_dir = args.output_dir
    os.makedirs(output_dir, exist_ok=True)
    runner_report_name = "%s_runner_report.csv" % (report_prefix)
    run_report_name = "%s_run_report.csv" % (report_prefix)

    runner_report_path = os.path.join(output_dir, runner_report_name)
    gen_runner_report(timestamp, runner_report_path)
    run_report_path = os.path.join(output_dir, run_report_name)
    gen_run_report(timestamp, run_report_path)

    if args.drive_cleint_config and args.drive_token and args.drive_folder_id:
        print("GDrive config is set, uploading reports to Gdrive.")
        upload_reports(args.drive_cleint_config, args.drive_token,
                       args.drive_folder_id, [runner_report_path, run_report_path])

    if args.credentials:
        print("GSpread credentials is set, uploading summary to spreadsheet.")
        challenge_spread = ChallengeSpread(args.credentials)

        if args.run_spread_key and args.intania_run_sheet_name:
            update_run_spread_intania(
                challenge_spread,
                args.run_spread_key,
                args.intania_run_sheet_name
            )

        if args.run_spread_key and args.ranger_run_sheet_name:
            update_run_spread_ranger(
                challenge_spread,
                args.run_spread_key,
                args.ranger_run_sheet_name
            )

        if args.runner_spread_key and args.intania_runner_sheet_name:
            update_runner_spread_intania(
                challenge_spread,
                args.runner_spread_key,
                args.intania_runner_sheet_name
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", help="Output directory for reports", action="store",
                        default=DEFAULT_OUTPUT_DIR, dest="output_dir", type=str)
    parser.add_argument("--time-zone", help="Timezone for timestamp", action="store",
                        default=None, dest="time_zone", type=str)
    parser.add_argument("--drive-client-config", help="GDrive client config file", action="store",
                        dest="drive_cleint_config", type=str)
    parser.add_argument("--drive-token", help="GDrive access token file", action="store",
                        dest="drive_token", type=str)
    parser.add_argument("--drive-folder-id", help="Destination folder id on GDrive", action="store",
                        dest="drive_folder_id", type=str)
    # Spreadsheet config
    parser.add_argument("--credentials", help="GSpread credentials", action="store",
                        dest="credentials", type=str)
    parser.add_argument("--run-spread-key", help="Spreadsheet key for intania & ranger run summary", action="store",
                        dest="run_spread_key", type=str)
    parser.add_argument("--intania-run-sheet-name", help="Worksheet name for intania run summary", action="store",
                        dest="intania_run_sheet_name", type=str)
    parser.add_argument("--ranger-run-sheet-name", help="Worksheet name for ranger run summary", action="store",
                        dest="ranger_run_sheet_name", type=str)

    parser.add_argument("--runner-spread-key", help="Spreadsheet key for runner summary", action="store",
                        dest="runner_spread_key", type=str)
    parser.add_argument("--intania-runner-sheet-name", help="Worksheet name for runner summary", action="store",
                        dest="intania_runner_sheet_name", type=str)
    args = parser.parse_args()
    main()
