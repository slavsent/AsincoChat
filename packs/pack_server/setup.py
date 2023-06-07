from setuptools import setup, find_packages

setup(name='sents_server_chat',
      version='1.0',
      description='Server packet',
      packages=find_packages(),  # ,Будем искать пакеты тут(включаем авто поиск пакетов)
      author_email='ricar@mail.ru',
      author='Slav Senteryov',
      install_requeres=['PyQt5', 'sqlalchemy', 'pycruptodome', 'pycryptodomex']
      # зависимости которые нужно до установить
      )
