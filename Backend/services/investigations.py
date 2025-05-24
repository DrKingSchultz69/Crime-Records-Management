from models import Investigation
from app import db

class InvestigationService:
    @staticmethod
    def create_investigation(data):
        investigation = Investigation(**data)
        db.session.add(investigation)
        db.session.commit()
        return investigation

    @staticmethod
    def get_investigation(investigation_id):
        return Investigation.query.get(investigation_id)

    @staticmethod
    def get_investigations():
        return Investigation.query.all()

    @staticmethod
    def update_investigation(investigation_id, data):
        investigation = Investigation.query.get(investigation_id)
        if not investigation:
            return None
        for key, value in data.items():
            setattr(investigation, key, value)
        db.session.commit()
        return investigation

    @staticmethod
    def delete_investigation(investigation_id):
        investigation = Investigation.query.get(investigation_id)
        if not investigation:
            return False
        db.session.delete(investigation)
        db.session.commit()
        return True 