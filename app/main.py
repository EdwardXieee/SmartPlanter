from flask import Blueprint, render_template, url_for, redirect
from flask_login import login_required, current_user
from app.models import FogDevice

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return redirect(url_for('auth.login'))

@main.route('/dashboard')
@login_required
def dashboard():
    fog_devices = FogDevice.query.filter_by(user_id=current_user.user_id).all()
    return render_template('main/dashboard.html', fog_devices=fog_devices) 