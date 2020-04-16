from app import db,Reservation
from random import randint,uniform
from datetime import datetime,timedelta

def add_test_data(records=10):
    db.drop_all ()
    db.create_all ()
    for _ in range ( records ):
        x = Reservation ( user_id=randint ( 1, 20 ), vehicle_id=randint ( 1, 20 ),
                          cost=round ( uniform ( 10, 50 ), 2 ),
                          start_date=datetime.now ()-timedelta(days=randint(1,10)),
                          end_date=datetime.utcnow () + timedelta ( days=randint ( 1, 10 ) ) )
        db.session.add ( x )
    db.session.commit ()


if  __name__ == "__main__":
    add_test_data(records=20)