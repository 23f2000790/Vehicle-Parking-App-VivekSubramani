from flask import current_app as app, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from .models import *
from .database import db
from datetime import datetime, timedelta
from functools import wraps



@app.route('/api/register',methods=['POST'])
def register():
    email = request.json.get('email')
    username = request.json.get('username')
    password = request.json.get('password')
    phone_no = request.json.get('phone_no')

    if not email or not username or not password or not phone_no:
        return jsonify(message = "Please enter all fields"), 401

    users = Users.query.filter((Users.username == username) | (Users.email == email)).first()
    if users:
        return jsonify({"msg":"User already exists!"}), 409
    hashpass = generate_password_hash(password)
    newuser = Users(email=email, username=username, password=hashpass, phone_no=phone_no, status=True)
    db.session.add(newuser)
    db.session.commit()

    return jsonify({"msg":"Account created successfully, Please Login"}), 201


@app.route('/api/login',methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    user = Users.query.filter_by(username = username).first()
    if not user:
        return jsonify({"msg":"Invalid Username"}), 401
    if not check_password_hash(user.password, password):
        return jsonify({"msg":"Incorrect Password"}), 401
    
    access_token = create_access_token(identity = user)
    return jsonify(access_token = access_token)


def type_based_access(valid_type):
    def wrapper(func):
        @wraps(func)
        @jwt_required()
        def decorator(*args, **kwargs):
            if current_user.type != valid_type:
                return jsonify(message = "You don't have access to this page"), 403
            return func(*args, **kwargs)
        return decorator
    return wrapper

@app.route('/api/dashboard')
@jwt_required()
def dashboard():
    if current_user.role == "admin":
        lots = Parkinglots.query.all()
        output_list = []
        for i in lots:
            no_of_spots = Parkingspot.query.filter_by(lotid = i.id).all()
            output_spots = {}
            for j in no_of_spots:
                output_spots[j.id] = j.status
            output_dict = {
                "lot_id" : i.id,
                "city" : i.cityname,
                "pincode" : i.pincode,
                "spots" : len(no_of_spots),
                "price" : i.priceperhour,
                "status_dict" : output_spots
            }
            output_list.append(output_dict)
        return jsonify({
            "username" : current_user.username,
            "data" : output_list
        })


@app.route('/api/addlot', methods = ['POST'])
@type_based_access("admin")
def addlot():
    cityname = request.json.get("cityname")
    address = request.json.get("address")
    pincode = request.json.get("pincode")
    maxspots = request.json.get("maxspots")
    priceperhour = request.json.get("priceperhour")
    status = request.json.get("status")

    newlot = Parkinglots(cityname=cityname, address=address, pincode=pincode, maxspots=maxspots, priceperhour=priceperhour, status=status)
    db.session.add(newlot)
    db.session.commit()


    for i in range(newlot.maxspots):
        newspot = Parkingspot(lotid = newlot.id, status = 1)
        db.session.add(newspot)
    db.session.commit()

    return "lot added"


@app.route('/api/editlot/<int:lotid>', methods = ['PUT'])
@type_based_access('admin')
def editlot(lotid):
    lot = Parkinglots.query.get(lotid)
    lot.address = request.json.get("address", lot.address)
    lot.pincode = request.json.get('pincode', lot.pincode)
    lot.maxspots = request.json.get('maxspots', lot.maxspots)
    lot.priceperhour = request.json.get("priceperhour", lot.priceperhour)
    lot.status = request.json.get("status", lot.status)

    spotoccupied = Parkingspot.query.filter_by(lotid = lot.id, status = 0).all()
    if int(lot.maxspots) < len(spotoccupied):
        return jsonify(message = "Please release the spots to update the maxspots"), 403
    
    spots = Parkingspot.query.filter_by(lotid = lot.id).all()
    if int(lot.maxspots) < len(spots):
        for i in range((len(spots)-int(lot.maxspots))):
            spot = Parkingspot.query.filter_by(lotid = lot.id, status = 1).first()
            db.session.delete(spot)

    if int(lot.maxspots) > len(spots):
        for i in range((int(lot.maxspots)-len(spots))):
            newspot = Parkingspot(lotid = lot.id, status = 1)
            db.session.add(newspot)
            
    db.session.commit()
    return "edited"


@app.route('/api/deletelot/<int:lotid>', methods = ['DELETE'])
@type_based_access("admin")
def deletelot(lotid):
    lot = Parkinglots.query.get(lotid)
    spots = Parkingspot.query.filter_by(lotid = lotid).all()
    for i in spots:
        if i.status == 0:
            return jsonify(message = "Please vacate all the spots before deleting the lot"), 403
    for i in spots:
        db.session.delete(i)
    db.session.delete(lot)
    db.session.commit()
    return "deleted"






    
        



