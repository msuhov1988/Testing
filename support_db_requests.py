"""
Модуль содержит перечисления колонок таблиц базы данных, а также sql запросы и функцию взаимодействия.
Единственная точка взаимодействия с базой данных.
"""


from enum import Enum
import os.path
import sqlite3
from typing import Callable, Union, Any, Tuple


_DB_PATH = os.path.join(os.path.dirname(__file__), "db.sqlite3")


class RangeCols(Enum):
    min_dt = "min_date"
    max_dt = "max_date"


class UserCols(Enum):
    dt = "date"
    fio = "user_fio"


class RequestsCols(Enum):
    dt = "date"
    loaded = "loaded"
    doubles = "doubles"
    for_creation = "for_creation"
    for_expand = "for_expand"
    handle_over = "handle_over"
    returned = "returned"
    sent_for_handle = "sent_for_handle"
    packages = "packages"


class DbRequests(Enum):
    date_range_insert = f"INSERT INTO date_range({RangeCols.min_dt.value}, {RangeCols.max_dt.value}) VALUES(?, ?)"

    users_insert = f"INSERT INTO users({UserCols.dt.value}, {UserCols.fio.value}) VALUES(?, ?)"

    requests_insert = f"""INSERT INTO requests({RequestsCols.dt.value},
                                               {RequestsCols.loaded.value},
                                               {RequestsCols.doubles.value},
                                               {RequestsCols.for_creation.value},
                                               {RequestsCols.for_expand.value},
                                               {RequestsCols.handle_over.value},
                                               {RequestsCols.returned.value},
                                               {RequestsCols.sent_for_handle.value},
                                               {RequestsCols.packages.value})
                           VALUES(?, ?, ?, ?, ?,  ?, ?, ?, ?)
                       """

    date_range_select = f"""SELECT {RangeCols.min_dt.value}, {RangeCols.max_dt.value} FROM date_range"""

    user_select = f"""SELECT COUNT(DISTINCT {UserCols.fio.value})
                      FROM users
                      WHERE {UserCols.dt.value} >= ? and {UserCols.dt.value} <= ?"""

    requests_select = f"""SELECT SUM({RequestsCols.loaded.value}),
                                 SUM({RequestsCols.doubles.value}),
                                 SUM({RequestsCols.for_creation.value}),
                                 SUM({RequestsCols.for_expand.value}),
                                 SUM({RequestsCols.handle_over.value}),
                                 SUM({RequestsCols.returned.value}),
                                 SUM({RequestsCols.sent_for_handle.value}),
                                 SUM({RequestsCols.packages.value})
                           FROM requests
                           WHERE {RequestsCols.dt.value} >= ? and {RequestsCols.dt.value} <= ?
                        """


def db_communicate(function: Callable, commit: bool, **kwargs) -> Union[Tuple[Any, None], Tuple[None, str]]:
    """
    Функция для взаимодействия с базой данных
    :param function: функция, принимающая cursor и **kwargs, осуществляющая манипуляции с данными
    :param commit: false | true - определяет, будут ли изменения сохраняться в базе данных
    :param kwargs: именованные аргументы, передаваемые в function
    :return: Union[Tuple[Any, None], Tuple[None, str]] - кортеж (результат, ошибка)
    """
    conn = None
    try:
        conn = sqlite3.connect(_DB_PATH)
        cursor = conn.cursor()
        result = function(cursor, **kwargs)
        if commit:
            conn.commit()
        return result, None
    except (sqlite3.OperationalError, sqlite3.DataError) as err:
        return None, f"!_ОШИБКА БАЗЫ ДАННЫХ - {err}"
    finally:
        if conn is not None:
            conn.close()
