import subprocess
from start_clients import start_clients

process = []

while True:
    action = input(
        'Выберите действие: q - выход , s - запустить сервер и клиенты, x - закрыть все окна, c - запустить клиенты:')
    if action == 'q':
        break
    elif action == 'c':
        num_clients = input('Введите сколько нужно запустить клиентов, если не число то 0: ')
        try:
            num_clients = int(num_clients)
        except ValueError:
            num_clients = 0
        start_clients(num_clients)
    elif action == 's':
        clients_count = int(input('Введите количество тестовых клиентов для запуска: '))
        # Запускаем сервер!
        process.append(subprocess.Popen('python server.py', creationflags=subprocess.CREATE_NEW_CONSOLE))
        # Запускаем клиентов:
        for i in range(clients_count):
            process.append(subprocess.Popen(f'python client.py', creationflags=subprocess.CREATE_NEW_CONSOLE))
    elif action == 'x':
        while process:
            process.pop().kill()
