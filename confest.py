import pytest
import os
import json
from utils.parser_2_0 import load_html
from utils.link_checker import check_url_status

# Фикстура для загрузки тестовых данных из JSON
@pytest.fixture(scope="module")
def actual_data():
    """Загружаем actual_result.json для использования в тестах."""
    data_file = os.path.join(os.path.dirname(__file__), 'data', 'actual_result.json')
    with open(data_file, 'r', encoding='utf-8') as f:
        return json.load(f)

@pytest.fixture(scope="module")
def expected_data():
    """Загружаем expected_result.json для использования в тестах."""
    data_file = os.path.join(os.path.dirname(__file__), 'data', 'expected_result.json')
    with open(data_file, 'r', encoding='utf-8') as f:
        return json.load(f)

# Фикстура для загрузки HTML из файла
@pytest.fixture(scope="module")
def html_content():
    """Загружаем содержимое HTML для тестов."""
    html_file = os.path.join(os.path.dirname(__file__), 'Emails', 'frozen_account_RU.html')
    return load_html(html_file)

# Фикстура для ссылки и проверки её статуса
@pytest.fixture()
def url_checker():
    """Фикстура для проверки ссылки с помощью requests."""
    return check_url_status

# Дополнительная фикстура для установки состояния, если это нужно
@pytest.fixture(scope="module", autouse=True)
def setup_module():
    """Запуск перед всеми тестами (например, настройка окружения или данных)."""
    print("\n[INFO] Setting up the test module...")
    yield
    print("\n[INFO] Teardown the test module...")
