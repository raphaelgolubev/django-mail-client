import re
from datetime import datetime


def extract_datetime(from_str: str):
    """ Получает дату и время из строки """
    if from_str:
        date_pattern = r'\w{3}, \d{1,2} \w{3} \d{4} \d{2}:\d{2}:\d{2} [+-]\d{4}'
        matches = re.findall(date_pattern, from_str)
        date_objects = [datetime.strptime(match, "%a, %d %b %Y %H:%M:%S %z") for match in matches]
        if date_objects:
            return date_objects[0].strftime("%d %B %Y в %H:%M")
    return from_str


def truncate_text(text, max_length):
    """ Обрезает текст до `max_length` символов """
    if len(text) > max_length:
        return text[:max_length - 3] + "..."
    return text


def reduce_spaces(text):
    """ Сокращает все возможные пробелы до одного """
    return re.sub(r'\s+', ' ', text).strip() 