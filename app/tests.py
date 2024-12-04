"""
Модуль для тестирования
Запускать через терминал: python manage.py test
Для перед запуском тестов происходит запуск сервера ДБ в отдельном потоке
Не запускать тесты при работающем сервере приложений
"""


from threading import Thread
from queue import Queue
import os.path
import sys
import json
from django.test import TestCase, Client
from django.urls import reverse


def run_server():
    """Функция запуска сервера ДБ в отдельном потоке для тестирования"""
    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.insert(0, parent_dir)
    from support_initializer import run_socketserver

    queue = Queue()
    thread = Thread(target=run_socketserver, args=(queue,))
    thread.daemon = True
    thread.start()
    error = queue.get()
    if error is not None:
        print(error)
        input("Приложение закрыто, нажмите любую клавишу для выхода: ")
        sys.exit()


run_server()


class SomeTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_meta_view(self):
        url = reverse('meta')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertEqual(data[0], "2023-05-17")
        self.assertEqual(data[1], "2023-08-22")
        self.assertEqual(data[2][0], 1016)
        self.assertEqual(data[2][1], 355)
        self.assertEqual(data[2][2], 577)
        self.assertEqual(data[2][3], 84)
        self.assertEqual(data[2][4], 961)
        self.assertEqual(data[2][5], 8)
        self.assertEqual(data[2][6], 41)
        self.assertEqual(data[2][7], 125)
        self.assertEqual(data[2][8], 21)

    def test_period_data_view(self):
        url = reverse('period_data')
        data = ["2023-05-17", "2023-08-22"]
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        answer = response.json()
        answer_data = answer[0]
        self.assertEqual(answer_data[0], 1016)
        self.assertEqual(answer_data[1], 355)
        self.assertEqual(answer_data[2], 577)
        self.assertEqual(answer_data[3], 84)
        self.assertEqual(answer_data[4], 961)
        self.assertEqual(answer_data[5], 8)
        self.assertEqual(answer_data[6], 41)
        self.assertEqual(answer_data[7], 125)
        self.assertEqual(answer_data[8], 21)
