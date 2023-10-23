import os

from flask import Flask, request, render_template, jsonify
from flask import redirect, url_for, flash
from sqlalchemy import text

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
        data = pd.read_csv(csv_file_path, header=None)
        
    
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

    
# Creating endpoint to the metrics

# Metric 1 : 
# Number of employees hired for each job and department in 2021 divided by quarter. 
# The table must be ordered alphabetically by department and job.

@app.route('/query_metric1', methods=['GET'])
def query_metric1():
    try:
        # Executing SQL query
        consulta_sql = text("""
        SELECT
            d.department AS department,
            j.job AS job,
            SUM(CASE WHEN strftime('%m', e.datetime) BETWEEN '01' AND '03' THEN 1 ELSE 0 END) AS q1,
            SUM(CASE WHEN strftime('%m', e.datetime) BETWEEN '04' AND '06' THEN 1 ELSE 0 END) AS q2,
            SUM(CASE WHEN strftime('%m', e.datetime) BETWEEN '07' AND '09' THEN 1 ELSE 0 END) AS q3,
            SUM(CASE WHEN strftime('%m', e.datetime) BETWEEN '10' AND '12' THEN 1 ELSE 0 END) AS q4

        FROM
        hired_employees e
        JOIN departments d ON e.department_id = d.id
        JOIN jobs j ON e.job_id = j.id
        WHERE
          substr(e.datetime, 0,5) = '2021'
        GROUP BY
          department, job
        ORDER BY
          department, job""")
        result = db.session.execute(consulta_sql)

        # Converting result in a dictionary
        data = [{'department': row.department, 
                  'job': row.job, 
                  'Q1': row.q1,
                  'Q2': row.q2,
                  'Q3': row.q3,
                  'Q4': row.q4
                } 
                for row in result]

        # Respond with data as JSON
        return jsonify(data)

    except Exception as e:
        return str(e), 500  # Exception handling
         
# Metric 2 : 
# List of ids, name and number of employees hired of each department that hired more
#employees than the mean of employees hired in 2021 for all the departments, ordered
#by the number of employees hired (descending)

@app.route('/query_metric2', methods=['GET'])
def query_metric2():
    try:
        # Executing SQL query
        
        consulta_sql = text("""
        SELECT
            d.id AS department_id,
            d.department AS department,
            COUNT(e.id) AS hired
        FROM
        departments d
        JOIN hired_employees e ON d.id = e.department_id
        WHERE substr(e.datetime, 0,5) = '2021' 
        GROUP BY
          d.id, d.department
        HAVING
          COUNT(e.id) > (SELECT AVG(employee_count) FROM (SELECT COUNT(*) AS employee_count FROM hired_employees WHERE substr(datetime, 0,5) = '2021' GROUP BY department_id) subquery)
        ORDER BY
          hired DESC;
        """)
        result = db.session.execute(consulta_sql)

        # Converting result in a dictionary
        data = [{'id': row.department_id,
                 'department': row.department,
                 'hired': row.hired
                } 
                for row in result]

        # Respond with data as JSON
        return jsonify(data)

    except Exception as e:
        return str(e), 500  # Exception handling    