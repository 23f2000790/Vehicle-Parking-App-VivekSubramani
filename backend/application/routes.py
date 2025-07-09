from flask import current_app as app, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from .models import *
from .database import db
from datetime import datetime, timezone
from functools import wraps



@app.route('/api/register',methods=['POST'])
def register():
    email = request.json.get('email')
    username = request.json.get('username')
    password = request.json.get('password')
    phone_no = request.json.get('phone_no')

    if not email or not username or not password or not phone_no:
        return jsonify({"msg" : "Please enter all fields"}), 401

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
                return jsonify({"msg" : "You don't have access to this page"}), 403
            return func(*args, **kwargs)
        return decorator
    return wrapper

@app.route('/api/dashboard')
@jwt_required()
def dashboard():
    if current_user.type == "admin":
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
                "address" : i.address,
                "status" : i.status,
                "status_dict" : output_spots
            }
            output_list.append(output_dict)
        return jsonify({
            "role" : current_user.type,
            "username" : current_user.username,
            "data" : output_list
        })
    
    else:
        reservations = Reservation.query.filter_by(userid = current_user.id).all()
        lots = Parkinglots.query.all()
        res_output = []
        for i in reservations:
            output_dict = {
                "spotid" : i.spotid,
                "address" : i.parkingspot.parkinglots.address,
                "parkingts" : i.parkingts.strftime("%Y-%m-%d %H:%M:%S"),
                "leavingts" : i.leavingts.strftime("%Y-%m-%d %H:%M:%S") if i.leavingts else "",
                "vehiclename" : i.vehiclename,
                "vehiclenp" : i.vehiclenp,
                "status" : i.status
            }
            res_output.append(output_dict)
        lot_output = []
        for j in lots:
            if j.status == 1:
                spotcount = Parkingspot.query.filter(Parkingspot.lotid == j.id, Parkingspot.status == 0).count()
                if spotcount > 0:
                    output_dict = {
                        "id" : j.id,
                        "address" : j.address,
                        "maxspots" : spotcount,
                        "price" : j.priceperhour,
                        "pincode" : j.pincode
                    }
                    lot_output.append(output_dict)
        return jsonify({
            "role" : current_user.type,
            "username" : current_user.username,
            "resdata" : res_output,
            "lotdata" : lot_output
        })





@app.route('/api/addlot', methods = ['POST'])
def addlot():
    cityname = request.json.get("cityname")
    address = request.json.get("address")
    pincode = request.json.get("pincode")
    maxspots = request.json.get("maxspots")
    priceperhour = request.json.get("priceperhour")
    status_1 = request.json.get("status")
    status = False
    if status_1 == "active":
        status = True
    newlot = Parkinglots(cityname=cityname, address=address, pincode=pincode, maxspots=maxspots, priceperhour=priceperhour, status=status)
    db.session.add(newlot)
    db.session.commit()


    for i in range(newlot.maxspots):
        newspot = Parkingspot(lotid = newlot.id, status = 0)
        db.session.add(newspot)
    db.session.commit()

    return jsonify({"msg" : "Lot Added Successfully!!"}), 201


@app.route('/api/editlot/<int:lotid>', methods = ['PUT'])
@type_based_access('admin')
def editlot(lotid):
    lot = Parkinglots.query.get(lotid)
    lot.address = request.json.get("address", lot.address)
    lot.pincode = request.json.get('pincode', lot.pincode)
    lot.maxspots = request.json.get('maxspots', lot.maxspots)
    lot.priceperhour = request.json.get("priceperhour", lot.priceperhour)
    status_1 = request.json.get("status")
    if status_1 is not None:
        if status_1 == "active":
            lot.status = True
        else:
            lot.status = False

    spotoccupied = Parkingspot.query.filter_by(lotid = lot.id, status = 1).all()
    if int(lot.maxspots) < len(spotoccupied):
        return jsonify({"msg" : "Please release the spots to update the maxspots"}), 403
    
    spots = Parkingspot.query.filter_by(lotid = lot.id).all()
    if int(lot.maxspots) < len(spots):
        for i in range((len(spots)-int(lot.maxspots))):
            spot = Parkingspot.query.filter_by(lotid = lot.id, status = 0).first()
            db.session.delete(spot)

    if int(lot.maxspots) > len(spots):
        for i in range((int(lot.maxspots)-len(spots))):
            newspot = Parkingspot(lotid = lot.id, status = 0)
            db.session.add(newspot)
            
    db.session.commit()
    return jsonify({"msg" : "Lot edited successfully!!"}), 201


@app.route('/api/deletelot/<int:lotid>', methods = ['DELETE'])
@type_based_access("admin")
def deletelot(lotid):
    lot = Parkinglots.query.get(lotid)
    spots = Parkingspot.query.filter_by(lotid = lotid).all()
    for i in spots:
        if i.status == 1:
            return jsonify({"msg" : "Please vacate all the spots before deleting the lot"}), 403
    for i in spots:
        db.session.delete(i)
    db.session.delete(lot)
    db.session.commit()
    return jsonify({"msg" : "Lot deleted successfully!!"}), 201


@app.route('/api/bookspot', methods = ['POST'])
@jwt_required()
def bookspot():
    parkingts = datetime.now()
    lotid = request.json.get("lotid")
    spot = Parkingspot.query.filter_by(lotid = lotid).first()
    reserve = Reservation(
        spotid = spot.id,
        userid = current_user.id,
        parkingts = parkingts,
        vehiclename = request.json.get("vehiclename"),
        vehiclenp = request.json.get("vehiclenp"),
        status = 1
    )
    spot.status = 1
    db.session.add(reserve)
    db.session.commit()
    return jsonify({"msg" : "Spot booked successfully"}), 201
    






    
        



