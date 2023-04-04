import yaml


def write_to_yaml(data_in):
    with open('my_file.yaml', 'w', encoding='utf-8') as file_in:
        yaml.dump(data_in, file_in, default_flow_style=False, allow_unicode=True, sort_keys=False
                  )


if __name__ == '__main__':

    my_data = {'items': ['computer', 'printer', 'keyboard', 'mouse', 'телефон'],
               'quantity': 4,
               'ptice': {'computer': '200€-1000€', 'printer': '100€-300€', 'keyboard': '5€-50€', 'mouse': '4€-7€',
                         'телефон': '44€-98€'}
               }

    write_to_yaml(my_data)

    with open("my_file.yaml", 'r', encoding='utf-8') as file_out:
        data_out = yaml.load(file_out, Loader=yaml.SafeLoader)

    print(my_data == data_out)

    DATA_IN = {'items': ['computer', 'printer', 'keyboard', 'mouse'],
               'items_quantity': 4,
               'items_ptice': {'computer': '200\u20ac-1000\u20ac',
                               'printer': '100\u20ac-300\u20ac',
                               'keyboard': '5\u20ac-50\u20ac',
                               'mouse': '4\u20ac-7\u20ac'}
               }
    write_to_yaml(DATA_IN)

    with open("my_file.yaml", 'r', encoding='utf-8') as file_out:
        data_out = yaml.load(file_out, Loader=yaml.SafeLoader)

    print(DATA_IN == data_out)
