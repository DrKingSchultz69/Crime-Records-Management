from models import Report
from app import db

class ReportService:
    @staticmethod
    def create_report(data):
        report = Report(**data)
        db.session.add(report)
        db.session.commit()
        return report

    @staticmethod
    def get_report(report_id):
        return Report.query.get(report_id)

    @staticmethod
    def get_reports():
        return Report.query.all()

    @staticmethod
    def update_report(report_id, data):
        report = Report.query.get(report_id)
        if not report:
            return None
        for key, value in data.items():
            setattr(report, key, value)
        db.session.commit()
        return report

    @staticmethod
    def delete_report(report_id):
        report = Report.query.get(report_id)
        if not report:
            return False
        db.session.delete(report)
        db.session.commit()
        return True 