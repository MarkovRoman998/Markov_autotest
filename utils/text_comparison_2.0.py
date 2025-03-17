import json
import difflib
import os


class DataSaver:
    """
    Класс для работы с JSON-файлами.
    """

    def __init__(self):
        self.BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.DATA_DIR = os.path.join(self.BASE_DIR, "data")

    def load_json(self, filename):
        """
        Загружает JSON-файл.
        """
        file_path = os.path.join(self.DATA_DIR, filename)
        if not os.path.exists(file_path):
            print(f"❌ Файл {filename} не найден!")
            return None
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception as e:
            print(f"❌ Ошибка при чтении {filename}: {e}")
            return None


class JsonComparator:
    """
    Класс для сравнения двух JSON-файлов.
    """

    def __init__(self, actual_filename="actual_result.json", expected_filename="expected_result.json"):
        self.data_saver = DataSaver()
        self.actual_data = self.data_saver.load_json(actual_filename)
        self.expected_data = self.data_saver.load_json(expected_filename)

    def filter_text_elements(self, data):
        """
        Извлекает все элементы типа 'text'.
        """
        if not data:
            return []

        text_elements = []
        for email in data.get("emails", []):
            for content in email.get("content", []):
                if content.get("type") == "text":
                    text_elements.append({
                        "selector": content.get("selector"),
                        "expected": content.get("expected", "")
                    })
        return text_elements

    def compare_text_elements(self):
        """
        Сравнивает текстовые элементы из JSON-файлов.
        """
        actual_text_elements = self.filter_text_elements(self.actual_data)
        expected_text_elements = self.filter_text_elements(self.expected_data)

        differences = []

        for actual, expected in zip(actual_text_elements, expected_text_elements):
            diff = list(difflib.ndiff([actual["expected"]], [expected["expected"]]))

            if any(line.startswith("- ") or line.startswith("+ ") for line in diff):
                differences.append({
                    "selector": actual["selector"],
                    "actual": actual["expected"],
                    "expected": expected["expected"],
                    "diff": "\n".join(diff)
                })

        return differences

    def run_comparison(self):
        """
        Запускает сравнение и выводит результат.
        """
        differences = self.compare_text_elements()

        if differences:
            print("❌ Найдены различия:")
            for diff in differences:
                print(f"🔹 **Селектор:** {diff['selector']}")
                print(f"✅ **Ожидаемое значение:** {diff['expected']}")
                print(f"❌ **Фактическое значение:** {diff['actual']}")
                print(f"🔍 **Различия:**\n{diff['diff']}")
                print("-" * 40)
        else:
            print("✅ Все значения типа 'text' совпадают.")


if __name__ == "__main__":
    comparator = JsonComparator()
    comparator.run_comparison()