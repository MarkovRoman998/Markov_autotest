import json
import requests
import os
import re
from bs4 import BeautifulSoup
from difflib import unified_diff

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EMAILS_DIR = os.path.join(BASE_DIR, "Emails")
DATA_DIR = os.path.join(BASE_DIR, "data")

class BasePage:
    def __init__(self, email_filename):
        self.email_filename = email_filename
        self.email_path = os.path.join(EMAILS_DIR, email_filename)

    def load_html(self):
        if not os.path.exists(self.email_path):
            print(f"❌ Файл {self.email_path} не найден!")
            return None
        try:
            with open(self.email_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"❌ Ошибка при чтении {self.email_path}: {e}")
            return None

class EmailPage(BasePage):
    def parse_html(self, html):
        if html:
            return BeautifulSoup(html, "html.parser")
        else:
            return None

    def extract_email_data(self, soup):
        content = []
        link_pattern = re.compile(r'^(?:[hbf]-link-\d+|f-social-link-\d+)$')
        img_pattern = re.compile(r'^[hbf]-img-\d+$')
        text_pattern = re.compile(r'^[hbf]-text-\d+$')

        for link in soup.find_all("a", id=link_pattern):
            content.append({
                "selector": link.get("id", "link_no_id"),
                "type": "link",
                "expected": link.get("href")
            })

        for img in soup.find_all("img", id=img_pattern):
            content.append({
                "selector": img.get("id", "img_no_id"),
                "type": "image",
                "expected": img.get("src")
            })

        for text_element in soup.find_all(id=text_pattern):
            content.append({
                "selector": text_element.get("id", "text_no_id"),
                "type": "text",
                "expected": text_element.get_text(strip=True)
            })

        return {
            "emails": [{
                "id": "1",
                "name": os.path.splitext(self.email_filename)[0],
                "language": "ru",
                "document": self.email_path,
                "content": content
            }]
        }

class DataSaver:
    def __init__(self):
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)

    def save_to_json(self, data, filename="actual_result.json"):
        file_path = os.path.join(DATA_DIR, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

class EmailProcessor:
    def __init__(self, email_filename):
        self.email_page = EmailPage(email_filename)
        self.data_saver = DataSaver()

    def process_email(self):
        html_content = self.email_page.load_html()
        if html_content:
            soup = self.email_page.parse_html(html_content)
            if soup:
                email_data = self.email_page.extract_email_data(soup)
                self.data_saver.save_to_json(email_data)

def check_url_status(url):
    try:
        response = requests.get(url, timeout=10)
        if 399 < response.status_code < 600:
            return False, response.status_code, response.url
        return True, response.status_code, response.url
    except requests.exceptions.RequestException as e:
        return False, None, str(e)

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

def compare_json_files(actual_file, expected_file):
    with open(actual_file, "r", encoding="utf-8") as f1, open(expected_file, "r", encoding="utf-8") as f2:
        actual_data = json.load(f1)
        expected_data = json.load(f2)

    diff = unified_diff(
        json.dumps(actual_data, indent=4).splitlines(),
        json.dumps(expected_data, indent=4).splitlines(),
        fromfile='actual', tofile='expected'
    )
    return list(diff)