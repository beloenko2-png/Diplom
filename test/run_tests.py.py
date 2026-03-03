import subprocess
import sys

def run_tests():
    # Список файлов для последовательного запуска
    test_files = ["test_ui.py", "test_api.py"]

    for test_file in test_files:
        print(f"\n{'='*20}")
        print(f"Запуск тестов из файла: {test_file}")
        print(f"{'='*20}\n")

        # Запускаем pytest через subprocess
        # --alluredir=allure-results собирает данные для отчета
        result = subprocess.run([sys.executable, "-m", "pytest", test_file, "--alluredir=allure-results"])

        if result.returncode != 0:
            print(f"\n[!] Тесты в {test_file} завершились с ошибками.")
        else:
            print(f"\n[+] {test_file} пройден успешно.")

if __name__ == "__main__":
    run_tests()
