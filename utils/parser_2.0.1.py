import os
import json
import re
from bs4 import BeautifulSoup

class DataSaver:
    """
    Класс для сохранения данных в JSON.
    """
    def __init__(self):
        self.BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.DATA_DIR = os.path.join(self.BASE_DIR, "data")

        if not os.path.exists(self.DATA_DIR):
            os.makedirs(self.DATA_DIR)

    def save_to_json(self, data, filename="actual_result.json"):
        """
        Сохраняет данные в JSON файл.
        """
        file_path = os.path.join(self.DATA_DIR, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"✅ Данные сохранены в {file_path}")


class EmailProcessor:
    """
    Класс для обработки email-писем.
    """
    def __init__(self, email_filename):
        self.BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.EMAILS_DIR = os.path.join(self.BASE_DIR, "Emails")
        self.email_filename = email_filename
        self.data_saver = DataSaver()

    def load_html(self):
        """
        Загружает HTML-файл.
        """
        file_path = os.path.join(self.EMAILS_DIR, self.email_filename)
        if not os.path.exists(file_path):
            print(f"❌ Файл {self.email_filename} не найден!")
            return None
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"❌ Ошибка при чтении {self.email_filename}: {e}")
            return None

    def parse_html(self, html):
        """
        Преобразует HTML в объект BeautifulSoup.
        """
        return BeautifulSoup(html, "html.parser") if html else None

    def extract_email_data(self, soup):
        """
        Извлекает ссылки, изображения и текст из HTML.
        """
        content = []
        link_pattern = re.compile(r'^(?:[hbf]-link-\d+|f-social-link-\d+)$')
        img_pattern = re.compile(r'^[hbf]-img-\d+$')
        text_pattern = re.compile(r'^[hbf]-text-\d+$')

        # Извлекаем ссылки
        for link in soup.find_all("a", id=link_pattern):
            content.append({"selector": link.get("id"), "type": "link", "expected": link.get("href")})

        # Извлекаем изображения
        for img in soup.find_all("img", id=img_pattern):
            content.append({"selector": img.get("id"), "type": "image", "expected": img.get("src")})

        # Извлекаем текст
        for text_element in soup.find_all(id=text_pattern):
            content.append({"selector": text_element.get("id"), "type": "text", "expected": text_element.get_text(strip=True)})

        return {
            "emails": [{
                "id": "1",
                "name": os.path.splitext(self.email_filename)[0],
                "language": "ru",
                "document": os.path.join(self.EMAILS_DIR, self.email_filename),
                "content": content
            }]
        }

    def process_email(self):
        """
        Основной процесс обработки email: загрузка, парсинг, извлечение, сохранение.
        """
        html_content = self.load_html()
        if html_content:
            soup = self.parse_html(html_content)
            if soup:
                email_data = self.extract_email_data(soup)
                self.data_saver.save_to_json(email_data)
            else:
                print("❌ Ошибка при парсинге HTML.")
        else:
            print("❌ Ошибка при загрузке HTML.")


if __name__ == "__main__":
    email_filename = "frozen_account_RU.html"  # Имя вашего HTML файла
    processor = EmailProcessor(email_filename)
    processor.process_email()