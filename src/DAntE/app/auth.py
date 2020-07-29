import bcrypt

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from flask_login import current_user, login_user, logout_user, fresh_login_required, login_required

from app import mongo, login_manager
from app.models.user import User


auth_bp = Blueprint('auth_bp', __name__, url_prefix='/auth')


@login_manager.user_loader
def load_user(email):
    user = User.find_one(email)
    if not user:
        return None
    return User(user['email'])

@auth_bp.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main_bp.index'))

    if request.method == 'POST':
        user = User.find_one(request.form['email'])
        if user and User.check_password(user['password'], request.form['password']):
            user_obj = User(user['email'])
            login_user(user_obj)
            return redirect(url_for('main_bp.index'))
        else:
            flash('Invalid email or password', category='error')
            return render_template('login.html')
    
    return render_template('login.html')

@auth_bp.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth_bp.login'))

@auth_bp.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        existing_user = User.find_one(email)

        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
            User.insert(email, hashpass)
            session['email'] = email

            return redirect(url_for('main_bp.index'))

        flash(email + ' is already registered!', category='error')
        return render_template('signup.html')

    return render_template('signup.html')