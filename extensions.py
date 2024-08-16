from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_caching import Cache
from flask_socketio import SocketIO

db = SQLAlchemy()
jwt = JWTManager()
cache = Cache()
socketio = SocketIO()
