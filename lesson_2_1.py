import csv
import re


def get_data():
    os_prod_list = []
    os_name_list = []
    os_code_list = []
    os_type_list = []
    main_data = []

    num_file = 1
    while True:
        try:
            with open(f'info_{num_file}.txt') as file_data:
                data = file_data.read()

                os_prod_reg = re.compile(r'Изготовитель системы:\s*\S*')
                os_prod_list.append(os_prod_reg.findall(data)[0].split()[2])

                os_name_reg = re.compile(r'Название ОС:.*')
                os_name_list.append(" ".join(os_name_reg.findall(data)[0].split()[2::]))

                os_code_reg = re.compile(r'Код продукта:\s*\S*')
                os_code_list.append(os_code_reg.findall(data)[0].split()[2])

                os_type_reg = re.compile(r'Тип системы:.*')
                os_type_list.append(" ".join(os_type_reg.findall(data)[0].split()[2::]))
        except FileNotFoundError:
            break
        else:
            num_file += 1

    headers = ['Изготовитель системы', 'Название ОС', 'Код продукта', 'Тип системы']
    main_data.append(headers)

    for i in range(0, num_file-1):
        row_data = []
        row_data.append(os_prod_list[i])
        row_data.append(os_name_list[i])
        row_data.append(os_code_list[i])
        row_data.append(os_type_list[i])
        main_data.append(row_data)
    return main_data


def write_to_csv(out_file):

    data = get_data()
    with open(out_file, 'w', encoding='utf-8') as file:
        file_writer = csv.writer(file, quoting=csv.QUOTE_NONNUMERIC)
        for row in data:
            file_writer.writerow(row)


if __name__ == '__main__':
    print(get_data())

    write_to_csv('data_report.csv')

    with open('data_report.csv', 'r', encoding='utf-8') as f_n:
        print(f_n.read())
