import mysql.connector
from pymongo import MongoClient

from model import Run, Runner

# SQL Database Connector
# ICMM Intania Challenge & F5 Challenge 2020

class SqlQueryGenerator():

    @classmethod
    def intania_runner_summary():
        pass
    
    @classmethod
    def intania_run_summary():
        pass

    @classmethod
    def foundation_runner_summary():
        pass
    
    @classmethod
    def foundation_run_summary():
        pass

class ChallengeSqlDB():
    DB = None

    @classmethod
    def init(cls, mysql_host, mysql_username, mysql_password):
        cls.DB = mysql.connector.connect(
            host=mysql_host,
            user=mysql_username,
            passwd=mysql_password
        )
        print("Initialized database connection")

    @classmethod
    def query(query_str):
        pass

    ###########
    # Club
    ###########
    # get_all_clubs

    ###########
    # USER
    ###########

    # get_all_users
    # get_all_intania_users
    # get_all_foundation_users
    # update_user_intania

    ###########
    # RUN
    ###########
    # get_run_by_strava_id
    # insert_run(replace=False)
    

# MongoDB Connector
class ChallengeDB():
    MONGO_CLIENT = None
    DB = None

    @classmethod
    def init(cls, mongodb_uri, database_name):
        cls.MONGO_CLIENT = MongoClient(mongodb_uri)
        cls.DB = eval("cls.MONGO_CLIENT.%s" % (database_name))
        print("Initialized database connection")

    ###########
    # RUN
    ###########
    @classmethod
    def find_one_run(cls, query={}):
        run_doc = cls.DB.challenge_runs.find_one(query)
        if run_doc:
            return Run.from_doc(run_doc)
        else:
            return None

    @classmethod
    def find_run(cls, query={}):
        run_cursor = cls.DB.challenge_runs.find(query)
        return [Run.from_doc(run_doc) for run_doc in run_cursor]

    @classmethod
    def find_run_by_id(cls, id):
        run_cursor = cls.DB.challenge_runs.find({"id": id})
        return [Run.from_doc(run_doc) for run_doc in run_cursor]

    @classmethod
    def find_run_by_intania(cls, intania):
        run_cursor = cls.DB.challenge_runs.find({"intania": intania})
        return [Run.from_doc(run_doc) for run_doc in run_cursor]

    @classmethod
    def find_summary_intania_distance(cls, intania_range=range(50, 100)):
        pipe = [{
                "$group": {
                    "_id": "$intania",
                    "distance": {
                        "$sum": {"$divide": ["$distance", 1000.0]}
                    }
                }
                },
                {"$sort": {"_id": 1}}
                ]
        cursor = ChallengeDB.DB.challenge_runs.aggregate(pipeline=pipe)
        summary = {str(intania): 0 for intania in intania_range}
        for doc in cursor:
            intania = doc["_id"]
            summary[intania] = doc["distance"]
        return [[intania, distance] for intania, distance in summary.items()]

    @classmethod
    def insert_run(cls, run):
        assert type(run) == Run
        print("Insert Run: id=%s distance=%.2f intania=%s name=%s" %
              (run.id, run.distance, run.intania, run.name))
        # Get result _id by inserted_id attribute
        return cls.DB.challenge_runs.insert_one(run.to_doc())

    @classmethod
    def update_one_run(cls, query, run, upsert=False):
        return cls.DB.challenge_runs.update_one(query, {"$set": run.to_doc()}, upsert=upsert)

    ###########
    # RUNNER
    ###########
    @classmethod
    def find_one_runner(cls, query={}):
        runner_doc = cls.DB.challenge_runners.find_one(query)
        return Runner.from_doc(runner_doc)

    @classmethod
    def find_runner(cls, query={}):
        runner_cursor = cls.DB.challenge_runners.find(query)
        return [Runner.from_doc(runner_doc) for runner_doc in runner_cursor]

    @classmethod
    def find_runner_by_intania(cls, intania):
        runner_cursor = cls.find_runner({"intania": intania})
        return [Runner.from_doc(runner_doc) for runner_doc in runner_cursor]

    @classmethod
    def insert_runner(cls, runner):
        assert type(runner) == Runner
        print("Insert Runner: id=%s displayname=%s intania=%s" %
              (runner.id, runner.displayname, runner.intania))
        return cls.DB.challenge_runners.insert_one(runner.to_doc())

    @classmethod
    def update_one_runner(cls, runner, updated_keys=None):
        assert type(runner) == Runner
        runner_doc = runner.to_doc()
        if updated_keys:
            runner_doc = {key: runner_doc[key] for key in keys}
        else:
            # Update all keys except "_id"
            runner_doc.pop("_id", None)
        print("Update Runner: id=%s displayname=%s intania=%s" %
              (runner.id, runner.displayname, runner.intania))
        return cls.DB.challenge_runners.update_one(
            {"_id": runner.id},
            {
                "$set": runner_doc
            }
        )

    @classmethod
    def update_one_runner_intania(cls, runner):
        assert type(runner) == Runner
        print("Update Runner's Intania: id=%s displayname=%s intania=%s" %
              (runner.id, runner.displayname, runner.intania))
        return cls.DB.challenge_runners.update_one(
            {"_id": runner.id},
            {
                "$set": {"intania": runner.intania}
            }
        )

    @classmethod
    def find_summary_runner(cls):
        field_filter = {"_id": 0, "displayname": 1, "intania": 1}
        sort_list = [("intania", 1), ("displayname", 1)]
        cursor = cls.DB.challenge_runners.find(
            {}, field_filter).sort(sort_list)
        summary_runners = []
        for idx, runner in enumerate(cursor):
            if runner["intania"] is not None:
                summary_runners.append(
                    [idx + 1, runner["displayname"], runner["intania"]])
            else:
                summary_runners.append([idx + 1, runner["displayname"], ""])

        return summary_runners
