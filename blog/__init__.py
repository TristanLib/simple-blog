from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv
import os
import hashlib

# 加载环境变量
load_dotenv()

# 初始化扩展
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    
    # 配置
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///blog.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # 自定义 hash 过滤器
    @app.template_filter('hash')
    def hash_filter(value, hash_type='md5'):
        """计算字符串的哈希值"""
        if hash_type.lower() == 'md5':
            return hashlib.md5(value.encode('utf-8')).hexdigest()
        return value

    # 注册蓝图
    from .views import main
    from .auth import auth
    from .admin import admin_bp
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(admin_bp)

    # 创建数据库表
    with app.app_context():
        db.create_all()

    return app
