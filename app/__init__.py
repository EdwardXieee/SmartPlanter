from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
from dotenv import load_dotenv
from config import Config
from app.tasks import prediction_task

# 加载环境变量
load_dotenv()

# 初始化Flask应用
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'mysql+pymysql://root:323993@localhost:3306/smart_planter')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化数据库
db = SQLAlchemy(app)

# 初始化登录管理器
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# 注册蓝图
from app.auth import auth as auth_blueprint
from app.main import main as main_blueprint
from app.api import api as api_blueprint

app.register_blueprint(auth_blueprint)
app.register_blueprint(main_blueprint)
app.register_blueprint(api_blueprint, url_prefix='/api')

# Start prediction task when app starts
with app.app_context():
    prediction_task.start()

from app import models 