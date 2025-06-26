from flask import current_app as app, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from .models import Users
from .database import db
from datetime import datetime, timedelta



@app.route('/register',methods=['POST'])
def register():
    email = request.json.get('email')
    username = request.json.get('username')
    password = request.json.get('password')
    phone_no = request.json.get('phone_no')

    users = Users.query.filter((Users.username == username) | (Users.email == email)).first()
    if users:
        return jsonify({"msg":"User already exists!"}), 409
    hashpass = generate_password_hash(password)
    newuser = Users(email=email, username=username, password=hashpass, phone_no=phone_no, status=True)
    db.session.add(newuser)
    db.session.commit()

    return jsonify({"msg":"User created successfully"}), 201


@app.route('/login',methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    user = Users.query.filter_by(username = username).first()
    if not user:
        return jsonify({"msg":"Invalid Username"}), 401
    if not check_password_hash(user.password, password):
        return jsonify({"msg":"Incorrect Password"}), 409
    
    access_token = create_access_token(identity = user)
    return jsonify(access_token = access_token)
    

