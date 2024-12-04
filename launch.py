"""
Модуль для запуска подготовительных функций и самого django-приложения
Точка входа для проекта
"""

from multiprocessing import Process, Queue
import subprocess
import sys
from support_initializer import initialize_data, run_socketserver


def preparatory_work():
    _, error = initialize_data()
    if error is not None:
        print(error)
        input("Приложение закрыто, нажмите любую клавишу для выхода: ")
        sys.exit()

    queue = Queue()
    process = Process(target=run_socketserver, args=(queue,))
    process.daemon = True
    process.start()
    error = queue.get()
    if error is not None:
        print(error)
        input("Приложение закрыто, нажмите любую клавишу для выхода: ")
        sys.exit()


if __name__ == "__main__":
    preparatory_work()
    subprocess.run([sys.executable, 'manage.py', 'runserver'])
