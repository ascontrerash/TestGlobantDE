from db import db

class JobModel(db.Model):
    __tablename__ = 'jobs'
    
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    job = db.Column(db.String, nullable=False)
    hired_employees = db.relationship('HiredEmployeeModel', back_populates='job', lazy='dynamic')