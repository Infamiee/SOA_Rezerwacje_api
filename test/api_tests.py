from app import db, Reservation
import unittest
from random import randint, uniform
from datetime import datetime, timedelta
import requests

URL = "http://127.0.0.1:5000/"


class Get_all_reservations_test ( unittest.TestCase ):
    url = URL + "reservation/all"

    def setUp(self) -> None:
        db.drop_all ()
        db.create_all ()
        for _ in range ( 10 ):
            x = Reservation ( user_id=randint ( 1, 20 ), vehicle_id=randint ( 1, 20 ),
                              cost=round ( uniform ( 10, 50 ), 2 ),
                              start_date=datetime.now (),
                              end_date=datetime.utcnow () + timedelta ( days=randint ( 1, 10 ) ) )

            db.session.add ( x )
        db.session.commit ()

    def tearDown(self) -> None:
        db.drop_all ()

    def test_get_all(self):
        resp = requests.get ( self.url )
        self.assertEqual ( resp.status_code, 200 )




class Get_by_id_test ( unittest.TestCase ):
    url = URL + "reservation/"

    def setUp(self) -> None:
        db.drop_all ()
        db.create_all ()
        for _ in range ( 10 ):
            x = Reservation ( user_id=randint ( 1, 20 ), vehicle_id=randint ( 1, 20 ),
                              cost=round ( uniform ( 10, 50 ), 2 ),
                              start_date=datetime.now (),
                              end_date=datetime.utcnow () + timedelta ( days=randint ( 1, 10 ) ) )
            db.session.add ( x )
        db.session.commit ()

    def tearDown(self) -> None:
        db.drop_all ()

    def test_correct_id(self):
        resp = [requests.get ( self.url + str ( i ) ) for i in range ( 1, 10 )]
        for r in resp:
            self.assertEqual ( r.status_code, 200 )

    def test_data_type_correction(self):
        resp = [requests.get ( self.url + str ( i ) ) for i in range ( 1, 10 )]
        for r in resp:
            data = r.json () ["reservations"]
            print ( data )
            self.assertEqual ( type ( data ["cost"] ), float )
            try:
                datetime.fromtimestamp ( data ["end_date"] )
            except:
                self.fail ( "wrong type" )
            try:
                datetime.fromtimestamp ( data ["start_date"] )
            except:
                self.fail ( "wrong type" )
            self.assertEqual ( type ( data ["id"] ), int )
            self.assertEqual ( type ( data ["user_id"] ), int )
            self.assertEqual ( type ( data ["vehicle_id"] ), int )

    def test_incorrect_id(self):
        resp = [requests.get ( self.url + str ( i ) ) for i in range ( 20, 30 )]
        for r in resp:
            self.assertEqual ( r.status_code, 404 )


class Add_reservation_test ( unittest.TestCase ):
    url = URL + "reservation"

    def setUp(self) -> None:
        db.create_all ()

    def tearDown(self) -> None:
        db.drop_all ()

    def test_good_body(self):
        cost = 12.12
        start_date =datetime.timestamp ( datetime.utcnow() )
        end_date = datetime.timestamp ( datetime.utcnow () + timedelta ( days=3 ) )
        user_id = 1
        vehicle_id = 1
        body = {
            'cost': cost,
            'start_date': start_date ,
            'end_date': end_date ,
            'user_id': user_id,
            'vehicle_id': vehicle_id
        }
        resp = requests.post ( self.url, json=body )
        self.assertEqual ( resp.status_code, 202 )
        resp = requests.get(URL+"reservation/all")
        data = resp.json()

        data = data["reservations"][0]
        self.assertEqual(data['cost'],cost)
        self.assertEqual(datetime.fromtimestamp(data["end_date"]),datetime.fromtimestamp(end_date))
        self.assertEqual(datetime.fromtimestamp(data["start_date"]),datetime.fromtimestamp(start_date))
        self.assertEqual(data["user_id"],user_id)
        self.assertEqual(data["vehicle_id"],vehicle_id)


    def test_bad_body(self):
        cost = "12.12"
        start_date =datetime.timestamp ( datetime.utcnow() )
        end_date = datetime.timestamp ( datetime.utcnow () + timedelta ( days=3 ) )
        user_id = 1
        vehicle_id = 1
        body = {
            'cost': cost,
            'start_date': start_date ,
            'end_date': end_date ,
            'user_id': user_id,
            'vehicle_id': vehicle_id
        }
        resp = requests.post ( self.url, json=body )
        self.assertEqual ( resp.status_code, 400)




if __name__ == '__main__':
    unittest.main ()
