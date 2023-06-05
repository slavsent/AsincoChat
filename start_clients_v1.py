from subprocess import Popen, PIPE, CREATE_NEW_CONSOLE


def start_clients(number_clients=1):
    adr_serv = input('Введите адрес сервера: ')
    port_serv = input('Введите порт сервера: ')

    commands = []
    for el in range(number_clients):
        commands.append(f'python client_v1.py {adr_serv} {port_serv}')
    procs = [Popen(el, creationflags=CREATE_NEW_CONSOLE) for el in commands]
    for p in procs:
        p.wait()


if __name__ == "__main__":
    num_clients = input('Введите сколько нужно запустить клиентов, если не число то 0: ')
    try:
        num_clients = int(num_clients)
    except ValueError:
        num_clients = 0
    start_clients(num_clients)
