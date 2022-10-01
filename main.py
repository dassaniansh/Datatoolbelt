from tokenize import String
from flask import Flask, render_template, request
from sklearn.utils import column_or_1d
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
from datetime import datetime
from dtb_functions import *

app = Flask(__name__)

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
      f.save(secure_filename(f.filename))

    # Conversion of files into CSV
      if f.filename[-3:] == 'xml':
       xmlTocsv(xmlFile= f.filename, csvfile=f'{f.filename[:-3]}csv')
    
      if f.filename[-4:] == 'json':
       jsonTocsv(jsonfile=f.filename, csvfile=f'{f.filename[:-4]}csv')

    # task_id is created according to time
    # hour[2 digits] min[2 digits] sec[2 digits]
      task_id=str(datetime.now().time()).replace(':', '')[:6]
      if f.filename[-3:] == 'csv':
        taskTofile[task_id]=f.filename
        return f'file uploaded successfully with filename {taskTofile[task_id]} and task id is {task_id}'
      else:
        return 'Invalid file format, we only support csv, xml, json'
   except:
    return 'Something wrong occured'

@app.route('/fetch/<task_id_for_file>')
def fetch_file(task_id_for_file):
    # return meta data from database
    output = metaData(taskTofile[task_id_for_file])
    return output

@app.route('/fetch/<task_id_for_file>/<column>/<page>')
def fetch_column(task_id_for_file, column, page):
    # getting column data from file
    data=taskTofile[task_id_for_file]
    
    return f'file uploaded successfully with filename with task id is {task_id_for_file}'

# main driver function
if __name__ == '__main__':
	app.run(debug=True)
