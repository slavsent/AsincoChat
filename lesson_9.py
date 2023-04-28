import socket
from ipaddress import ip_address
from subprocess import Popen, PIPE
from tabulate import tabulate


def host_ping(host_list: list, timeout=500, requests=1):
    result_dict = {"Доступные узлы": [], "Недоступные узлы": [], "Недействительные узлы": []}

    for host in host_list:
        try:
            test_address = ip_address(host)
        except ValueError:
            pass

        try:
            test_address = ip_address(socket.gethostbyname(host))
        except Exception:
            result_dict["Недействительные узлы"].append(host)
            continue

        proc = Popen(f"ping {test_address} -w {timeout} -n {requests}", shell=False, stdout=PIPE)
        proc.wait()
        if proc.returncode == 0:
            result_dict['Доступные узлы'].append(host)
        else:
            result_dict['Недоступные узлы'].append(host)

    print(f'Доступные узлы: {", ".join(result_dict["Доступные узлы"])}')
    print(f'Недоступные узлы: {", ".join(result_dict["Недоступные узлы"])}')
    print(f'Недействительные узлы: {", ".join(result_dict["Недействительные узлы"])}')
    return result_dict


def host_range_ping():
    while True:
        range_pin = input('Введите IP адрес: ')
        if len(range_pin.split('.')) < 3:
            print(
                'Вы ввели не коректный адрес, адрес должен быть или 0.0.0.0 последний элемент с которго проверить'
                'или 0.0. если проверить с 0-го')
            continue
        else:
            if len(range_pin.split('.')) == 4:
                try:
                    top_el = int(range_pin.split('.')[3])
                except ValueError:
                    print('Вы ввели последний элемент не цисло, первоначальный будет 0')
                    top_el = 0
            else:
                top_el = 0
            end_el = input('Введите до каго значения проверить, но не боле 254, иначе будт 254: ')
            try:
                end_el = int(end_el)
            except ValueError:
                print('Вы ввели не цисло, диапозон будет до 254')
                end_el = 254
            if end_el < top_el:
                end_el = top_el
            host_list = []
            [host_list.append((".".join(range_pin.split(".")[:3:]) + '.' + str(x))) for x in range(top_el, end_el+1)]
            return host_ping(host_list)


def host_range_ping_tab():
    result_dict = host_range_ping()
    print(tabulate(result_dict, headers='keys', tablefmt="pipe", stralign="center"))


if __name__ == "__main__":
    list_ip = ['127.0.0.1', '127.0.0.2', 'google.com', '192.168.142.200']
    list_ip1 = ['127.0.0.1', '127.0.0.2', 'goog', '192.168.142.200']
    host_ping(list_ip)
    host_ping(list_ip1)
    host_range_ping()
    host_range_ping_tab()
