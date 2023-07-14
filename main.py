import requests
import time
import os
from dotenv import load_dotenv
from terminaltables import AsciiTable


HH_CITY_ID = 1
SJ_CITY_ID = 4
HH_PROFESSIONAL_ROLE_ID = 96
DAYS_COUNT = 31
VACANSIES_PER_PAGE = 100


def get_hh_salaries(language):
    page = 0
    pages_number = 1
    url = 'https://api.hh.ru/vacancies'
    headers = {"User-Agent": 'PostmanRuntime/7.30.1'}
    salaries = []
    while page < pages_number:
        params = {"professional_role": HH_PROFESSIONAL_ROLE_ID,
                  "area": HH_CITY_ID,
                  "period": DAYS_COUNT,
                  "text": f"программист {language}",
                  "per_page": VACANSIES_PER_PAGE,
                  "page": page
                  }
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
    else:
        return count_real_salary(salary['from'], salary['to'])


def get_superjob_salaries(language, params):
    page = 0
    pages_number = 1
    url = 'https://api.superjob.ru/2.0/vacancies/'
    headers = {"User-Agent": 'PostmanRuntime/7.30.1',
               "Host": "api.superjob.ru",
               "X-Api-App-Id": params['client_secret']}
    salaries = []
    while page < pages_number:
        params = {"login": params['login'],
                  "password": params['password'],
                  "client_id": params['client_id'],
                  "client_secret": params['client_secret'],
                  "keyword": f"программист {language}",
                  "town": SJ_CITY_ID,
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
            salaries_payload = [(vacancy['payment_from'],
                                 vacancy['payment_to'],
                                 vacancy['currency']) for vacancy in vacancies
                                ]
            salaries = salaries + salaries_payload
        except requests.exceptions.HTTPError as error:
            exit("Can't get data from server: \n{0}".format(error))
        time.sleep(2)
    return {'salaries': salaries, 'number_of_vacansies': payload['total']}


def predict_rub_salary_sj(salary):
    if not salary[-1] or salary[-1] != "rub":
        return None
    else:
        return count_real_salary(salary[0], salary[1])


def count_real_salary(salary_from, salary_to):
    if not salary_from and not salary_to:
        return None
    if salary_from and not salary_to:
        return salary_from * 1.2
    if not salary_from and salary_to:
        return salary_to * 0.8
    else:
        avg_salary = (salary_from + salary_to) / 2
        return avg_salary


def main():
    load_dotenv()
    superjob_params = {
        "login": os.environ['SJ_LOGIN'],
        "password": os.environ['SJ_PASS'],
        "client_id": os.environ['SJ_ID'],
        "client_secret": os.environ['SJ_SECRET'],
    }
    languages = [
        "Python", "TypeScript", "Swift", "Scala",
        "Objective-C", "Shell", "Go", "C",
        "C#", "C++", "PHP", "Ruby",
        "Java", "JavaScript"
    ]

    HH_TITLE = 'HH Moscow'
    SUPERJOB_TITLE = 'SuperJob Moscow'
    hh_avg_salaries = [
        ['Язык программирования',
         'Вакансий найдено',
         'Вакансий обработано',
         'Средняя зарплата']
    ]
    for language in languages:
        payload_vacancies = get_hh_salaries(language)
        found_vacancies = payload_vacancies['number_of_vacansies']
        avg_salaries = [predict_rub_salary(salary) for salary in payload_vacancies['salaries']]
        real_salaryes = [salary for salary in avg_salaries if salary]
        processed_vacancies = len(real_salaryes)
        if real_salaryes:
            average_salary = int(sum(real_salaryes) / len(real_salaryes))
        else:
            average_salary = None
        aggregate_one_language = [language,
                                  found_vacancies,
                                  processed_vacancies,
                                  average_salary
                                  ]
        hh_avg_salaries.append(aggregate_one_language)
        time.sleep(30)
    hh_avg_salaries_table = AsciiTable(hh_avg_salaries, HH_TITLE)

    superjob_avg_salaries = [
        ['Язык программирования',
         'Вакансий найдено',
         'Вакансий обработано',
         'Средняя зарплата'
         ]
    ]

    for language in languages:
        payload_vacancies = get_superjob_salaries(language, superjob_params)
        found_vacancies = payload_vacancies['number_of_vacansies']
        avg_salaries = [predict_rub_salary_sj(salary) for salary in payload_vacancies['salaries']]
        real_salaryes = [salary for salary in avg_salaries if salary]
        processed_vacancies = len(real_salaryes)
        if real_salaryes:
            average_salary = int(sum(real_salaryes) / len(real_salaryes))
        else:
            average_salary = None
        aggregate_one_language = [language,
                                  found_vacancies,
                                  processed_vacancies,
                                  average_salary
                                  ]
        superjob_avg_salaries.append(aggregate_one_language)
    superjob_avg_salaries_table = AsciiTable(superjob_avg_salaries, SUPERJOB_TITLE)
    print(hh_avg_salaries_table.table)
    print()
    print(superjob_avg_salaries_table.table)


if __name__ == '__main__':
    main()
