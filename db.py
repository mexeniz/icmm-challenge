import sqlalchemy as db
from sqlalchemy import Column, DateTime, Date, String, Integer, BigInteger, Float, Boolean, ForeignKey, func
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import create_engine, MetaData, Table, func
from sqlalchemy.orm import sessionmaker

import mysql.connector
from pymongo import MongoClient

from model import Run, Runner

# Model for SqlDB
Base = declarative_base()
        
class IntaniaClub(Base):
    __tablename__ = 'intania_clubs'
    id = Column(BigInteger, primary_key=True)
    strava_id = Column(String)
    intania = Column(BigInteger)
    name = Column(String)
    clubs = relationship('User',
                        secondary='user_clubs',
                        uselist=True)
    
class User(Base):
    __tablename__ = 'users'
    id = Column(BigInteger, primary_key=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    deleted_at = Column(DateTime)
    first_name = Column(String)
    last_name = Column(String)
    strava_id = Column(String)
    credentials = relationship('Credential',
                        lazy='joined')
    registration_id = Column(BigInteger, ForeignKey("registrations.id"))
#     registation = relationship('Registration')
    clubs = relationship(IntaniaClub,
                        secondary='user_clubs',
                        uselist=True,
                        lazy='joined')

class UserClub(Base):
    __tablename__ = 'user_clubs'
    user_id = Column(BigInteger, ForeignKey('users.id'), primary_key=True)
    club_id = Column(BigInteger, ForeignKey('intania_clubs.id'), primary_key=True)
    
class Credential(Base):
    __tablename__ = 'credentials'
    id = Column(BigInteger)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    deleted_at = Column(DateTime)
    user_id = Column(BigInteger, ForeignKey("users.id"))
    strava_client = Column(String, primary_key=True)
    strava_token = Column(String, primary_key=True)
    strava_code = Column(String)
    
class Registration(Base):
    __tablename__ = 'registrations'
    id = Column(BigInteger, primary_key=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    deleted_at = Column(DateTime)
    first_name = Column(String)
    last_name = Column(String)
    gender = Column(String)
    phone_number = Column(String)
    race_type = Column(String)
    race_category = Column(String)
    foundation_id =  Column(BigInteger, ForeignKey('foundations.id'))
    foundation = relationship('Foundation')
    registration_id = Column(String, unique=True)
    
class Foundation(Base):
    __tablename__ = 'foundations'
    id = Column(BigInteger, primary_key=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    deleted_at = Column(DateTime)
    name = Column(String)
    
class Activity(Base):
    __tablename__ = 'activities'
    id = Column(BigInteger, primary_key=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.utc_timestamp())
    deleted_at = Column(DateTime)
    user_id = Column(BigInteger, ForeignKey("users.id"))
    strava_id = Column(String, unique=True)
    name = Column(String)
    start_date = Column(DateTime)
    start_date_local = Column(DateTime)
    distance = Column(BigInteger)
    moving_time = Column(BigInteger)
    elapsed_time = Column(BigInteger)
    elev_high = Column(Float)
    elev_low = Column(Float)
    total_elevation_gain = Column(Float)
    manual = Column(Boolean)
    promo_comment = Column(String)
    promo_multiplier = Column(Float)

# SQL Database Connector
# ICMM Intania Challenge & F5 Challenge 2020

class ChallengeSqlDB():
    DB_ENGINE = None
    SESSION = None

    @classmethod
    def init(cls, mysql_host, mysql_username, mysql_password, mysql_db_name):
        connection_str = 'mysql://{}:{}@{}/{}?charset=utf8mb4'.format(mysql_username, mysql_password, mysql_host, mysql_db_name)
        cls.DB_ENGINE = create_engine(connection_str)
        
        cls.SESSION = sessionmaker()
        cls.SESSION.configure(bind=cls.DB_ENGINE)
        Base.metadata.create_all(cls.DB_ENGINE)
        connection = cls.DB_ENGINE.connect()
        print("Initialized database connection: host={}".format(mysql_host))

    ###########
    # Club
    ###########
    @classmethod
    def get_all_intania_clubs(cls):
        sess = cls.SESSION()
        rows = sess.query(IntaniaClub).all()
        return rows

    ###########
    # USER
    ###########
    @classmethod
    def get_all_users(cls):
        sess = cls.SESSION()
        rows = sess.query(User).all()
        return rows

    @classmethod
    def get_all_intania_users(cls):
        sess = cls.SESSION()
        rows = sess.query(User).filter(User.clubs).all()
        return rows

    @classmethod
    def get_all_foundation_users(cls):
        sess = cls.SESSION()
        rows = sess.query(User).filter(User.registration).all()
        return rows
    
    @classmethod
    def update_user_intania(cls, user_id, club_id):
        sess = cls.SESSION()
        user_club = UserClub(user_id=user_id, club_id=club_id)
        sess.add(user_club)
        sess.commit()
    
    @classmethod
    def update_user_name(cls, user_id, first_name, last_name):
        sess = cls.SESSION()
        sess.query(User).filter(User.id == user_id).update(
            {
                'first_name': first_name,
                'last_name': last_name
            })
        sess.commit()

    ###########
    # RUN
    ###########
    @classmethod
    def get_run_by_strava_id(cls, strava_id):
        sess = cls.SESSION()
        row = sess.query(Activity).filter(Activity.strava_id == strava_id).one()
        return row

    @staticmethod
    def __run_to_activity(run):
        return Activity(
            strava_id=run.strava_id,
            user_id=run.user_id,
            name=run.name,
            start_date=run.start_date,
            start_date_local=run.start_date_local,
            distance=run.distance,
            moving_time=run.moving_time,
            elapsed_time=run.elapsed_time,
            elev_high=run.elev_high,
            elev_low=run.elev_low,
            total_elevation_gain=run.total_elevation_gain,
            manual=run.manual
        )

    @classmethod
    def insert_run(cls, run):
        sess = cls.SESSION()
        actvity = cls.__run_to_activity(run)
        sess.add(actvity)
        sess.commit()
    

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
