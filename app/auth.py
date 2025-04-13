from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from app.models import User
from app import db

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if not user or user.password != password:
            flash('Incorrect username or password')
            return redirect(url_for('auth.login'))
            
        login_user(user)
        return redirect(url_for('main.dashboard'))
        
    return render_template('auth/login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        
        user = User.query.filter_by(username=username).first()
        
        if user:
            flash('Username already exists')
            return redirect(url_for('auth.register'))
            
        new_user = User(
            username=username,
            password=password,
            email=email
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please log in')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login')) 