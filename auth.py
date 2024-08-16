from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import create_access_token
import bcrypt
from extensions import db, jwt  # Import db from extensions.py
from models import User

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@auth.route('/register', methods=['GET'])
def register_page():
    return render_template('register.html')

@auth.route('/register', methods=['POST'])
def register():
    username = request.json.get('username', None)
    password = request.json.get('password', None)

    if not username or not password:
        return jsonify({"msg": "Username and password required"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"msg": "Username already exists"}), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "User created successfully"}), 201

@auth.route('/login', methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)

    user = User.query.filter_by(username=username).first()

    if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200

    return jsonify({"message": "Bad username or password"}), 401
