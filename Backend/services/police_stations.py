from models import PoliceStation
from app import db

class PoliceStationService:
    @staticmethod
    def create_police_station(data):
        police_station = PoliceStation(**data)
        db.session.add(police_station)
        db.session.commit()
        return police_station

    @staticmethod
    def get_police_station(station_id):
        return PoliceStation.query.get(station_id)

    @staticmethod
    def get_police_stations():
        return PoliceStation.query.all()

    @staticmethod
    def update_police_station(station_id, data):
        police_station = PoliceStation.query.get(station_id)
        if not police_station:
            return None
        for key, value in data.items():
            setattr(police_station, key, value)
        db.session.commit()
        return police_station

    @staticmethod
    def delete_police_station(station_id):
        police_station = PoliceStation.query.get(station_id)
        if not police_station:
            return False
        db.session.delete(police_station)
        db.session.commit()
        return True 