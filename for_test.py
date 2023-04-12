from collections import deque


def num_diapason(number):
    """
 Список диапазона числа от отрицательного значения до самого числа
 :param number: число
 :return: список чисел
    """
    try:
        num_int = int(number)
    except ValueError:
        return 'Вы ввели не число'
    else:
        res = deque()
        res.append(0)
        for i in range(1, num_int + 1):
            res.append(i)
            res.appendleft(i * -1)
        return list(res)


def num_rules(number):
    """
 Нахождение чисел кратных 5, 10, 15, но не 30
    :param number: число
 :return: True or False
    """
    try:
        num_int = int(number)
    except ValueError:
        return 'Вы ввели не число'
    else:
        if (num_int % 30 != 0) and (num_int % 5 == 0 or num_int % 10 == 0 or num_int % 15 == 0):
            return True
        else:
            return False


def num_float_one(number):
    """
 нахождение первой цифры после точки в вещественном числе
 :param number: число
 :return: первая цифра или нет
    """
    try:
        num_float = float(number)
    except ValueError:
        return 'Вы ввели не число или дробь введена не через .'
    else:
        if '.' in str(number):
            # еще вариант return number.split('.')[1][0]
            # еще вариант return int(num_float * 10) - int(num_float) * 10
            return int(num_float * 10 % 10)
        else:
            return 'Нет'



if __name__ == '__main__':
    num = input('Введите число: ')
    print(num_diapason(num))

    num = input('Введите число: ')
    print(num_rules(num))

    num = input('Введите число: ')
    print(num_float_one(num))