import os
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from os.path import join, dirname, realpath
import pandas as pd


# specify the allowed extensions and folder where data wil be stored
UPLOAD_FOLDER = join(dirname(realpath(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'csv'}

app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# variables stored the uploaded data
df = pd.DataFrame([])
columns = list()
# maxValues = pd.DataFrame([])
# minValues = pd.DataFrame([])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def assign_to_variable(filename):
    path = f'uploads/{filename}'
    return pd.read_csv(path, sep=',')


def create_list_of_columns(filename):
    path = f'uploads/{filename}'
    # print(pd.read_csv(path).columns)
    # print(type(pd.read_csv(path).columns))
    return pd.read_csv(path).columns


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    global df, columns
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            resp = jsonify({'message': 'No file part in the request'})
            resp.status_code = 400
            return resp
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            resp = jsonify({'message': 'No file selected for uploading'})
            resp.status_code = 400
            return resp
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            print("\n\n -------------------------------THE FILE IS UPLOADING IN: ", UPLOAD_FOLDER)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            df = assign_to_variable(filename)
            columns = create_list_of_columns(filename)
            # print(df)
            resp = jsonify({'message': 'File successfully uploaded'})
            resp.status_code = 201
            return resp
        else:
            resp = jsonify({'message': 'Allowed file types is csv'})
            resp.status_code = 400
            return resp
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    </html>
    '''


@app.route('/rows/<filename>')
def number_of_rows(filename):
    print("\n\n -------------------------------NUMBER OF ROWS: ", len(df))
    return f'The number of rows in the uploaded file: {len(df)}'


@app.route('/columns/<filename>')
def number_of_columns(filename):
    print("\n\n -------------------------------NUMBER OF COLUMNS: ", len(df.columns))
    return f'The number of columns in the uploaded file: {len(df.columns)}'


@app.route('/<filename>/min/<number>')
def column_min(filename, number):
    print(columns[int(number)], "min value:", df[columns[int(number)]].min())
    return f'Minimum value of the column ({columns[int(number)]}): {df[columns[int(number)]].min()}'


@app.route('/<filename>/max/<number>')
def column_max(filename, number):
    print(columns[int(number)], "max value:", df[columns[int(number)]].max())
    return f'Maximum value of the column ({columns[int(number)]}): {df[columns[int(number)]].max()}'


@app.route('/<filename>/mean/<number>')
def column_mean(filename, number):
    # print(columns[int(number)], "min value: ", df[columns[int(number)]].mean())
    return f'Mean value of the column ({columns[int(number)]}): {df[columns[int(number)]].mean()}'


@app.route('/<filename>/column/<number>/percentile/<pNumber>')
def column_percentile(filename, number, pNumber):
    column = df[columns[int(number)]].sort_values()
    column = column.reset_index(drop=True)
    n = int(pNumber) / 100 * len(column)
    if n % 1 == 0:
        # print("n:", n)
        # print("columns: ", column[n], column[n+1])
        return f'{pNumber}th percentile: {(column[n-1] + column[n]) / 2}'
    else:
        if n % 1 >= .5:
            n += (1 - n % 1)
            return f'{pNumber}th percentile: {column[n]}'
        else:
            n -= n % 1
            return f'{pNumber}th percentile: {column[n-1]}'


@app.route('/<filename>/missing/column/<number>')
def percent_missing(filename, number):
    print("Number of empty fields: ", df[columns[int(number)]].isnull().sum())
    return f'Percent of missing values: {(df[columns[int(number)]].isnull().sum() * 100) / len(df)}'


if __name__ == '__main__':
    app.run(debug=True)
