from models import Complaint
from app import db

class ComplaintService:
    @staticmethod
    def create_complaint(data):
        complaint = Complaint(**data)
        db.session.add(complaint)
        db.session.commit()
        return complaint

    @staticmethod
    def get_complaint(complaint_id):
        return Complaint.query.get(complaint_id)

    @staticmethod
    def get_complaints():
        return Complaint.query.all()

    @staticmethod
    def update_complaint(complaint_id, data):
        complaint = Complaint.query.get(complaint_id)
        if not complaint:
            return None
        for key, value in data.items():
            setattr(complaint, key, value)
        db.session.commit()
        return complaint

    @staticmethod
    def delete_complaint(complaint_id):
        complaint = Complaint.query.get(complaint_id)
        if not complaint:
            return False
        db.session.delete(complaint)
        db.session.commit()
        return True 