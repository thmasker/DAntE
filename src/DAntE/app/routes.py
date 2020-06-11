from flask import Blueprint, render_template, redirect, url_for, session, request
from flask_login import login_required


main_bp = Blueprint('main_bp', __name__)


@main_bp.route('/', methods=['GET'])
@login_required
def index():
    return render_template('index.html')