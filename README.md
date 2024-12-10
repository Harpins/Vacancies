# Сравниваем вакансии программистов

Создает запросы к API **[hh.ru](https://dev.hh.ru/)** и **[superjob.ru](https://api.superjob.ru/)**, после чего выводит в консоль данные о вакансиях программистов в **г. Москве** в виде таблиц следующего вида:
```
+HH Moscow--------------+------------------+---------------------+------------------+
| Язык программирования | Вакансий найдено | Вакансий обработано | Средняя зарплата |
+-----------------------+------------------+---------------------+------------------+
| TypeScript            | 266              | 266                 | 183694           |
| Swift                 | 69               | 69                  | 211015           |
| Scala                 | 17               | 17                  | 304352           |
| Shell                 | 89               | 89                  | 147295           |
| C#                    | 279              | 279                 | 213465           |
| C++                   | 412              | 412                 | 211210           |
| Ruby                  | 46               | 46                  | 251800           |
| Python                | 1062             | 1000                | 193647           |
| Java                  | 351              | 351                 | 212307           |
| Go                    | 420              | 420                 | 178707           |
+-----------------------+------------------+---------------------+------------------+
+SuperJob Moscow--------+------------------+---------------------+------------------+
| Язык программирования | Вакансий найдено | Вакансий обработано | Средняя зарплата |
+-----------------------+------------------+---------------------+------------------+
| TypeScript            | 4                | 0                   | None             |
| Swift                 | 3                | 2                   | 492500           |
| Shell                 | 0                | 0                   | None             |
| C#                    | 3                | 3                   | 246666           |
| C++                   | 6                | 5                   | 298800           |
| Ruby                  | 1                | 1                   | 235000           |
| Python                | 14               | 5                   | 309800           |
| Java                  | 3                | 0                   | None             |
| Go                    | 3                | 0                   | None             |
+-----------------------+------------------+---------------------+------------------+
```

## Окружение

### Зависимости

- Python3 должен быть уже установлен
- Затем используйте `pip` (или `pip3`, есть конфликт с Python2) для установки зависимостей:
```pycon
pip install -r requirements.txt
```

### Переменные окружения

- SJ_SECRET_KEY

Создайте файл `env.env` в одной папке с `vacancies.py`.

Пример содержимого `env.env`:
```
SJ_SECRET_KEY=yoursecretkey1.yoursecretkey0.yoursecretkey.123yoursecretkey.4yoursecretkey
```
#### Получение
Подробности по ссылке: [Документация API SuperJob](https://api.superjob.ru/)

## Запуск

Запустите скрипт стандартной командой вашей IDE

## Цели проекта

Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org).
