import pytest
import allure
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@pytest.fixture
def driver():
    """Инициализация браузера с маскировкой под пользователя."""
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    # Маскировка автоматизации для обхода защиты
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()

@allure.feature("Поиск в Читай-городе")
def test_chitai_gorod_search_workflow(driver):
    wait = WebDriverWait(driver, 20)

    with allure.step("1. Войти на сайт https://www.chitai-gorod.ru"):
        driver.get("https://www.chitai-gorod.ru")

    with allure.step("2. Подождать 10 секунд и нажать кнопку подтверждения города"):
        # Принудительная пауза по вашему требованию
        time.sleep(10)
        city_btn_selector = "button.chg-app-button--block:nth-child(1) > div:nth-child(1)"
        city_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, city_btn_selector)))
        
        # Исправленный вызов JS: arguments[0]
        driver.execute_script("arguments[0].click();", city_btn)

    with allure.step("3. Появление 'Популярное' при нажатии на поисковую строку"):
        search_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#app-search")))
        
        if search_element.tag_name != "input":
            search_input = search_element.find_element(By.TAG_NAME, "input")
        else:
            search_input = search_element

        # Клик через JS для активации выпадающего списка
        driver.execute_script("arguments[0].click();", search_input)
        
        popular_title = wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, ".suggests-list__header")
        ))
        assert "Популярные запросы" in popular_title.text

    with allure.step("4. Появление подсказок при вводе 3х символов"):
        search_input.send_keys("Кни")
        suggestions = wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "li.suggests-list__item:nth-child(1) > a:nth-child(1) > span:nth-child(1)")
        ))
        assert suggestions.is_displayed()

    with allure.step("5. Появление кнопки 'Х' при вводе 1 символа"):
        # Очистка через JS и ввод 1 символа
        driver.execute_script("arguments[0].value = '';", search_input)
        search_input.send_keys("А")
        
        clear_btn = wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, ".chg-utility-button > svg:nth-child(1)")
        ))
        assert clear_btn.is_displayed()

    with allure.step("6. Очистка строки поиска при нажатии 'Х'"):
        # Кликаем по родительской кнопке, так как SVG не имеет метода click()
        parent_clear_btn = clear_btn.find_element(By.XPATH, "./..")
        parent_clear_btn.click()
        assert search_input.get_attribute("value") == ""

    with allure.step("7. Нажатие значка лупа выдает список найденных товаров"):
        query = "Психология"
        search_input.send_keys(query)
        
        # Ожидаем появление иконки лупы
        search_icon = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".search-form__icon-search")
        ))
        
        # Кликаем по родительскому элементу лупы (кнопке)
        search_button = search_icon.find_element(By.XPATH, "./ancestor::button")
        driver.execute_script("arguments[0].click();", search_button)
        
        # Ожидаем заголовок результатов поиска
        search_result_header = wait.until(EC.visibility_of_element_located((By.TAG_NAME, "h1")))
        
        # Проверяем наличие ключевого слова в заголовке и наличие карточек товаров
        assert query.lower() in search_result_header.text.lower()
        products = driver.find_elements(By.CSS_SELECTOR, "article.product-card")
        assert len(products) > 0, "Товары не найдены на странице результатов"
