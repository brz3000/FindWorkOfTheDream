import requests
import time
import os
from dotenv import load_dotenv
from terminaltables import AsciiTable


def number_of_vacansies(vacancy=""):
    url = 'https://api.hh.ru/vacancies'
    params = {'professional_role': 96,
              "area": 1,
              "period": 31,
              "text": f"программист {vacancy}"
              }
    headers = {"User-Agent": 'PostmanRuntime/7.30.1'}
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    vacansies = response.json()
    return vacansies['found']


def language_salary(vacancy="Python"):
    page = 0
    pages_number = 1
    url = 'https://api.hh.ru/vacancies'
    headers = {"User-Agent": 'PostmanRuntime/7.30.1'}
    salaries = []
    while page < pages_number:
        params = {"professional_role": 96,
                  "area": 1,
                  "period": 31,
                  "text": f"программист {vacancy}",
                  "per_page": 100,
                  "page": page}
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            page_payload = response.json()
            salaries_payload = [vacancy["salary"] for vacancy in page_payload["items"]]
            pages_number = page_payload['pages']
            salaries = salaries + salaries_payload
            page += 1
        except requests.exceptions.HTTPError as error:
            exit("Can't get data from server: \n{0}".format(error))
    return salaries


def predict_rub_salary(salary):
    if salary:
        if salary['currency'] is None:
            predict = None
        else:
            if salary['currency'] == 'RUR':
                if salary['from'] is None:
                    predict = salary['to'] * 0.8
                elif salary['to'] is None:
                    predict = salary['from'] * 1.2
                else:
                    predict = (salary['from'] + salary['to']) / 2
            else:
                predict = None
    else:
        predict = None
    return predict


def superjob_get_vacansies(vacancy=''):
    page = 0
    pages_number = 1
    url = 'https://api.superjob.ru/2.0/vacancies/'
    headers = {"User-Agent": 'PostmanRuntime/7.30.1',
               "Host": "api.superjob.ru",
               "X-Api-App-Id": os.environ['SJ_SECRET']}
    salaries = []
    while page < pages_number:
        params = {"login": os.environ['SJ_LOGIN'],
                  "password": os.environ['SJ_PASS'],
                  "client_id": os.environ['SJ_ID'],
                  "client_secret": os.environ['SJ_SECRET'],
                  "keyword": f"программист {vacancy}",
                  "town": 4,
                  "page": page,
                  "count": 100
                  }
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            payload = response.json()
            vacancies = payload['objects']
            pages_number = (payload['total'] / params['count']) + 1
            page += 1
            salaries_payload = [(vacancy['payment_from'], vacancy['payment_to'], vacancy['currency']) for vacancy in vacancies]
            salaries = salaries + salaries_payload
        except requests.exceptions.HTTPError as error:
            exit("Can't get data from server: \n{0}".format(error))
        time.sleep(2)
    return salaries


def number_of_vacansies_sj(vacancy=""):
    url = 'https://api.superjob.ru/2.0/vacancies/'
    headers = {"User-Agent": 'PostmanRuntime/7.30.1',
               "Host": "api.superjob.ru",
               "X-Api-App-Id": os.environ['SJ_SECRET']}
    params = {"login": os.environ['SJ_LOGIN'],
              "password": os.environ['SJ_PASS'],
              "client_id": os.environ['SJ_ID'],
              "client_secret": os.environ['SJ_SECRET'],
              "keyword": f"программист {vacancy}",
              "town": 4
              }
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        payload = response.json()
        count_vacansies_sj = payload['total']
    except requests.exceptions.HTTPError as error:
        exit("Can't get data from server: \n{0}".format(error))
    return count_vacansies_sj


def predict_rub_salary_sj(salary):
    if salary[-1] is None:
        predict = None
    else:
        if salary[-1] == 'rub':
            if salary[0] == 0 & salary[1] == 0:
                predict = None
            elif salary[0] > 0 & salary[1] > 0:
                predict = (salary[0] + salary[1]) / 2
            elif salary[0] > 0 & salary[1] == 0:
                predict = salary[0] * 1.2
            elif salary[0] == 0 & salary[1] > 0:
                predict = salary[1] * 0.8
            else:
                print("an incredible scenario")
        else:
            predict = None
    return predict


def main():
    load_dotenv()
    languages = ["Python", "TypeScript", "Swift", "Scala",
                 "Objective-C", "Shell", "Go", "C",
                 "C#", "C++", "PHP", "Ruby",
                 "Java", "JavaScript"]
    title_hh = 'HH Moscow'
    title_sj = 'SuperJob Moscow'
    avg_salaries_hh = [
        ['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']
    ]
    for language in languages:
        vacancies_found = number_of_vacansies(language)
        predicts = [predict_rub_salary(salary) for salary in language_salary(language)]
        real_salaryes = [salary for salary in predicts if salary is not None]
        vacancies_processed = len(real_salaryes)
        if len(real_salaryes) != 0:
            average_salary = int(sum(real_salaryes) / len(real_salaryes))
        else:
            average_salary = None
        average_salary_object = [language, vacancies_found, vacancies_processed, average_salary]
        avg_salaries_hh.append(average_salary_object)
        time.sleep(30)
    avg_salaries_hh_table = AsciiTable(avg_salaries_hh, title_hh)

    avg_salaries_sj = [
        ['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']
    ]

    for language in languages:
        predicts = [predict_rub_salary_sj(salary) for salary in superjob_get_vacansies(language)]
        real_salaryes = [salary for salary in predicts if salary is not None]
        vacancies_processed = len(real_salaryes)
        if len(real_salaryes) != 0:
            average_salary = int(sum(real_salaryes) / len(real_salaryes))
        else:
            average_salary = None
        average_salary_object = [language, number_of_vacansies_sj(language), vacancies_processed, average_salary]
        avg_salaries_sj.append(average_salary_object)
    avg_salaries_sj_table = AsciiTable(avg_salaries_sj, title_sj)
    return print(avg_salaries_hh_table.table), print(), print(avg_salaries_sj_table.table)


if __name__ == '__main__':
    main()
