import unittest
from for_test import num_diapason, num_rules, num_float_one


class TestFunctionForNum(unittest.TestCase):

    def test_num_diapason(self):
        self.assertEqual(num_diapason(3), [-3, -2, -1, 0, 1, 2, 3])

    def test_num_rules_true(self):
        self.assertEqual(num_rules(105), True)

    def test_num_rules_false(self):
        self.assertEqual(num_rules(90), False)

    def test_num_float_one(self):
        self.assertEqual(num_float_one(56.57), 5)


if __name__ == '__main__':
    unittest.main()
