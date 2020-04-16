from datetime import datetime, timedelta
from data_parser import get_dates, get_beetween
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask import request
from flask_selfdoc import Autodoc

from activemq_connector import connector

app = Flask(__name__)
app.config.from_pyfile("config.cfg")
db = SQLAlchemy(app)
auto = Autodoc(app)
mq_conn = connector()

import json
import pypandoc
app = Flask ( __name__ )
app.config.from_pyfile ( "config.cfg" )
db = SQLAlchemy ( app )
auto = Autodoc ( app )



class Reservation(db.Model):
    reservation_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False)
    vehicle_id = db.Column(db.Integer, nullable=False)
    cost = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.DATETIME, nullable=False, default=datetime.timestamp(datetime.utcnow()))
    end_date = db.Column(db.DATETIME, nullable=False, default=datetime.timestamp(datetime.utcnow()))

    def to_dict(self):
        return {
            "id": self.reservation_id,
            "user_id": self.user_id,
            "vehicle_id": self.vehicle_id,
            "cost": self.cost,
            "start_date": datetime.timestamp(self.start_date),
            "end_date": datetime.timestamp(self.end_date)
        }


@auto.doc()
@app.route('/reservation/all', methods=["GET"])
def get_all_reservations():
    '''
    Get all reservations between dates
    params:
        after: timestamp (optional)
        before: timestamp (optional)
    '''
    params = request.args
    try:
        before, after = get_dates(params.to_dict())
    except Exception as e:
        return "Wrong data type", 400
    try:
        obj_data = Reservation.query.all()
        obj_data = get_beetween(obj_data, before=before, after=after)
        if not obj_data:
            return "Reservations not found", 404
        obj_dict = [x.to_dict() for x in obj_data]
        return jsonify({"reservations": obj_dict}), 200
    except Exception as e:

        return "Server problem", 500


@auto.doc()
@app.route('/reservation/<id>', methods=["GET"])
def get_reservation_by_id(id):
    '''Get reservation by id'''
    try:
        id = int(id)
    except Exception as e:
        return "wrong data form", 400
    try:
        x = Reservation.query.filter_by(reservation_id=id).first()
    except Exception as e:

        return "Server problem", 500
    if not x:
        return "Reservation not found", 404
    return jsonify({"reservations": x.to_dict()}), 200


@auto.doc()
@app.route('/reservation', methods=["POST"])
def add_reservation():
    '''     Add reservation and send payment details to activemq
            Body data:
            {
            "vehicle_id":INT,
            "user_id":INT,
            "start_date":TIMESTAMP,
            "end_date":TIMESTAMP,
            "cost": FLOAT
            }
    '''
    body = request.json
    if not body or not set(body.keys()) == {"vehicle_id", "user_id", "start_date", "end_date", "cost"}:
        return "wrong data form", 400
    try:

        vehicle_id = body['vehicle_id']
        user_id = body['user_id']
        cost = body["cost"]
        if not (type(vehicle_id) == int and type(user_id) == int and type(cost) == float):
            return "wrong data form", 400
        end_date = datetime.fromtimestamp(body['end_date'])
        start_date = datetime.fromtimestamp(body['start_date'])
        reservation = Reservation(vehicle_id=vehicle_id, user_id=user_id,
                                  end_date=end_date, start_date=start_date, cost=cost)
        try:
            pay_det = {"user_id": user_id,
                       "reservation_id": reservation.reservation_id,
                       "cost": cost}
            mq_conn.details_to_queue(pay_det)
        except:
            return "couldnt send payment", 500
        db.session.add(reservation)
        db.session.commit()

        return "OK", 202
    except Exception as e:

        return "Server problem", 500


@app.route("/reservation/user/<user_id>")
@auto.doc()
def get_reservations_by_user_id(user_id):
    '''
    Get all user reservations between dates
    params:
        after: timestamp (optional)
        before: timestamp (optional)
    '''
    try:
        user_id = int(user_id)
    except:
        return "wrong data form", 400

    params = request.args
    try:
        before, after = get_dates(params.to_dict())
    except Exception as e:
        return "Wrong data type", 400
    try:
        reservations = Reservation.query.filter_by(user_id=user_id).all()
        reservations = get_beetween(reservations, before=before, after=after)
        res_dict = [x.to_dict() for x in reservations]
        return jsonify({"reservations": res_dict}), 200
    except:
        return "Server problem", 500


@app.route("/reservation/payment/<reservation_id>")
@auto.doc()
def get_payments_details(reservation_id):
    '''Get reservation paymment details'''
    try:
        reservation_id = int(reservation_id)

    except:
        return "wrong data form", 400

    try:
        details = Reservation.query.filter_by(reservation_id=reservation_id).first()
    except:
        return "Server problem", 500
    if details:
        ret = {
            "cost": details.cost,
            "user_id": details.user_id,
            "reservation_id": details.reservation_id

        }

        return ret, 200
    return "Payment not found", 404


@app.route('/')
def documentation():
    return auto.html()


if __name__ == '__main__':
    app.run(debug=True)
