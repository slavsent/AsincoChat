import unittest
import datetime
from server_utilit import create_msg_to_client


class TestServer(unittest.TestCase):

    def test_create_msg_to_client_resp(self):
        now_time = datetime.datetime.now().timestamp()
        res_create_msg_server = {
            'action': 'presence',
            'time': now_time,
            'encoding': 'utf-8',
            'message': 'hi server',
            'user': {
                "account_name": "Guest",
                "status": "I ok!"
            }
        }
        res_create_msg_client = {
            "response": 200,
            "message": f"Привет клиент: Guest",
            'time': now_time,
        }
        self.assertEqual(create_msg_to_client(res_create_msg_server), res_create_msg_client)

    def test_create_msg_to_client_err(self):
        now_time = datetime.datetime.now().timestamp()
        res_create_msg_server = {
            "message": 'Error',
            "time": 'Error'
        }
        res_create_msg_client = {
            "response": 400,
            "message": "Bad Request",
            'time': now_time,
        }
        self.assertEqual(create_msg_to_client(res_create_msg_server), res_create_msg_client)

    def test_create_msg_to_client_other(self):
        now_time = datetime.datetime.now().timestamp()
        res_create_msg_server = {
            'action': 'action',
            'time': now_time,
            'encoding': 'utf-8',
            'message': 'hi server',
            'user': {
                "account_name": "Guest",
                "status": "I ok!"
            }
        }
        res_create_msg_client = {
            "response": 200,
            "message": "Wait action",
            'time': now_time,
        }
        self.assertEqual(create_msg_to_client(res_create_msg_server), res_create_msg_client)


if __name__ == '__main__':
    unittest.main()
