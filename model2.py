import datetime


class Run():

    def __init__(self, id, strava_id, user_id, name,  start_date, start_date_local, distance, moving_time, elapsed_time, elev_high, elev_low, total_elevation_gain, created_at=None):
        self.id = id  # Incremental ID
        self.strava_id = id
        self.user_id = user_id
        self.name = name
        self.start_date = start_date
        self.start_date_local = start_date_local
        self.distance = distance              # metres - float
        self.moving_time = moving_time        # seconds
        self.elapsed_time = elapsed_time      # seconds
        self.elev_high = elev_high
        self.elev_low = elev_low
        self.total_elevation_gain = total_elevation_gain

        if not created_at:
            self.created_at = datetime.datetime.now()
        else:
            self.created_at = created_at

    def to_row(self):
        row = (
            self.id,
            self.strava_id,
            self.user_id,
            self.name,
            self.start_date,
            self.start_date_local,
            self.distance,
            self.moving_time,
            self.elapsed_time,
            self.elev_high,
            self.elev_low,
            self.total_elevation_gain,
            self.created_at
        )
        return row

    @classmethod
    def from_row(cls, run_row):
        id = run_row[0]
        strava_id = run_row[1]
        user_id = run_row[2]
        name = run_row[3]
        start_date = run_row[5]
        start_date_local = run_row[6]
        distance = run_row[7]
        moving_time = run_row[8]
        elapsed_time = run_row[9]
        created_at = run_row[10]
        elev_high = run_row[11]
        elev_low = run_row[12]
        total_elevation_gain = run_row[13]
        created_at = run_row[14]
        return cls(id, strava_id, user_id, name, start_date, start_date_local, distance, moving_time, elapsed_time, elev_high, elev_low, total_elevation_gain, created_at)

    @classmethod
    def from_activity(cls, act, user_id):
        """ 
        Create an Activity object by Strava API activity. 
        """
        id = None
        strava_id = str(act.id)
        name = act.name
        start_date = act.start_date
        start_date_local = act.start_date_local
        distance = float(act.distance)
        moving_time = int(act.moving_time.seconds +
                          (act.moving_time.days * 86400))
        elapsed_time = int(act.elapsed_time.seconds +
                           (act.elapsed_time.days * 86400))
        elev_high = float(act.elev_high) if act.elev_high is not None else 0.0
        elev_low = float(act.elev_low) if act.elev_low is not None else 0.0
        total_elevation_gain = float(
            act.total_elevation_gain) if act.total_elevation_gain is not None else 0.0
        return cls(id, strava_id, user_id, name, athlete_id, start_date, start_date_local, distance, moving_time, elapsed_time, elev_high, elev_low, total_elevation_gain)


class User():
    def __init__(self, id, reg_info_id, strava_id,  first_name, last_name, strava_code, strava_token, created_at=None, intania=None, foundation=None):
        self.id = id
        self.reg_info_id = reg_info_id
        self.strava_id = strava_id
        self.first_name = first_name
        self.last_name = last_name
        self.strava_code = strava_code
        self.strava_token = strava_token

        if not created_at:
            self.created_at = datetime.datetime.now()
        else:
            self.created_at = created_at

        # From joining table
        self.intania = foundation
        self.foundation = foundation

    def to_row(self):
        row = (
            self.id,
            self.reg_info_id,
            self.strava_id,
            self.first_name,
            self.last_name,
            self.strava_code,
            self.strava_token,
            self.created_at,
            self.intania,
            self.foundation
        )
        return row

    @classmethod
    def from_row(cls, user_row):
        id = user_row[0]
        reg_info_id = user_row[0],
        strava_id = user_row[1]
        first_name = user_row[2]
        last_name = user_row[3]
        strava_code = user_row[4]
        strava_token = user_row[5]
        created_at = user_row[6]

        intania = user_row[7]
        foundation = user_row[8]
        return cls(id, reg_info_id, strava_id, first_name, last_name, strava_code, strava_token, created_at, intania, foundation)

class Club():
    def __init__(self, id, strava_id,  name, intaniaม created_at):
        self.id = id
        self.strava_id = strava_id
        self.name = name
        self.intania = intania

        if not created_at:
            self.created_at = datetime.datetime.now()
        else:
            self.created_at = created_at

    def to_row(self):
        row = (
            self.id,
            self.strava_id,
            self.name,
            self.intania
        )
        return row

    @classmethod
    def from_row(cls, club_row):
        id = club_row[0]
        strava_id = club_row[1]
        name = club_row[2]
        intania = club_row[3]
        return cls(id, strava_id, name, intania)
