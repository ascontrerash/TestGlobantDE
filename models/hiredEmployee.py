from db import db

class HiredEmployeeModel(db.Model):
    __tablename__ = 'hired_employees'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    datetime = db.Column(db.String)
    department_id = db.Column(db.Integer, db.ForeignKey('deparments.id'), unique=False, nullable=False)
    department = db.relationship('DepartmentModel', back_populates='hired_employees')
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), unique=False, nullable=False)
    job = db.relationship('JobModel', back_populates='hired_employees')