from flask import Flask, g, request, redirect, url_for
from flask_babel import Babel
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from oauthlib.oauth2 import WebApplicationClient
import os
from flask_socketio import SocketIO

from config import Config
from dotenv import load_dotenv
from pymongo import MongoClient
from flask_login import UserMixin
from bson import ObjectId

load_dotenv()

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)

app.debug = True  # Enable debug mode
app.config.from_object(Config)

babel = Babel(app)
client = WebApplicationClient(app.config['GOOGLE_CLIENT_ID'])
google_client = WebApplicationClient(app.config['GOOGLE_CLIENT_ID'])

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

# mongo_client = MongoClient('localhost', 27017)
mongo_client = MongoClient('waramity-mongo', 27017)

user_db = mongo_client["user"]
feature_db = mongo_client["feature"]

from app.features.ai_hub import ai_hub as ai_hub_blueprint
app.register_blueprint(ai_hub_blueprint)

@babel.localeselector
def get_locale():
    if not g.get('lang_code', None):
        g.lang_code = request.accept_languages.best_match(
            app.config['LANGUAGES']) or app.config['LANGUAGES'][0]
    return g.lang_code

@app.route('/')
def index():
    if not g.get('lang_code', None):
        get_locale()
    return redirect(url_for('main.index'))

from app.features.ai_hub.models import User as AIUser

@login_manager.user_loader
def load_user(user_id):
    if user_id.startswith('mongo_'):
        user_json = user_db.profile.find_one({'_id': user_id})
        if not user_json:
            return None
        return AIUser(user_json)
    else:
        return DatingUser.query.get(user_id)

with app.app_context():
    try:
        server_info = mongo_client.server_info()
        if server_info.get('ok') == 1:
            print("Connected to MongoDB")
        else:
            print("Failed to connect to MongoDB")
    except Exception as e:
        print("Error:", str(e))
