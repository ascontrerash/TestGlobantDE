from flask import Flask, request
import pandas as pd

app = Flask(__name__)

# Creating a route and method to recive and upload the csv

@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    if 'file' in request.files:
        file = request.files['file']
        if file.filename != '':
            data = pd.read_csv(file)
            # Lets process and clean up the data
            return 'CSV File: ' +  file.filename + ' was uploaded and processed successfully'
        else:
            return 'Invalid CSV File', 400
    else: 
        return 'No CSV File was provided'
    
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