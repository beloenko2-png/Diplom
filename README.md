# Diplom

Автоматизированные UI-тесты(фаил test_ui.py)

1.Появление поля Популярные при нажатии на поисковую строку.

2.Появление подсказок при вводе 3х символов.

3.Появление кнопки'Х' при вводе 1 символа.

4.Очистка строки поиска при нажатии "Х"

5.Нажатие значка лупа выдает список найденных товаров.

pytest test_ui.py   запуск теста

pytest test_ui.py --alluredir=allure-results  запуск с сохранением результатов для Allure 

allure generate allure-results -o allure-report    генерация отчёта Allure

allure open allure-report   просмотр отчёта

pytest test_ui.py test_api.py --alluredir=allure-results запуск UI и API тестов





Автоматизированные API-тесты(фаил test_api.py)

1.Отправка пустого запроса(пробелы).

2.Отравка запроса на кириллице.

3.Отправка запроса на латинице.

4.Отправка запроса состоящего из символов.

5.Отправка запроса включающего цифры.

pytest test_api.py   запуск теста

pytest test_api.py --alluredir=allure-results  запуск с сохранением результатов для Allure

allure generate allure-results -o allure-report    генерация отчёта Allurе

allure open allure-report   просмотр отчёта

pytest test_ui.py test_api.py --alluredir=allure-results запуск UI и API тестов




https://skypro1111.yonote.ru/share/df0b2e9e-76aa-492f-9abf-e670492d9542     ссылка на финальный проект по ручному тестированию
