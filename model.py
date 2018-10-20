import datetime

class Run():
    def __init__(self, id, name, start_date, start_date_local, athlete_id, intania, distance, moving_time, elapsed_time, elev_high, elev_low, total_elevation_gain, object_id=None, created_at=None):
        self.id = id
        self.object_id = object_id
        self.start_date = start_date
        self.start_date_local = start_date_local
        self.name = name
        self.athlete_id = athlete_id
        self.intania = intania
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
    
    def to_doc(self):
        doc = {
            "id": self.id,
            "_id": self._id,
            "name": self.name,
            "athleteId": self.athlete_id,
            "startDate": self.start_date,
            "startDateLocal": self.start_date_local,
            "intania": self.intania,
            "distance": self.distance,
            "movingTime": self.moving_time,
            "elapsedTime": self.elapsed_time,
            "elevHigh": self.elev_high,
            "elevLow": self.elev_low,
            "totalElevationGain": self.total_elevation_gain,
            "createdAt" : self.created_at
        }
        return doc
    
    @classmethod
    def from_doc(cls, run_doc):
        name = run_doc["name"]
        athlete_id = run_doc["athleteId"]
        intania = run_doc["intania"]
        startDate = run_doc["startDate"]
        start_date_local = run_doc["startDateLocal"]
        distance = run_doc["distance"]
        moving_time = run_doc["movingTime"]
        elapsed_time = run_doc["elapsedTime"]
        created_at = run_doc["createdAt"]
        elev_high = run_doc["elevHigh"]
        elev_low = run_doc["elevLow"]
        total_elevation_gain = run_doc["totalElevationGain"]
        object_id = run_doc["_id"]
        created_at = run_doc["createdAt"]
        return cls(id, name, start_date, start_date_local, athlete_id, intania, distance, moving_time, elapsed_time, elev_high, elev_low, total_elevation_gain, object_id, created_at)
    
    @classmethod
    def from_activity(cls, act, intania):
        name = act.name
        id = str(act.id)
        athlete_id = str(act.athlete.id)
        intania = str(intania)
        start_date = act.start_date
        start_date_local = act.start_date_local
        distance = float(act.distance)
        moving_time = int(act.moving_time.seconds)
        elapsed_time = int(act.elapsed_time.seconds)
        elev_high = float(act.elev_high) if act.elev_high is not None else 0.0
        elev_low = float(act.elev_low) if act.elev_low is not None else 0.0
        total_elevation_gain = float(act.total_elevation_gain) if act.total_elevation_gain is not None else 0.0
        return cls(id, name, start_date, start_date_local, athlete_id, intania, distance, moving_time, elapsed_time, elev_high, elev_low, total_elevation_gain)
        

class Runner():
    def __init__(self, id, displayname, intania, code, access_token, created_at=None):
        self.id = id
        self.displayname = displayname
        self.intania = intania
        self.code = code
        self.access_token = access_token
        
        if not created_at:
            self.created_at = datetime.datetime.now()
        else:
            self.created_at = created_at
    
    def to_doc(self):
        doc = {
            "_id": self.id,
            "displayname": self.displayname,
            "intania": self.intania,
            "code": self.code,
            "accessToken": self.access_token,
            "createdAt" : self.created_at
        }
        return doc

    @classmethod
    def from_doc(cls, runner_doc):
        id = runner_doc["_id"]
        displayname = runner_doc["displayname"]
        intania = runner_doc["intania"]
        code = runner_doc["code"]
        access_token = runner_doc["accessToken"]
        created_at = runner_doc["createdAt"]
        return cls(id, displayname, intania, code, access_token, created_at)