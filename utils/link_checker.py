import json
import requests
import os
import re

# Абсолютный путь для данных
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")  # Папка data находится в основной директории проекта

# Функция для проверки статуса кода HTTP и получения конечного URL
def check_url_status(url):
    try:
        response = requests.get(url, timeout=10)
        if 399 < response.status_code < 600:
            return False, response.status_code, response.url
        return True, response.status_code, response.url
    except requests.exceptions.RequestException as e:
        return False, None, str(e)

# Функция для проверки всех ссылок
def check_links(data):
    issues = []

    for email in data['emails']:
        for content in email['content']:
            if content['type'] == 'link':
                url = content['expected']
                is_valid, status_code, final_url = check_url_status(url)

                if not is_valid:
                    issues.append({
                        'selector': content['selector'],
                        'url': url,
                        'status_code': status_code,
                        'final_url': final_url,
                        'error': 'Ошибка при запросе' if status_code is None else f'Статус код: {status_code}'
                    })

    return issues

# Запуск проверки
if __name__ == "__main__":
    # Путь к файлу actual_result.json
    actual_result_file = os.path.join(DATA_DIR, "actual_result.json")
    print(f"Путь к файлу: {actual_result_file}")  # Выводим путь для отладки

    # Загружаем данные из actual_result.json
    with open(actual_result_file, "r", encoding="utf-8") as file:
        actual_data = json.load(file)

    # Проверка ссылок
    issues = check_links(actual_data)

    if issues:
        print("Найдены проблемы с некоторыми ссылками:")
        for issue in issues:
            print(f"Селектор: {issue['selector']}")
            print(f"URL: {issue['url']}")
            print(f"Статус код: {issue['status_code']}")
            print(f"Конечный URL: {issue['final_url']}")
            print(f"Ошибка: {issue['error']}")
            print("-" * 30)
    else:
        print("Все ссылки работают корректно.")