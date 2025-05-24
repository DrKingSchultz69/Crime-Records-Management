from models import Location
from app import db

class LocationService:
    @staticmethod
    def create_location(data):
        location = Location(**data)
        db.session.add(location)
        db.session.commit()
        return location

    @staticmethod
    def get_location(location_id):
        return Location.query.get(location_id)

    @staticmethod
    def get_locations():
        return Location.query.all()

    @staticmethod
    def update_location(location_id, data):
        location = Location.query.get(location_id)
        if not location:
            return None
        for key, value in data.items():
            setattr(location, key, value)
        db.session.commit()
        return location

    @staticmethod
    def delete_location(location_id):
        location = Location.query.get(location_id)
        if not location:
            return False
        db.session.delete(location)
        db.session.commit()
        return True 