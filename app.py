import os

from flask import Flask, request, render_template, redirect, url_for, flash
from werkzeug.utils import secure_filename
import pandas as pd

from db import db
from models.job import JobModel
from models.hiredEmployee import HiredEmployeeModel
from models.department import DepartmentModel


UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///data.db') # configure later other DBMS
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db.init_app(app)


with app.app_context():
    db.drop_all()
    db.create_all()

# creating a function that verifies the extensions to upload
ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index ():
    return render_template('upload_file.html')



# Creating a route and method to recive and upload the csv

@app.route('/upload', methods=['POST'])
def upload_csv():
    # Saving data in temporary folder
    if 'file' in request.files:
        uploaded_file = request.files['file']
        filename = secure_filename(uploaded_file.filename)
        uploaded_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        csv_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        data = pd.read_csv(csv_file_path)
        
    
    # saving or data in the data base
        if uploaded_file.filename == 'jobs.csv':
            for index, row in data.iterrows():
                nueva_fila = JobModel(
                    id=row[0], 
                    job=row[1])
                db.session.add(nueva_fila)
                
        elif uploaded_file.filename == 'departments.csv':
            for index, row in data.iterrows():
                nueva_fila = DepartmentModel(
                    id=row[0], 
                    department=row[1])
                db.session.add(nueva_fila)
                
        else:
            columns = ['id', 'name', 'datetime', 'department_id', 'job_id']
            
            data = data.fillna(0)
            for index, row in data.iterrows():
                nueva_fila = HiredEmployeeModel(
                    id=row[0], 
                    name=row[1],
                    datetime=row[2],
                    department_id=row[3],
                    job_id=row[4])
                db.session.add(nueva_fila)
        db.session.commit()
        
        return f'uploaded {uploaded_file.filename}'
    return 'CSV file uploaded'
         
        
        
'''  
uploaded_file = request.files['file']
    if uploaded_file.filename == 'jobs.csv':
        jobs = JobModel(filename=uploaded_file.filename, data=uploaded_file.read())
        db.session.add(jobs)
    elif uploaded_file.filename == 'departments.csv':
        deparment = DepartmentModel(filename=uploaded_file.filename, data=uploaded_file.read())
        db.session.add(deparment)
    else:
        hired_employee = HiredEmployeeModel(filename=uploaded_file.filename, data=uploaded_file.read())
        db.session.add(hired_employee)
    db.session.commit()
    return f'CSV file uploaded:'
    
    

'''
# Creating a route and method to instert the batch transactions

@app.route('/insert_batch_trxs', methods=['POST'])
def insert_batch_trxs():
    try:
        data = request.json
        if data:
            # Lets process and load the rows here
            return 'Batch transactions inserted successfully'
        else:
            return 'Invalidad data in the request', 400
    except Exception as e:
        return 'Error in the request: ' + str(e), 500
    