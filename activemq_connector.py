import stomp
import json
class connector():

    def __init__(self,username=None,passcode=None):
        self.username = username
        self.password = passcode
        self.conn = stomp.Connection()
        self.conn.connect(username,passcode)

    def details_to_queue(self,details):
        try:
            if type(details) is dict:
                details = json.dumps(details)

            self.conn.send( body=details,destination='soa.payment.details')
        except Exception as e:
            raise e



