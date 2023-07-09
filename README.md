# Comparing programmer vacancies
 displays a table of average salaries of programmers.

## Programming vacancies compare
The script outputs two comparative tables of average salaries of programmers by programming languages
The first table of vacancies from the site [hh.ru](https://hh.ru) , the second table from the site [superjob.ru](https://superjob.ru)


## Requirements
Python 3 must be installed to work. You also need to install the requests, python-dotenv libraries,
terminaltables, which are described in the file requirements.txt
To install python 3, download and read the installation instructions on the website [python.org](https://www.python.org/downloads/)


## How to install
The requests library is installed by the command:
```bash
pip install requests
```
The python-dotenv library is installed by the command:
```bash
pip install python-dotenv
```
The terminal tables library is installed by the command:
```bash
pip install terminaltables==3.1.10
```

## Settings
It is necessary that there is a .env file in the project directory that contains environment variables:
* SJ_SECRET - The secret key of your application, issued in superjob when registering the application
* SJ_ID - the id that superjob issues when registering the application
* SJ_LOGIN - login from superjob
* SJ_PASS - password from superjob
## Example
```bash
python main.py
```

Project Goals
The code is written for educational purposes on online-course for web-developers dvmn.org.


# Сравниваем вакансии программистов
Скрипт выводит две сравнительные таблицы средних зарплат программистов по языкам программирования
Первая таблица вакансий с сайта [hh.ru](https://hh.ru), вторая таблица с сайта [superjob.ru](https://superjob.ru)

## Требования
Для работы должен быть установлен python3. А также необходимо установить библиотеки requests, python-dotenv, 
terminaltables, которые описаны в файле requirements.txt
Чтобы установить python3 скачайте и ознакомьтесь с инструкцией по установке на сайте [python.org](https://www.python.org/downloads/)

## Как установить
Библиотека requests устанавливается командой:
```bash
pip install requests
```
Библиотека python-dotenv устанавливается командой:
```bash
pip install python-dotenv
```
Библиотека terminaltables устанавливается командой:
```bash
pip install terminaltables==3.1.10
```

## Настройки
Необходимо чтобы в дирректории проекта был файл .env, в котором содержаться переменные окружения:
* SJ_SECRET - Secret key вашего приложения, выданный в superjob при регистрации приложения
* SJ_ID - id который выдает superjob при регистрации приложения
* SJ_LOGIN - логин от superjob
* SJ_PASS - пароль от superjob
## Пример запуска скрипта
```bash
python main.py
```

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org).