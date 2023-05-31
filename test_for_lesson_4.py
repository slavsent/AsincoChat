import unittest
import datetime
from for_test import num_diapason, num_rules, num_float_one
from server_utilit import create_msg_to_client
from client import create_msg_for_server


class TestFunctionForNum(unittest.TestCase):

    def test_num_diapason(self):
        self.assertEqual(num_diapason(3), [-3, -2, -1, 0, 1, 2, 3])

    def test_num_rules_true(self):
        self.assertEqual(num_rules(105), True)

    def test_num_rules_false(self):
        self.assertEqual(num_rules(90), False)

    def test_num_float_one(self):
        self.assertEqual(num_float_one(56.57), 5)


class TestClientServer(unittest.TestCase):

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
