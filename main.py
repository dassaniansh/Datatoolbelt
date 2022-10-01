from tokenize import String
from flask import Flask, jsonify,render_template, request
from sklearn.utils import column_or_1d
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
from datetime import datetime
from dtb_functions import *
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

task_id=0
taskTofile={}

@app.route('/')
def hello_world():
	return 'Hello World'

@app.route('/upload')
def upload_file():
   return render_template('upload.html')

@app.route('/uploader', methods = ['GET', 'POST'])
def upload_files():
   try:
    if request.method == 'POST':
      f = request.files['file']

      task_id=str(datetime.now().time()).replace(':', '')[:6]
      while task_id in taskTofile:
        task_id=str(datetime.now().time()).replace(':', '')[:6]

      f.save(os.path.join(app.instance_path, 'data', secure_filename(task_id)))
      mimetype = f.content_type

    # Conversion of files into CSV
      if mimetype.split('/')[-1]=="xml":
       xmlTocsv(xmlFile= task_id, csvfile=task_id)
    
      if mimetype.split('/')[-1] == 'json':
       jsonTocsv(jsonfile=task_id, csvfile=task_id)

    # task_id is created according to time
    # hour[2 digits] min[2 digits] sec[2 digits]
      
      if mimetype.split('/')[-1] in ['csv', 'xml', 'json']:
        taskTofile[task_id]=f.filename
        return f'file uploaded successfully with filename {taskTofile[task_id]} and task id is {task_id}'
      else:
        return 'Invalid file format, we only support csv, xml, json'
   except:
    return 'Something wrong occured'

@app.route('/fetch/<task_id_for_file>')
def fetch_file(task_id_for_file):
    # return meta data from database
    output = metaData(task_id_for_file)
    return jsonify(output)

@app.route('/fetch/<task_id_for_file>/<column>/<page>')
def fetch_column(task_id_for_file, column, page):
    # getting column data from file
    data=taskTofile[task_id_for_file]
    
    return f'file uploaded successfully with filename with task id is {task_id_for_file}'

# main driver function
if __name__ == '__main__':
	app.run(debug=True)
