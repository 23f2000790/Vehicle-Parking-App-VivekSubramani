from flask import current_app as app, jsonify, request, send_from_directory
from flask_jwt_extended import create_access_token, jwt_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from .models import *
from .database import db
from datetime import datetime, timezone
from functools import wraps
from sqlalchemy import or_
from celery.result import AsyncResult
from .tasks import csv_report, monthly_report, generate_msg, vacatespot_msg
from .caching import cache



@app.route('/api/register',methods=['POST'])
def register():
    email = request.json.get('email')
    username = request.json.get('username')
    password = request.json.get('password')
    phone_no = request.json.get('phone_no')

    users = Users.query.filter((Users.username == username) | (Users.email == email)).first()
    if len(password) < 4:
        return jsonify({"msg":"Length of password should be atleast 4!"}), 409
    if users:
        return jsonify({"msg":"User already exists!"}), 409
    phone_check = Users.query.filter_by(phone_no=phone_no).first()
    if phone_check:
        return jsonify({"msg":"This phone number already exists!"}), 409
    if len(phone_no) != 10:
        return jsonify({"msg": "Invalid Phone number!"}), 409
    hashpass = generate_password_hash(password)
    newuser = Users(email=email, username=username, password=hashpass, phone_no=phone_no, status=True)
    db.session.add(newuser)
    db.session.commit()

    cache.delete('user_data')
    return jsonify({"msg":"Account created successfully, Please Login"}), 201


@app.route('/api/login',methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    user = Users.query.filter_by(username = username).first()
    if not user:
        return jsonify({"msg":"User does not exist, please register"}), 401
    if not check_password_hash(user.password, password):
        return jsonify({"msg":"Incorrect Password"}), 401
    if user.status == 0:
        return jsonify({"msg":"Account Unauthorized, Please contact Admin"}), 401
    
    access_token = create_access_token(identity = user)
    cache.delete('dashboard_data')
    cache.delete('summary_data')

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
@cache.cached(timeout=300, key_prefix='dashboard_data')
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
                "id" : i.id,
                "spotid" : i.spotid,
                "address" : i.address,
                "parkingts" : i.parkingts.strftime("%Y-%m-%d %H:%M:%S"),
                "leavingts" : i.leavingts.strftime("%Y-%m-%d %H:%M:%S") if i.leavingts else "",
                "price" : i.price,
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
    existaddress = Parkinglots.query.filter_by(address = address).first()
    if existaddress:
        return jsonify({"msg" : "Cannot add 2 lots at same address!!"}), 409
    if len(pincode) != 6:
        return jsonify({"msg" : "Invalid Pincode!!"}), 409
    newlot = Parkinglots(cityname=cityname, address=address, pincode=pincode, maxspots=maxspots, priceperhour=priceperhour, status=status)
    db.session.add(newlot)
    db.session.commit()


    for i in range(newlot.maxspots):
        newspot = Parkingspot(lotid = newlot.id, status = 0)
        db.session.add(newspot)
    db.session.commit()

    cache.delete('dashboard_data')
    return jsonify({"msg" : "Lot Added Successfully!!"}), 201


@app.route('/api/editlot/<int:lotid>', methods = ['PUT'])
@type_based_access('admin')
def editlot(lotid):
    spotoccupied = Parkingspot.query.filter_by(lotid = lotid, status = 1).all()
    lot = Parkinglots.query.get(lotid)
    if len(spotoccupied) > 0:
        newmaxspots = int(request.json.get('maxspots', lot.maxspots))
        newpriceperhour = int(request.json.get("priceperhour", lot.priceperhour))
        if newmaxspots < len(spotoccupied):
            return jsonify({"msg" : "Please release the spots to update the maxspots"}), 403
        
        spots = Parkingspot.query.filter_by(lotid = lot.id).all()
        if newmaxspots < len(spots):
            for i in range((len(spots)-newmaxspots)):
                spot = Parkingspot.query.filter_by(lotid = lot.id, status = 0).first()
                db.session.delete(spot)

        if newmaxspots > len(spots):
            for i in range(newmaxspots-len(spots)):
                newspot = Parkingspot(lotid = lot.id, status = 0)
                db.session.add(newspot)
        status_1 = request.json.get("status")
        if status_1 is not None:
            if status_1 == "active":
                lot.status = True
            else:
                lot.status = False
        lot.maxspots = newmaxspots
        lot.priceperhour = newpriceperhour
        db.session.commit()
        cache.delete('dashboard_data')
        return jsonify({"msg" : "Only maxspots and price/hour have been edited due to some occupied spots!!"}), 201
    
    lot.cityname = request.json.get("cityname", lot.cityname)
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
    if request.json.get('pincode'):
        if len(request.json.get('pincode')) != 6:
            return jsonify({"msg" : "Invalid Pincode!!"}), 409
        
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
    cache.delete('dashboard_data')
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
    cache.delete('dashboard_data')
    return jsonify({"msg" : "Lot deleted successfully!!"}), 201


@app.route('/api/bookspot', methods = ['POST','PUT'])
@jwt_required()
def bookspot():
    parkingts = datetime.now()
    lotid = request.json.get("lotid")
    vehiclenp = request.json.get("vehiclenp")
    rescheck = Reservation.query.filter_by(vehiclenp = vehiclenp, status = 1).first()
    if rescheck:
        return jsonify({"msg" : "Vehicle with this number place is already parked in some other spot!!"}), 409
    if len(vehiclenp) != 10:
        return jsonify({"msg": "Invalid Vehicle Number!"})
    spot = Parkingspot.query.filter_by(lotid = lotid, status = 0).first()
    reserve = Reservation(
        lotid = lotid,
        spotid = spot.id,
        address = spot.parkinglots.address,
        userid = current_user.id,
        parkingts = parkingts,
        priceperhour = spot.parkinglots.priceperhour,
        vehiclename = request.json.get("vehiclename"),
        vehiclenp = vehiclenp,
        status = 1
    )
    spot2 = Parkingspot.query.get(spot.id)
    spot2.status = 1
    db.session.add(reserve)
    db.session.commit()
    res = generate_msg.delay(current_user.username, reserve.id, request.json.get("vehiclename"), spot.id, spot.parkinglots.address)
    msg = "Spot #"+str(spot.id)+" is your allocated spot"
    cache.delete('dashboard_data')
    cache.delete('summary_data')
    cache.delete('user_data')
    return jsonify({"msg" : msg}), 201


@app.route('/api/users')
@jwt_required()
@cache.cached(timeout=300, key_prefix='user_data')
def users():
    users = Users.query.filter(Users.type == "user").all()
    role = current_user.type
    data = []
    for i in users:
        resdata = []
        reservations = Reservation.query.filter_by(userid = i.id).all()
        for j in reservations:
            res_obj = {
                "id": j.id,
                "lotid": j.lotid,
                "spotid": j.spotid,
                "userid": j.userid,
                "parkingts": j.parkingts,
                "leavingts": j.leavingts,
                "price": j.price,
                "priceperhour": j.priceperhour,
                "vehiclename": j.vehiclename,
                "vehiclenp": j.vehiclenp,
                "status": j.status
            }
            resdata.append(res_obj)
        user_obj = {
            "id": i.id,
            "email": i.email,
            "username": i.username,
            "phone_no": i.phone_no,
            "status": i.status,
            "reservations" : resdata
        }
        data.append(user_obj)
    return jsonify({"data":data, "role" : role})


@app.route('/api/edituser', methods = ['PUT'])
@jwt_required()
def edituser():
    userid = request.json.get("userid")
    user = Users.query.get(userid)
    if user.status:
        user.status = False
    else:
        user.status = True
    db.session.commit()
    cache.delete('dashboard_data')
    cache.delete('user_data')
    cache.delete('summary_data')
    return jsonify({"msg" : "Status Changed Successfully!!"}), 201
    

@app.route('/api/vacatespot', methods=['PUT'])
@jwt_required()
def vacatespot():
    lts = datetime.now()
    spotid = request.json.get("spotid")
    id = request.json.get("id")
    spot = Parkingspot.query.get(spotid)
    price = spot.parkinglots.priceperhour
    pts_str = request.json.get("pts")
    pts = datetime.strptime(pts_str, "%Y-%m-%d %H:%M:%S")
    timediff = lts - pts
    timediffsec = timediff.total_seconds()
    priceforsec = price/3600
    totalprice = round(timediffsec*priceforsec,2)

    res = Reservation.query.get(id)
    res.price = totalprice
    res.leavingts = lts
    res.status = 0
    spot.status = 0
    db.session.commit()
    res = vacatespot_msg.delay(current_user.username, res.address, res.vehiclename, res.parkingts, res.leavingts, res.price)
    cache.delete('dashboard_data')
    cache.delete('summary_data')
    cache.delete('user_data')
    return jsonify({"msg":"Spot Vacated Successfully"}),201


@app.route('/api/search')
@jwt_required()
def search():
    searchword = request.args.get("searchword")
    query = "%" + searchword + "%"
    result = Parkinglots.query.filter(or_(Parkinglots.address.like(query), Parkinglots.pincode.like(query))).all()
    lot_output = []
    if len(result) == 0:
        return jsonify({"msg" : "No results found"}), 404
    for j in result:
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
    cache.delete('dashboard_data')
    return jsonify({"searchres" : lot_output}), 201


@app.route('/api/bill')
@jwt_required()
def bill():
    resid = request.args.get("id")
    res = Reservation.query.get(resid)
    pts = res.parkingts
    lts = res.leavingts
    timetaken = lts - pts
    insec = timetaken.total_seconds()
    hour = int(insec//3600)
    minute = int((insec%3600)//60)
    seconds = int(insec%60)
    final_time = str(hour) + "hr, " + str(minute) + "min, " + str(seconds) + "sec"
    res_obj = {
        "resid": resid,
        "address": res.address,
        "priceperhour": res.priceperhour,
        "vehiclename": res.vehiclename,
        "vehiclenp": res.vehiclenp,
        "parkingts": pts,
        "leavingts": lts,
        "timetaken": final_time,
        "price" : res.price,
    }
    
    return jsonify({"billdata" : res_obj}), 201


@app.route('/api/viewspot')
@jwt_required()
def viewspot():
    spotid = request.args.get("id")
    res = Reservation.query.filter_by(spotid=spotid, status= 1).first()
    output_obj = {
        "spotid": res.spotid,
        "vehiclename": res.vehiclename,
        "vehiclenp": res.vehiclenp,
        "parkingts": res.parkingts
    }
    user = Users.query.filter_by(id = res.userid).first()
    return jsonify({"spotdata": output_obj, "username" : user.username}), 201
    

@app.route('/exportcsv')
@jwt_required()
def exportcsv():
    result = csv_report.delay(current_user.id)
    return {
        "id": result.id,
        "result": result.result
    }


@app.route('/api/csv_result/<id>')
def csv_result(id):
    result = AsyncResult(id)
    if result.ready():
        filename = result.result
        return send_from_directory('static', filename, as_attachment=True)
    else:
        return jsonify({"error": "CSV not ready"}), 202


@app.route('/api/send_mail')
def send_mail():
    result = monthly_report.delay()
    return {"message": result.result}


@app.route('/api/summary')
@jwt_required()
@cache.cached(timeout=300, key_prefix='summary_data')
def summary():
    if current_user.type == 'admin':
        reservations = Reservation.query.all()
        earning = 0
        lot_data = {}
        user_data = {}
        for i in reservations:
            if i.users.username in user_data:
                user_data[i.users.username] += 1
            else:
                user_data[i.users.username] = 1
            if i.price is not None:
                earning += i.price
                if i.address not in lot_data:
                    lot_data[i.address] = i.price
                else:
                    lot_data[i.address] += i.price

        profitable_lots = [{"label": address, "value": price} for address, price in lot_data.items()]
        profitable_lots.sort(key=lambda x: x['value'], reverse=True)
        profitable_lots = profitable_lots[:5]

        frequent_users = [{"label": username, "value": frequency} for username, frequency in user_data.items()]
        frequent_users.sort(key=lambda x: x['value'], reverse=True)
        frequent_users = frequent_users[:5]
        actusers = Users.query.filter_by(type = "user", status = 1).count()
        unausers = Users.query.filter_by(type = "user", status = 0).count()
        lots = Parkinglots.query.count()
        spots = Parkingspot.query.count()
        return jsonify({
            "username": current_user.username,
            "role": "admin",
            "lots": lots,
            "spots": spots,
            "actusers": actusers,
            "unausers": unausers,
            "earning": earning,
            "profitable_lots": profitable_lots,
            "frequent_users": frequent_users
        })

    else:
        reservations = Reservation.query.filter_by(userid = current_user.id).all()
        money_spent = 0
        activeres = 0
        expiredres = 0
        res_data = []

        for i in reservations:
            if i.price is not None:
                money_spent += i.price
                res_data.append({"label": i.address, "value": i.price, "date": i.parkingts.strftime("%Y-%m-%d %H:%M")})
            if i.status:
                activeres += 1
            else:
                expiredres += 1
        
        return jsonify({
            "username": current_user.username,
            "role": "user",
            "money_spent": round(money_spent, 2),
            "activeres": activeres,
            "expiredres": expiredres,
            "res_data": res_data
        })

    
        



