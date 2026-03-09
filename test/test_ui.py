import time
from typing import Generator, List

import allure
import pytest
from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Глобальные константы
BASE_URL: str = "https://www.chitai-gorod.ru"
CITY_BTN_SELECTOR: str = "button.chg-app-button--block:nth-child(1)"


@pytest.fixture
def driver() -> Generator[WebDriver, None, None]:
    """Инициализация и закрытие браузера для каждого теста."""
    options: Options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver_instance: WebDriver = webdriver.Chrome(options=options)
    yield driver_instance
    driver_instance.quit()


@pytest.fixture
def setup(driver: WebDriver) -> WebDriver:
    """Предусловие: вход на сайт и выбор города."""
    wait: WebDriverWait = WebDriverWait(driver, 25)
    with allure.step(f"1. Войти на сайт {BASE_URL}"):
        driver.get(BASE_URL)

    with allure.step("2. Подождать 10 секунд и подтвердить город"):
        time.sleep(10)
        city_btn: WebElement = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, CITY_BTN_SELECTOR))
        )
        driver.execute_script("arguments[0].click();", city_btn)
    return driver


@allure.step("Получение поля ввода поиска")
def get_search_input(driver: WebDriver) -> WebElement:
    """Утилита для нахождения корректного поля ввода."""
    wait: WebDriverWait = WebDriverWait(driver, 15)
    search_container: WebElement = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#app-search"))
    )
    if search_container.tag_name == "input":
        return search_container
    return search_container.find_element(By.TAG_NAME, "input")


@allure.epic("Поиск в Читай-городе")
@allure.feature("Функциональность поисковой строки")
@pytest.mark.regression
class TestSearch:

    @allure.story("Интерфейс поисковой строки")
    @allure.title("Появление 'Популярное' при нажатии на поиск")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.ui
    def test_popular_suggestions_display(self, setup: WebDriver) -> None:
        driver: WebDriver = setup
        wait: WebDriverWait = WebDriverWait(driver, 15)
        search_input: WebElement = get_search_input(driver)

        with allure.step("3. Нажать на строку поиска"):
            driver.execute_script("arguments[0].click();", search_input)
            popular_title: WebElement = wait.until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, ".suggests-list__header")
                )
            )
            assert "Популярные запросы" in popular_title.text

    @allure.story("Подсказки при вводе")
    @allure.title("Появление подсказок при вводе 3х символов")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    @pytest.mark.positive
    def test_suggestions_on_input(self, setup: WebDriver) -> None:
        driver: WebDriver = setup
        wait: WebDriverWait = WebDriverWait(driver, 15)
        search_input: WebElement = get_search_input(driver)

        with allure.step("4. Ввести 3 символа в поиск"):
            search_input.send_keys("Кни")
            suggestions: WebElement = wait.until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, "li.suggests-list__item")
                )
            )
            assert suggestions.is_displayed()

    @allure.story("Элементы управления поиском")
    @allure.title("Появление кнопки очистки 'Х'")
    @allure.severity(allure.severity_level.TRIVIAL)
    @pytest.mark.ui
    def test_clear_button_visibility(self, setup: WebDriver) -> None:
        driver: WebDriver = setup
        wait: WebDriverWait = WebDriverWait(driver, 15)
        search_input: WebElement = get_search_input(driver)

        with allure.step("5. Ввести символ и проверить кнопку 'Х'"):
            search_input.send_keys("А")
            clear_btn: WebElement = wait.until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, ".chg-utility-button")
                )
            )
            assert clear_btn.is_displayed()

    @allure.story("Элементы управления поиском")
    @allure.title("Очистка строки поиска")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    def test_clear_search_functionality(self, setup: WebDriver) -> None:
        driver: WebDriver = setup
        wait: WebDriverWait = WebDriverWait(driver, 15)
        search_input: WebElement = get_search_input(driver)

        with allure.step("6. Нажать 'Х' и проверить очистку поля"):
            search_input.send_keys("Тест")
            clear_btn_selector = ".chg-utility-button"
            clear_btn: WebElement = wait.until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, clear_btn_selector)
                )
            )
            driver.execute_script("arguments[0].click();", clear_btn)
            wait.until(
                lambda d: search_input.get_attribute("value") == ""
            )
            assert search_input.get_attribute("value") == ""

    @allure.story("Выполнение поиска")
    @allure.title("Поиск по клику на лупу")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.search
    @pytest.mark.smoke
    def test_search_execution(self, setup: WebDriver) -> None:
        driver: WebDriver = setup
        wait: WebDriverWait = WebDriverWait(
            driver,
            25,
            ignored_exceptions=[StaleElementReferenceException]
        )
        search_input: WebElement = get_search_input(driver)

        with allure.step("7. Ввести запрос и нажать на иконку поиска"):
            query: str = "Психология"
            search_input.send_keys(query)

            s_icon_selector = ".search-form__icon-search"
            search_icon: WebElement = wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, s_icon_selector)
                )
            )
            search_button: WebElement = search_icon.find_element(
                By.XPATH, "./ancestor::button"
            )

            with allure.step("Пауза 4 секунды перед кликом"):
                time.sleep(4)

            driver.execute_script("arguments[0].click();", search_button)

        with allure.step("8. Проверить заголовок и наличие товаров"):
            res_header: WebElement = wait.until(
                EC.visibility_of_element_located((By.TAG_NAME, "h1"))
            )
            assert query.lower() in res_header.text.lower()
            products: List[WebElement] = driver.find_elements(
                By.CSS_SELECTOR, "article.product-card"
            )

            allure.attach(
                f"Найдено товаров: {len(products)}",
                name="Статистика поиска",
                attachment_type=allure.attachment_type.TEXT
            )
            assert len(products) > 0, "Результаты поиска пусты"
