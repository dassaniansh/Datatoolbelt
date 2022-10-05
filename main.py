from tokenize import String
from flask import make_response, Response, Flask, jsonify, render_template, request, send_file
from sklearn.utils import column_or_1d
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from datetime import datetime
from dtb_functions import *
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

uploads_dir = os.path.join(app.instance_path, 'uploads')
os.makedirs(uploads_dir, exist_ok=True)

task_id = 0
taskTofile = {
  "210747": {
    "dt": "2022-10-01", 
    "name": "username.csv", 
    "path": "E:\\dtb\\Datatoolbelt\\instance\\uploads\\210747",
    "size": 176
  },
  "190854": {
    "dt": "2022-10-02", 
    "name": "cars.csv", 
    "path": "E:\\dtb\\Datatoolbelt\\instance\\uploads\\190854", 
    "size": 22663
  }, 
  "194319": {
    "dt": "2022-10-02", 
    "name": "drake_data.csv", 
    "path": "E:\\dtb\\Datatoolbelt\\instance\\uploads\\194319", 
    "size": 800611
  }, 
}


@app.route('/')
def hello_world():
    return 'Hello World'


@app.route('/upload')
def upload_file():
    return render_template('upload.html')


@app.route('/uploader', methods=['GET', 'POST'])
def upload_files():
    try:
        if request.method == 'POST':
            f = request.files['file']

            task_id = str(datetime.now().time()).replace(':', '')[:6]
            while task_id in taskTofile:
                task_id = str(datetime.now().time()).replace(':', '')[:6]
            fileWithPath = os.path.join(uploads_dir, secure_filename(task_id))
            f.save(fileWithPath)
            mimetype = f.content_type

        # Conversion of files into CSV
            if mimetype.split('/')[-1] == "xml":
                xmlTocsv(xmlFile=fileWithPath, csvfile=fileWithPath)

            if mimetype.split('/')[-1] == 'json':
                jsonTocsv(jsonfile=fileWithPath, csvfile=fileWithPath)

        # task_id is created according to time
        # hour[2 digits] min[2 digits] sec[2 digits]

            if mimetype.split('/')[-1] in ['csv', 'xml', 'json']:
                taskTofile[task_id] = {
                    'name': f.filename,
                    'path': fileWithPath,
                    'size': os.stat(fileWithPath).st_size,
                    'dt': str(datetime.now().date())
                }
                return task_id, 200
            else:
                return 'Invalid file format, we only support csv, xml, json'
    except Exception as e:
        print(e)
        return 'Something wrong occured'


@app.route('/fetch')
def fetch():
    return taskTofile, 200


@app.route('/fetch/<task_id_for_file>')
def fetch_file(task_id_for_file):
    # return meta data from database
    output, rows = metaData(taskTofile[task_id_for_file]['path'])
    metadata = {
      'name': taskTofile[task_id_for_file]['name'],
      'size': taskTofile[task_id_for_file]['size'],
      'dt': taskTofile[task_id_for_file]['dt'],
      'col': output,
      'rows': rows
    }
    print(metadata)
    return metadata, 200


@app.route('/get', methods=['GET', 'POST'])
def fetch_column():
    print(request.json)
    taskId = request.json['taskId']
    col = request.json['col']
    page = request.json['page']
    return {'values': getColumnPage(taskTofile[taskId]['path'], col, page)}

@app.route('/function', methods=['POST'])
def operate():
    print(request.json)
    operation = request.json['operation']
    taskId = request.json['taskId']
    params = request.json['params']
    if operation == 'convert':
        if params['type'] == 'json':
            resp = csvTojson(taskTofile[taskId]['path'])
            res = Response(resp, status=200, mimetype='application/json')
            return res
        elif params['type'] == 'csv':
            return send_file(taskTofile[taskId]['path'], mimetype='text/csv', download_name=taskTofile[taskId]['name'])
        elif params['type'] == 'xml':
            xmlf = csvToxml(taskTofile[taskId]['path'])
            fname = taskTofile[taskId]['name']
            fname = '.'.join(fname.split('.')[:-1]) + '.xml'
            return send_file(xmlf, mimetype='application/xml', download_name=fname)
    elif operation == 'clean':
        pass
    elif operation == 'visualize':
        pass
    elif operation == 'analyze':
        pass
    else:
        return "Invalid Input", 400
    return 'done'

# main driver function
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
