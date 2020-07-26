import os

from flask import Blueprint, redirect, current_app
from flask.helpers import send_from_directory


main_bp = Blueprint('main_bp', __name__)


@main_bp.route('/', methods=['GET'])
def index():
    return redirect('/dashboard/')

@main_bp.route('/download/<string:filename>', methods=['GET'])
def download_file(filename):
    data = os.path.join(current_app.root_path, current_app.config['DATA_DIR'])
    return send_from_directory(directory=data, filename=filename, as_attachment=True)