from .database import db

class Users(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(), unique = True, nullable = False)
    username = db.Column(db.String(), unique = True, nullable = False)
    password = db.Column(db.String(), nullable = False)
    phone_no = db.Column(db.String(), unique = True, nullable = False)
    type = db.Column(db.String(), nullable = False, default = 'user')  
    status = db.Column(db.Boolean, nullable = False)
    reservation = db.relationship('Reservation', backref = 'users', lazy = True)

class Parkinglots(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    cityname = db.Column(db.String(), nullable = False)
    address = db.Column(db.String(), unique = True, nullable = False)
    pincode = db.Column(db.String(), nullable = False)
    maxspots = db.Column(db.Integer, nullable = False)
    priceperhour = db.Column(db.Integer, nullable = False)
    status = db.Column(db.Boolean, nullable = False)
    parkingspot = db.relationship('Parkingspot', backref = 'parkinglots', lazy = True)

class Parkingspot(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    lotid = db.Column(db.Integer, db.ForeignKey('parkinglots.id'), nullable = False)
    status = db.Column(db.Boolean, nullable = False)
    reservation = db.relationship('Reservation', backref = 'parkingspot', lazy = True)

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    spotid = db.Column(db.Integer, db.ForeignKey('parkingspot.id'), nullable = False)
    userid = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)
    parkingts = db.Column(db.DateTime, nullable = False)
    leavingts = db.Column(db.DateTime)
    vehiclename = db.Column(db.String(), nullable = False)
    vehiclenp = db.Column(db.String(), nullable = False)
    status = db.Column(db.Boolean, nullable = False)
