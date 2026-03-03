import pytest
import allure
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

@allure.epic("Тестирование поиска")
class TestBookSearch:

    def setup_method(self):
        with allure.step("Открыть браузер и настроить сессию"):
            options = webdriver.ChromeOptions()
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--disable-notifications")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            self.driver.maximize_window()
            self.driver.get("https://www.chitai-gorod.ru")
            self.wait = WebDriverWait(self.driver, 20)

    def teardown_method(self):
        with allure.step("Закрыть браузер"):
            self.driver.quit()

    @allure.story("1. Отправка пустого запроса (пробелы)")
    def test_search_empty_spaces(self):
        self._search("   ")
        with allure.step("Проверка: строка поиска пуста или не выдала результаты"):
            search_input = self.driver.find_element(By.NAME, "phrase")
            assert search_input.get_attribute("value").strip() == ""

    @allure.story("2. Запрос на кириллице")
    def test_search_cyrillic(self):
        self._search("Приключения")
        self._check_results()

    @allure.story("3. Запрос на латинице")
    def test_search_latin(self):
        self._search("Python")
        self._check_results()

    @allure.story("4. Запрос из символов")
    def test_search_symbols(self):
        self._search("!@#$%")
        with allure.step("Проверить сообщение о пустом результате"):
            msg = self.wait.until(EC.visibility_of_element_located((By.XPATH, "//h1 | //div[contains(@class, 'catalog-empty')]")))
            assert "ничего не найдено" in msg.text.lower()

    @allure.story("5. Запрос с цифрами")
    def test_search_numbers(self):
        self._search("1984")
        self._check_results()

    @allure.step("Выполнить поиск: '{text}'")
    def _search(self, text):
        search_input = self.wait.until(EC.element_to_be_clickable((By.NAME, "phrase")))
        search_input.click()
        # Очистка через комбинацию клавиш для надежности
        search_input.send_keys(Keys.CONTROL + "a")
        search_input.send_keys(Keys.BACKSPACE)
        search_input.send_keys(text)
        search_input.send_keys(Keys.ENTER)

    @allure.step("Проверка наличия карточек товаров")
    def _check_results(self):
        with allure.step("Ожидание загрузки результатов"):
            # Селектор карточек часто меняется, используем два варианта
            cards = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article.product-card, .product-card")))
            assert len(cards) > 0, "Товары не найдены"

