from setuptools import setup, find_packages

setup(name='sents_client_chat',
      version='1.0',
      description='Client packet',
      packages=find_packages(),  # ,Будем искать пакеты тут(включаем авто поиск пакетов)
      author_email='ricar@mail.ru',
      author='Slav Senteryov',
      install_requeres=['PyQt5', 'sqlalchemy', 'pycruptodome', 'pycryptodomex']
      ##зависимости которые нужно до установить
      )
