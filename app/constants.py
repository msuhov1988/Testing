from datetime import date
from enum import Enum
import json


# sqlite3 не поддерживает тип даты и времени - поэтому даты будут сохранены, как кол-во дней от основания
DATE_BASEMENT = date(2000, 1, 1)

DB_SERVER_HOST = 'localhost'
DB_SERVER_PORT = 8866
DB_META_COMMAND = ["meta"]


# типы заявок для html таблицы - данные имена должны быть определены и на клиентской стороне
class NamesForTable(Enum):
    loaded = "Загруженных заявок"
    doubles = "Дубли"
    for_creation = "На создание"
    for_expand = "На расширение"
    handle_over = "Обработка завершена"
    returned = "Возвращена на уточнение"
    sent_for_handle = "Отправлена в обработку"
    packages = "Пакетов"
    users = "Пользователей"
