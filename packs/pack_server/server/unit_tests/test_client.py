import unittest
import datetime
from client import create_msg_for_server


class TestClient(unittest.TestCase):

    def test_create_msg_for_server(self):
        msg = 'hi server'
        now_time = datetime.datetime.now().timestamp()
        res_create_msg_server = {
            'action': 'presence',
            'time': now_time,
            'encoding': 'utf-8',
            'message': msg,
            'user': {
                "account_name": "Guest",
                "status": "I ok!"
            }
        }
        self.assertEqual(create_msg_for_server(msg), res_create_msg_server)


if __name__ == '__main__':
    unittest.main()
