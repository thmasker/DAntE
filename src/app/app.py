import os
from flask import Flask, render_template, flash, request, redirect, url_for

from werkzeug.utils import secure_filename


UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'csv'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def dir_last_updated(folder):
    return str(max(os.path.getmtime(os.path.join(root_path, f)) for root_path, dirs, files in os.walk(folder) for f in files))


app = Flask(__name__)
app.secret_key = b'\xde\xd0\x9d\x19\xe4\xc4k\x90\xe3Z\xc9H:\xea\x9f9'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024


@app.route('/', methods=['POST'])
def upload_csv():
    if 'file' not in request.files:
        flash('No file part', category='error')
        return render_template('index.html')

    f = request.files['file']
    if f.filename == '':
        flash('No selected file', category='error')
        return render_template('index.html')
    elif f and allowed_file(f.filename):
        filename = secure_filename(f.filename)
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash('File uploaded successfully', category='info')
        return render_template('index.html')
    else:
        flash('Only CSV files are allowed', category='error')
        return render_template('index.html')
    

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', last_updated=dir_last_updated('static'))

app.run(debug=True)