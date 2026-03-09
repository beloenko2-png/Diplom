from typing import List

import allure
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# Глобальная переменная для URL
BASE_URL: str = "https://www.chitai-gorod.ru"


@allure.epic("Тестирование поиска")
@allure.feature("Валидация поисковых запросов")
class TestBookSearch:

    def setup_method(self) -> None:
        with allure.step(f"Открыть браузер и перейти на {BASE_URL}"):
            options: Options = webdriver.ChromeOptions()
            options.add_argument(
                "--disable-blink-features=AutomationControlled"
            )
            options.add_argument("--disable-notifications")
            options.add_experimental_option(
                "excludeSwitches", ["enable-automation"]
            )

            service: Service = Service(ChromeDriverManager().install())
            self.driver: webdriver.Chrome = webdriver.Chrome(
                service=service, options=options
            )
            self.driver.maximize_window()
            self.driver.get(BASE_URL)
            self.wait: WebDriverWait = WebDriverWait(self.driver, 20)

    def teardown_method(self) -> None:
        with allure.step("Закрыть браузер"):
            self.driver.quit()

    @pytest.mark.ui
    @pytest.mark.negative
    @allure.story("Негативные сценарии")
    @allure.title("Поиск строки из пробелов")
    @allure.severity(allure.severity_level.MINOR)
    def test_search_empty_spaces(self) -> None:
        self._search("   ")
        with allure.step("Проверка: строка поиска пуста"):
            search_input: WebElement = self.driver.find_element(
                By.NAME, "phrase"
            )
            assert search_input.get_attribute("value").strip() == ""

    @pytest.mark.search
    @pytest.mark.positive
    @allure.story("Положительные сценарии")
    @allure.title("Поиск на кириллице")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_search_cyrillic(self) -> None:
        self._search("Приключения")
        self._check_results()

    @pytest.mark.search
    @pytest.mark.positive
    @allure.story("Положительные сценарии")
    @allure.title("Поиск на латинице")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_latin(self) -> None:
        self._search("Python")
        self._check_results()

    @pytest.mark.ui
    @pytest.mark.negative
    @allure.story("Негативные сценарии")
    @allure.title("Поиск спецсимволов")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_symbols(self) -> None:
        self._search("!@#$%")
        with allure.step("Проверить сообщение: 'Похоже, у нас такого нет'"):
            selector = (By.CSS_SELECTOR, ".catalog-stub__title")
            msg: WebElement = self.wait.until(
                EC.visibility_of_element_located(selector)
            )
            expected_text: str = "похоже, у нас такого нет"
            assert expected_text in msg.text.lower()

    @pytest.mark.search
    @pytest.mark.positive
    @allure.story("Положительные сценарии")
    @allure.title("Поиск по цифрам (названию)")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_numbers(self) -> None:
        self._search("1984")
        self._check_results()

    @allure.step("Ввод текста '{text}' в поисковую строку")
    def _search(self, text: str) -> None:
        search_input: WebElement = self.wait.until(
            EC.element_to_be_clickable((By.NAME, "phrase"))
        )
        search_input.click()
        search_input.send_keys(Keys.CONTROL + "a")
        search_input.send_keys(Keys.BACKSPACE)
        search_input.send_keys(text)
        search_input.send_keys(Keys.ENTER)

    @allure.step("Проверка результатов поиска")
    def _check_results(self) -> None:
        with allure.step("Ожидание появления карточек товаров"):
            cards_selector: str = "article.product-card, .product-card"
            cards: List[WebElement] = self.wait.until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, cards_selector)
                )
            )
            allure.attach(
                f"Найдено товаров: {len(cards)}",
                name="Результат",
                attachment_type=allure.attachment_type.TEXT
            )
            assert len(cards) > 0, "Товары не найдены"
