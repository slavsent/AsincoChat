import json
import datetime


def write_order_to_json(item='', quantity=0, price=0, buyer='', date=str(datetime.datetime.now())):

    with open('orders.json', 'r', encoding='utf-8') as file_out:
        data = json.load(file_out)

    with open('orders.json', 'w', encoding='utf-8') as file_in:
        orders_list = data['orders']
        order_info = {'item': item, 'quantity': quantity, 'price': price, 'buyer': buyer, 'date': date}
        orders_list.append(order_info)
        json.dump(data, file_in, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    write_order_to_json('printer', 1, 23.5, 'takscom', '24/01/23')
    write_order_to_json('сканер', 3, 40.5, 'Ростелеком', '24/01/23')
    write_order_to_json('тонер', 2, 5.2, 'Ростелеком')

    with open('orders.json', 'r', encoding='utf-8') as f_n:
        print(f_n.read())
