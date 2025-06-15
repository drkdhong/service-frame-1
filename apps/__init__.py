# app/__init__.py
from flask import Flask
from .config import Config

def create_app():
    app = Flask(__name__)
    #app = Flask(__name__, static_folder='../apps/static')
    app.config.from_object(Config)

    # main 블루프린트 등록
    from .main import main 
    app.register_blueprint(main)

    return app 

