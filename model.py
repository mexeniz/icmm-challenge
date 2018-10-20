import datetime

class Run():
    def __init__(self, name, athlete_firstname, athlete_lastname, intania, distance, moving_time, elapsed_time, total_elevation_gain, _id=None, virt_id=None, created_at=None):
        self._id = _id
        self.name = name
        self.athlete_firstname = athlete_firstname
        self.athlete_lastname = athlete_lastname 
        self.intania = str(intania)
        self.distance = distance              # metres - float
        self.moving_time = moving_time        # seconds
        self.elapsed_time = elapsed_time      # seconds
        self.total_elevation_gain = total_elevation_gain              # metres - float
        if not virt_id:
            self.virt_id = "%d_%d_%d_%d" % (int(distance * 10), moving_time, elapsed_time, int(total_elevation_gain * 10))
        else:
            self.virt_id = virt_id
        
        if not created_at:
            self.created_at = datetime.datetime.now()
        else:
            self.created_at = created_at
    
    def to_doc(self):
        doc = {
            "virtId": self.virt_id,
            "name": self.name,
            "athleteFirstname": self.athlete_firstname,
            "athleteLastname": self.athlete_lastname,
            "intania": self.intania,
            "distance": self.distance,
            "movingTime": self.moving_time,
            "elapsedTime": self.elapsed_time,
            "totalElevationGain": self.total_elevation_gain,
            "createdAt" : self.created_at
        }
        return doc
    
    @classmethod
    def from_doc(cls, run_doc):
        name = run_doc["name"]
        athlete_firstname = run_doc["athleteFirstname"]
        athlete_lastname = run_doc["athleteLastname"]
        intania = run_doc["intania"]
        distance = run_doc["distance"]
        moving_time = run_doc["movingTime"]
        elapsed_time = run_doc["elapsedTime"]
        total_elevation_gain = run_doc["totalElevationGain"]
        _id = run_doc["_id"]
        virt_id = run_doc["virtId"]
        created_at = run_doc["createdAt"]
        return cls(name, athlete_firstname, athlete_lastname, intania, distance, moving_time, elapsed_time, total_elevation_gain, _id, virt_id, created_at)

class Runner():
    def __init__(self, firstname, lastname, intania, _id=None, created_at=None):
        self._id = _id
        self.firstname = firstname
        self.lastname = lastname
        self.intania = intania
        
        if not created_at:
            self.created_at = datetime.datetime.now()
        else:
            self.created_at = created_at
    
    def to_doc(self):
        doc = {
            "firstname": self.firstname,
            "lastname": self.lastname,
            "intania": self.intania,
            "createdAt" : self.created_at
        }
        return doc

    @classmethod
    def from_doc(cls, runner_doc):
        firstname = runner_doc["firstname"]
        lastname = runner_doc["lastname"]
        intania = runner_doc["intania"]
        _id = runner_doc["_id"]
        created_at = runner_doc["createdAt"]
        return cls(firstname, lastname, intania, _id, created_at)