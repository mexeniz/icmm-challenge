from pymongo import MongoClient
from model import Run, Runner

class ChallengeDB():
    MONGO_CLIENT = None
    DB = None
    
    @classmethod
    def init(cls, mongodb_uri, database_name):
        cls.MONGO_CLIENT = MongoClient(mongodb_uri)
        cls.DB = eval ("cls.MONGO_CLIENT.%s" % (database_name))
        print("Initialized database connection")
    
    ###########
    # RUN
    ###########
    @classmethod
    def find_one_run(cls, query={}):
        run_doc = cls.DB.challenge_runs.find_one(query)
        return Run.from_doc(run_doc)

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
    def insert_run(cls, run):
        assert type(run) == Run
        # Get result _id by inserted_id attribute
        return cls.DB.challenge_runs.insert_one(run.to_doc())
    
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
        return cls.DB.challenge_runners.insert_one(runner.to_doc())