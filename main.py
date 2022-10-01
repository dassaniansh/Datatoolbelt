from tokenize import String
from flask import Flask, render_template, request
from sklearn.utils import column_or_1d
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
from datetime import datetime
import random
# from dtb_functions import *

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
      task_id=str(random.randint(0, 999999)).zfill(6)
      while task_id in taskTofile:
        task_id = str(random.randint(0, 999999)).zfill(6)
      f.save(secure_filename('./data/' + task_id))
    # prebuilt function
    # conversion of file to csv()

    # task_id is created according to time
    # hour[2 digits] min[2 digits] sec[2 digits]
      taskTofile[task_id]=task_id
      print(taskTofile)
      return task_id, 200
   except:
    return 'Something wrong occured'

@app.route('/fetch/<task_id_for_file>')
def fetch_file(task_id_for_file):
    # return meta data from database
      return f'file uploaded successfully with filename with task id is {task_id_for_file}'

@app.route('/fetch/<task_id_for_file>/<column>/<page>')
def fetch_column(task_id_for_file, column, page):
    # getting column data from file
    data=taskTofile[task_id_for_file]
    return f'file uploaded successfully with filename with task id is {task_id_for_file}'

# main driver function
if __name__ == '__main__':
	app.run(debug=True)
