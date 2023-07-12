import requests
import time
import os
from dotenv import load_dotenv
from terminaltables import AsciiTable


ID_CITY_HH = 1
ID_CITY_SJ = 4
ID_PROFESSIONAL_ROLE_HH = 96
COUNT_DAYS = 31
VACANSIES_PER_PAGE = 100


def get_salaries_hh(vacancy=""):
    page = 0
    pages_number = 1
    url = 'https://api.hh.ru/vacancies'
    headers = {"User-Agent": 'PostmanRuntime/7.30.1'}
    salaries = []
    while page < pages_number:
        params = {"professional_role": ID_PROFESSIONAL_ROLE_HH,
                  "area": ID_CITY_HH,
                  "period": COUNT_DAYS,
                  "text": f"программист {vacancy}",
                  "per_page": VACANSIES_PER_PAGE,
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
    return {'salaries': salaries, 'number_of_vacansies': page_payload['found']}


def predict_rub_salary(salary):
    if not salary or not salary['currency'] or salary['currency'] != 'RUR':
        return None
    if not salary['from'] and not salary['to']:
        return None
    if salary['from'] and not salary['to']:
        return salary['from'] * 1.2
    if salary['to'] and not salary['from']:
        return salary['to'] * 0.8
    else:
        avg_salary = (salary['from'] + salary['to']) / 2
        return avg_salary


def get_salaries_superjob(vacancy=''):
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
                  "town": ID_CITY_SJ,
                  "page": page,
                  "count": VACANSIES_PER_PAGE
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
    return {'salaries': salaries, 'number_of_vacansies': payload['total']}


def predict_rub_salary_sj(salary):
    if not salary[-1] or salary[-1] != "rub":
        return None
    if not salary[0] and not salary[1]:
        return None
    if salary[0] and not salary[1]:
        return salary[0] * 1.2
    if not salary[0] and salary[1]:
        return salary[1] * 0.8
    else:
        avg_salary = (salary[0] + salary[1]) / 2
        return avg_salary


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
        vacancies_payload = get_salaries_hh(language)
        vacancies_found = vacancies_payload['number_of_vacansies']
        avg_salaries = [predict_rub_salary(salary) for salary in get_salaries_hh(language)['salaries']]
        real_salaryes = [salary for salary in avg_salaries if salary]
        vacancies_processed = len(real_salaryes)
        if real_salaryes:
            average_salary = int(sum(real_salaryes) / len(real_salaryes))
        else:
            average_salary = None
        aggregate_one_language = [language, vacancies_found, vacancies_processed, average_salary]
        avg_salaries_hh.append(aggregate_one_language)
        time.sleep(30)
    avg_salaries_hh_table = AsciiTable(avg_salaries_hh, title_hh)

    avg_salaries_sj = [
        ['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']
    ]

    for language in languages:
        vacancies_payload = get_salaries_superjob(language)
        number_of_vacansies_sj = vacancies_payload['number_of_vacansies']
        avg_salaries= [predict_rub_salary_sj(salary) for salary in vacancies_payload['salaries']]
        real_salaryes = [salary for salary in avg_salaries if salary]
        vacancies_processed = len(real_salaryes)
        if real_salaryes:
            average_salary = int(sum(real_salaryes) / len(real_salaryes))
        else:
            average_salary = None
        aggregate_one_language = [language, number_of_vacansies_sj, vacancies_processed, average_salary]
        avg_salaries_sj.append(aggregate_one_language)
    avg_salaries_sj_table = AsciiTable(avg_salaries_sj, title_sj)
    return print(avg_salaries_hh_table.table), print(), print(avg_salaries_sj_table.table)


if __name__ == '__main__':
    main()
