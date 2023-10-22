import os

from flask import Flask, request, render_template, redirect, url_for, flash
from werkzeug.utils import secure_filename
import pandas as pd

from db import db
import models


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
    if 'file' in request.files:
        uploaded_file = request.files['file']
        filename = secure_filename(uploaded_file.filename)
        uploaded_file.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename))
        data = pd.read_csv(uploaded_file)
        data.to_csv('uploaded')
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
    