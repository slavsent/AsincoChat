import subprocess
import locale


# Задание 1
word_1 = 'разработка'
word_2 = 'сокет'
word_3 = 'декоратор'
print(f'type: {type(word_1)}, word: {word_1}')
print(f'type: {type(word_2)}, word: {word_2}')
print(f'type: {type(word_3)}, word: {word_3}')
word_1_unicode = '\u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0430'
word_2_unicode = '\u0441\u043e\u043a\u0435\u0442'
word_3_unicode = '\u0434\u0435\u043a\u043e\u0440\u0430\u0442\u043e\u0440'
print(f'type: {type(word_1_unicode)}, word: {word_1_unicode}')
print(f'type: {type(word_2_unicode)}, word: {word_2_unicode}')
print(f'type: {type(word_3_unicode)}, word: {word_3_unicode}')
# result
"""
type: <class 'str'>, word: разработка
type: <class 'str'>, word: сокет
type: <class 'str'>, word: декоратор
type: <class 'str'>, word: разработка
type: <class 'str'>, word: сокет
type: <class 'str'>, word: декоратор
"""

# Задание 2
bytes_w_1 = b'class'
bytes_w_2 = b'function'
bytes_w_3 = b'method'
print(f'type: {type(bytes_w_1)}, word: {bytes_w_1}, len: {len(bytes_w_1)}')
print(f'type: {type(bytes_w_2)}, word: {bytes_w_2}, len: {len(bytes_w_2)}')
print(f'type: {type(bytes_w_3)}, word: {bytes_w_3}, len: {len(bytes_w_3)}')
# result
"""
type: <class 'bytes'>, word: b'class', len: 5
type: <class 'bytes'>, word: b'function', len: 8
type: <class 'bytes'>, word: b'method', len: 6
"""

# Задание 3
bytes_w_1 = b'attribute'
#bytes_w_2 = b'класс'
#bytes_w_3 = b'функция'
bytes_w_4 = b'type'
print(f'type: {type(bytes_w_1)}, word: {bytes_w_1}, len: {len(bytes_w_1)}')
#print(f'type: {type(bytes_w_2)}, word: {bytes_w_2}, len: {len(bytes_w_2)}')
#print(f'type: {type(bytes_w_3)}, word: {bytes_w_3}, len: {len(bytes_w_3)}')
print(f'type: {type(bytes_w_4)}, word: {bytes_w_4}, len: {len(bytes_w_4)}')
# result
"""
Невозможно записать в байтовом типе слова на кириллице
SyntaxError: bytes can only contain ASCII literal characters
"""

# Задание 4
word_1 = 'разработка'
word_2 = 'администрирование'
word_3 = 'protocol'
word_4 = 'standard'
word_1_b = word_1.encode('utf-8')
word_2_b = word_2.encode('utf-8')
word_3_b = word_3.encode('utf-8')
word_4_b = word_4.encode('utf-8')
print(f'encode: {word_1_b}, decode: {word_1_b.decode("utf-8")}')
print(f'encode: {word_2_b}, decode: {word_2_b.decode("utf-8")}')
print(f'encode: {word_3_b}, decode: {word_3_b.decode("utf-8")}')
print(f'encode: {word_4_b}, decode: {word_4_b.decode("utf-8")}')
# result
"""
encode: b'\xd1\x80\xd0\xb0\xd0\xb7\xd1\x80\xd0\xb0\xd0\xb1\xd0\xbe\xd1\x82\xd0\xba\xd0\xb0', decode: разработка
encode: b'\xd0\xb0\xd0\xb4\xd0\xbc\xd0\xb8\xd0\xbd\xd0\xb8\xd1\x81\xd1\x82\xd1\x80\xd0\xb8\xd1\x80\xd0\xbe\xd0\xb2\xd0\xb0\xd0\xbd\xd0\xb8\xd0\xb5', decode: администрирование
encode: b'protocol', decode: protocol
encode: b'standard', decode: standard
"""

# Задание 5
args_1 = ['ping', 'yandex.ru']
args_2 = ['ping', 'youtube.com']
subproc_ping_1 = subprocess.Popen(args_1, stdout=subprocess.PIPE)
subproc_ping_2 = subprocess.Popen(args_2, stdout=subprocess.PIPE)
subproc_ping_3 = subprocess.Popen(args_1, stdout=subprocess.PIPE)
subproc_ping_4 = subprocess.Popen(args_2, stdout=subprocess.PIPE)

print('ping yandex.ru bytes')
for line in subproc_ping_1.stdout:
    print(f'bytes: {line}')
print('ping youtube.com bytes')
for line in subproc_ping_2.stdout:
    print(f'bytes: {line}')
print('ping yandex.ru decode')
for line in subproc_ping_3.stdout:
    line = line.decode('cp866')
    print(f'bytes: {line}')
print('ping youtube.com decode')
for line in subproc_ping_4.stdout:
    line = line.decode('cp866')
    print(f'bytes: {line}')
# result
"""
ping yandex.ru bytes
bytes: b'\r\n'
bytes: b'\x8e\xa1\xac\xa5\xad \xaf\xa0\xaa\xa5\xe2\xa0\xac\xa8 \xe1 yandex.ru [5.255.255.77] \xe1 32 \xa1\xa0\xa9\xe2\xa0\xac\xa8 \xa4\xa0\xad\xad\xeb\xe5:\r\n'
bytes: b'\x8e\xe2\xa2\xa5\xe2 \xae\xe2 5.255.255.77: \xe7\xa8\xe1\xab\xae \xa1\xa0\xa9\xe2=32 \xa2\xe0\xa5\xac\xef=7\xac\xe1 TTL=54\r\n'
bytes: b'\x8e\xe2\xa2\xa5\xe2 \xae\xe2 5.255.255.77: \xe7\xa8\xe1\xab\xae \xa1\xa0\xa9\xe2=32 \xa2\xe0\xa5\xac\xef=7\xac\xe1 TTL=54\r\n'
bytes: b'\x8e\xe2\xa2\xa5\xe2 \xae\xe2 5.255.255.77: \xe7\xa8\xe1\xab\xae \xa1\xa0\xa9\xe2=32 \xa2\xe0\xa5\xac\xef=12\xac\xe1 TTL=54\r\n'
bytes: b'\x8e\xe2\xa2\xa5\xe2 \xae\xe2 5.255.255.77: \xe7\xa8\xe1\xab\xae \xa1\xa0\xa9\xe2=32 \xa2\xe0\xa5\xac\xef=12\xac\xe1 TTL=54\r\n'
bytes: b'\r\n'
bytes: b'\x91\xe2\xa0\xe2\xa8\xe1\xe2\xa8\xaa\xa0 Ping \xa4\xab\xef 5.255.255.77:\r\n'
bytes: b'    \x8f\xa0\xaa\xa5\xe2\xae\xa2: \xae\xe2\xaf\xe0\xa0\xa2\xab\xa5\xad\xae = 4, \xaf\xae\xab\xe3\xe7\xa5\xad\xae = 4, \xaf\xae\xe2\xa5\xe0\xef\xad\xae = 0\r\n'
bytes: b'    (0% \xaf\xae\xe2\xa5\xe0\xec)\r\n'
bytes: b'\x8f\xe0\xa8\xa1\xab\xa8\xa7\xa8\xe2\xa5\xab\xec\xad\xae\xa5 \xa2\xe0\xa5\xac\xef \xaf\xe0\xa8\xa5\xac\xa0-\xaf\xa5\xe0\xa5\xa4\xa0\xe7\xa8 \xa2 \xac\xe1:\r\n'
bytes: b'    \x8c\xa8\xad\xa8\xac\xa0\xab\xec\xad\xae\xa5 = 7\xac\xe1\xa5\xaa, \x8c\xa0\xaa\xe1\xa8\xac\xa0\xab\xec\xad\xae\xa5 = 12 \xac\xe1\xa5\xaa, \x91\xe0\xa5\xa4\xad\xa5\xa5 = 9 \xac\xe1\xa5\xaa\r\n'
ping youtube.com bytes
bytes: b'\r\n'
bytes: b'\x8e\xa1\xac\xa5\xad \xaf\xa0\xaa\xa5\xe2\xa0\xac\xa8 \xe1 youtube.com [142.250.150.93] \xe1 32 \xa1\xa0\xa9\xe2\xa0\xac\xa8 \xa4\xa0\xad\xad\xeb\xe5:\r\n'
bytes: b'\x8e\xe2\xa2\xa5\xe2 \xae\xe2 142.250.150.93: \xe7\xa8\xe1\xab\xae \xa1\xa0\xa9\xe2=32 \xa2\xe0\xa5\xac\xef=19\xac\xe1 TTL=60\r\n'
bytes: b'\x8e\xe2\xa2\xa5\xe2 \xae\xe2 142.250.150.93: \xe7\xa8\xe1\xab\xae \xa1\xa0\xa9\xe2=32 \xa2\xe0\xa5\xac\xef=19\xac\xe1 TTL=60\r\n'
bytes: b'\x8e\xe2\xa2\xa5\xe2 \xae\xe2 142.250.150.93: \xe7\xa8\xe1\xab\xae \xa1\xa0\xa9\xe2=32 \xa2\xe0\xa5\xac\xef=25\xac\xe1 TTL=60\r\n'
bytes: b'\x8e\xe2\xa2\xa5\xe2 \xae\xe2 142.250.150.93: \xe7\xa8\xe1\xab\xae \xa1\xa0\xa9\xe2=32 \xa2\xe0\xa5\xac\xef=24\xac\xe1 TTL=60\r\n'
bytes: b'\r\n'
bytes: b'\x91\xe2\xa0\xe2\xa8\xe1\xe2\xa8\xaa\xa0 Ping \xa4\xab\xef 142.250.150.93:\r\n'
bytes: b'    \x8f\xa0\xaa\xa5\xe2\xae\xa2: \xae\xe2\xaf\xe0\xa0\xa2\xab\xa5\xad\xae = 4, \xaf\xae\xab\xe3\xe7\xa5\xad\xae = 4, \xaf\xae\xe2\xa5\xe0\xef\xad\xae = 0\r\n'
bytes: b'    (0% \xaf\xae\xe2\xa5\xe0\xec)\r\n'
bytes: b'\x8f\xe0\xa8\xa1\xab\xa8\xa7\xa8\xe2\xa5\xab\xec\xad\xae\xa5 \xa2\xe0\xa5\xac\xef \xaf\xe0\xa8\xa5\xac\xa0-\xaf\xa5\xe0\xa5\xa4\xa0\xe7\xa8 \xa2 \xac\xe1:\r\n'
bytes: b'    \x8c\xa8\xad\xa8\xac\xa0\xab\xec\xad\xae\xa5 = 19\xac\xe1\xa5\xaa, \x8c\xa0\xaa\xe1\xa8\xac\xa0\xab\xec\xad\xae\xa5 = 25 \xac\xe1\xa5\xaa, \x91\xe0\xa5\xa4\xad\xa5\xa5 = 21 \xac\xe1\xa5\xaa\r\n'
ping yandex.ru decode
bytes: 

bytes: Обмен пакетами с yandex.ru [5.255.255.77] с 32 байтами данных:

bytes: Ответ от 5.255.255.77: число байт=32 время=7мс TTL=54

bytes: Ответ от 5.255.255.77: число байт=32 время=7мс TTL=54

bytes: Ответ от 5.255.255.77: число байт=32 время=12мс TTL=54

bytes: Ответ от 5.255.255.77: число байт=32 время=12мс TTL=54

bytes: 

bytes: Статистика Ping для 5.255.255.77:

bytes:     Пакетов: отправлено = 4, получено = 4, потеряно = 0

bytes:     (0% потерь)

bytes: Приблизительное время приема-передачи в мс:

bytes:     Минимальное = 7мсек, Максимальное = 12 мсек, Среднее = 9 мсек

ping youtube.com decode
bytes: 

bytes: Обмен пакетами с youtube.com [142.250.150.93] с 32 байтами данных:

bytes: Ответ от 142.250.150.93: число байт=32 время=19мс TTL=60

bytes: Ответ от 142.250.150.93: число байт=32 время=21мс TTL=60

bytes: Ответ от 142.250.150.93: число байт=32 время=23мс TTL=60

bytes: Ответ от 142.250.150.93: число байт=32 время=20мс TTL=60

bytes: 

bytes: Статистика Ping для 142.250.150.93:

bytes:     Пакетов: отправлено = 4, получено = 4, потеряно = 0

bytes:     (0% потерь)

bytes: Приблизительное время приема-передачи в мс:

bytes:     Минимальное = 19мсек, Максимальное = 23 мсек, Среднее = 20 мсек
"""

# Задание 5

def_coding = locale.getpreferredencoding()
print(f'кодировка по умолчанию: {def_coding}')

print('Открытие файла с кодировкой по умолчанию')
with open('test_file.txt') as file:
    for line_str in file:
        print(line_str, end='')

print('\n file open utf-8')
with open('test_file.txt', encoding='utf-8') as file:
    for line_str in file:
        print(line_str, end='')
# result
"""
кодировка по умолчанию: cp1251
Открытие файла с кодировкой по умолчанию
СЃРµС‚РµРІРѕРµ РїСЂРѕРіСЂР°РјРјРёСЂРѕРІР°РЅРёРµ
СЃРѕРєРµС‚
РґРµРєРѕСЂР°С‚РѕСЂ
 file open utf-8
сетевое программирование
сокет
декоратор
"""
