from tokenize import String
from cv2 import norm
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

@app.route('/update-cell', methods=['POST'])
def update_cell():
    print(request.json)
    taskId = request.json['taskId']
    col = request.json['col']
    page = request.json['page']
    idx = request.json['idx']
    newVal = request.json['newVal']
    updateCell(taskTofile[taskId]['path'], col, page, idx, newVal)
    return 'done'

@app.route('/update-head', methods=['POST'])
def update_head():
    print(request.json)
    taskId = request.json['taskId']
    col = request.json['col']
    newVal = request.json['newVal']
    updateHead(taskTofile[taskId]['path'], col, newVal)
    return 'done'

@app.route('/del-col', methods=['POST'])
def del_row():
    print(request.json)
    taskId = request.json['taskId']
    col = request.json['col']
    removeCol(taskTofile[taskId]['path'], col)
    return 'done'

@app.route('/del-row', methods=['POST'])
def del_col():
    print(request.json)
    taskId = request.json['taskId']
    page = request.json['page']
    idx = request.json['idx']
    removeRow(taskTofile[taskId]['path'], page, idx)
    return 'done'

@app.route('/function', methods=['POST'])
def operate():
    print(request.json)
    operation = request.json['operation']
    taskId = request.json['taskId']
    params = request.json['params']
    method = request.json['method'] if 'method' in request.json else ''
    if operation == 'convert':
        if params['type'] == 'json':
            resp = csvTojson(taskTofile[taskId]['path'])
            res = Response(resp, status=200, mimetype='application/json')
            return res
        elif params['type'] == 'csv':
            return send_file(taskTofile[taskId]['path'], mimetype='text/csv', download_name=taskTofile[taskId]['name'])
        elif params['type'] == 'xml':
            xmlf = csvToxml(taskTofile[taskId]['path'])
            return send_file(xmlf, mimetype='application/xml')
    elif operation == 'cleaning':
        if method == 'normalization':
            col = params['col']
            rmin = float(params['min'])
            rmax = float(params['max'])
            normalization(taskTofile[taskId]['path'], col, rmin, rmax)        
        elif method == 'outlier':
            col = params['col']
            rmin = float(params['min'])
            rmax = float(params['max'])
            outlier(taskTofile[taskId]['path'], col, rmin, rmax) 
        elif method == 'null-value':
            col = params['col']
            replacement = params['replace']
            method = 1 if replacement == 'drop' else 2
            nullValues(taskTofile[taskId]['path'], col, method, replacement)
    elif operation == 'visualization': 
        if method == 'columnwise':
            col = params['col']
            graph = columnRep(taskTofile[taskId]['path'], col)
            return send_file(graph, mimetype='application/octet-stream')
        elif method == 'heatmap':
            cols = params['cols']
            graph = coorelation_analysis(taskTofile[taskId]['path'], cols)
            return send_file(graph, mimetype='application/octet-stream')
        elif method == 'column-comparison':
            cols = params['cols']
            col1 = cols[0]
            col2 = cols[1]
            graph = columnComp(taskTofile[taskId]['path'], col1, col2)
            return send_file(graph, mimetype='application/octet-stream')
    elif operation == 'processing':
        if method == 'feature-creation':
            eq = params['eq']
            variables = params['variables']
            var = {}
            for v in variables:
                if v['var'] == '':
                    continue
                var[v['var']] = v['col']['value']
            columnCreation(taskTofile[taskId]['path'], var, eq)
        if method == 'classification':
            pass
        if method == 'feature-reduction':
            pass
        if method == 'clustering':
            pass
    else:
        return "Invalid Input", 400
    return 'done', 200

# main driver function
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
