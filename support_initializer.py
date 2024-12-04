"""
Модуль содержит функции, которые должны выполниться до запуска приложения django
"""
import os.path
import socketserver
import json
from functools import lru_cache
from datetime import datetime, timedelta
from typing import List, Tuple, Union
from app.constants import DATE_BASEMENT, DB_SERVER_HOST, DB_SERVER_PORT, DB_META_COMMAND
from support_db_requests import DbRequests, db_communicate
from support_file_reader import read_data_from_file


def _first_insertion(cursor, schema: str, min_date: int, max_date: int, users: List[Tuple], requests_qnt: List[Tuple]):
    cursor.executescript(schema)
    cursor.execute(DbRequests.date_range_insert.value, (min_date, max_date))
    cursor.executemany(DbRequests.users_insert.value, users)
    cursor.executemany(DbRequests.requests_insert.value, requests_qnt)


def initialize_data() -> Union[Tuple[None, None], Tuple[None, str]]:
    """
    Чтение данных из файла, создание базы данных, запись данных
    :return: кортеж (результат = None, ошибка)
    """
    schema_path = os.path.join(os.path.dirname(__file__), "db_schema.sql")

    try:
        with open(schema_path, encoding='utf-8') as f:
            schema = f.read()
    except FileNotFoundError:
        return None, f"!_ОШИБКА СХЕМЫ БД - {schema_path} не существует"
    except UnicodeDecodeError:
        return None, f"!_ОШИБКА СХЕМЫ БД - {schema_path} неверный формат файла"
    print("Схема базы данных прочитана")

    data_from_file, file_error = read_data_from_file()
    if file_error is not None:
        return None, file_error
    min_date, max_date, users, requests_qnt = data_from_file
    print("Данные из исходного файла прочитаны")

    print("Запись данных в базу...")
    _, db_error = db_communicate(_first_insertion, commit=True, schema=schema,
                                 min_date=min_date, max_date=max_date, users=users, requests_qnt=requests_qnt)
    if db_error is not None:
        return None, db_error
    print("Данные записаны в базу")
    return None, None


def _get_meta(cursor) -> List:
    """
    Извлекает минимальную и максимальную даты из БД, а также суммарные данные по всем датам
    Выполняется один раз при создании сокет-сервера для взаимодействия с БД
    :param cursor:
    :return:
    """
    dates = cursor.execute(DbRequests.date_range_select.value).fetchone()
    min_date_int, max_date_int = dates
    min_date, max_date = DATE_BASEMENT + timedelta(days=min_date_int), DATE_BASEMENT + timedelta(days=max_date_int)
    min_date, max_date = min_date.strftime("%Y-%m-%d"), max_date.strftime("%Y-%m-%d")

    quantities = list(cursor.execute(DbRequests.requests_select.value, (min_date_int, max_date_int)).fetchone())
    users = cursor.execute(DbRequests.user_select.value, (min_date_int, max_date_int)).fetchone()
    quantities.extend(users)
    return [min_date, max_date, quantities]


def _request_period_data(cursor, min_date: str, max_date: str):
    min_dt = datetime.strptime(min_date, "%Y-%m-%d").date()
    max_dt = datetime.strptime(max_date, "%Y-%m-%d").date()
    min_int, max_int = (min_dt - DATE_BASEMENT).days, (max_dt - DATE_BASEMENT).days,
    quantities = list(cursor.execute(DbRequests.requests_select.value, (min_int, max_int)).fetchone())
    users = cursor.execute(DbRequests.user_select.value, (min_int, max_int)).fetchone()
    quantities.extend(users)
    return quantities


# lru_cache - потокобезопасный декоратор
@lru_cache(maxsize=100)
def _get_period_data(min_date: str, max_date: str):
    """
    Возвращает суммированные за период данные
    Кэширует результаты с помощью lru_cache
    :param min_date: строка-дата начала периода
    :param max_date: строка-дата конца периода
    :return:
    """
    period_data, db_error = db_communicate(_request_period_data, commit=False, min_date=min_date, max_date=max_date)
    if db_error is not None:
        return json.dumps([None, db_error]).encode(encoding="utf-8")
    else:
        return json.dumps([period_data, None]).encode(encoding="utf-8")


def _socketserver_factory(meta_data: bytes):
    """
    фабрика для создания сокет-сервера, имеющего готовые данные в атрибуте класса
    :param meta_data:
    :return:
    """
    class DataBaseHandler(socketserver.BaseRequestHandler):
        meta = meta_data

        def handle(self):
            length = self.request.recv(4)
            length, read, chunks = int.from_bytes(length, byteorder="little"), 0, []
            while read < length:
                chunk = self.request.recv(1024).strip()
                chunks.append(chunk)
                read += len(chunk)
            data = json.loads(b"".join(chunks))
            if data == DB_META_COMMAND:
                answer = DataBaseHandler.meta
            else:
                min_date, max_date = data
                answer = _get_period_data(min_date=min_date, max_date=max_date)
            self.request.send(len(answer).to_bytes(4, byteorder="little"))
            self.request.sendall(answer)

    return DataBaseHandler


def run_socketserver(queue):
    """
    Запуск сервера для централизованного взаимодействия с базой данных
    Также осуществляет кэширование данных, см. _get_period_data
    :param queue: межпоточная или межпроцессная очередь для сигнализации о возникших ошибках при запуске
    :return:
    """
    meta_data, db_error = db_communicate(_get_meta, commit=False)
    if db_error is not None:
        queue.put(db_error)
    else:
        json_meta = json.dumps(meta_data).encode(encoding="utf-8")
        handler_class = _socketserver_factory(meta_data=json_meta)
        queue.put(None)
        print("Сервер для взаимодействия с базой данных запущен")
        with socketserver.ThreadingTCPServer((DB_SERVER_HOST, DB_SERVER_PORT), handler_class) as server:
            server.serve_forever()
