import os
from copy import deepcopy
import requests
from dotenv import load_dotenv
from terminaltables import AsciiTable


TABLE_DATA = [
    [
        'Язык программирования',
        'Вакансий найдено',
        'Вакансий обработано',
        'Средняя зарплата'
    ]
]

LANGUAGES = [
    'TypeScript',
    'Swift',
    'Scala',
    'Shell',
    'C#',
    'C++',
    'Ruby',
    'Python',
    'Java',
    'Go'
]


def get_sj_response(sj_secret_key: str, sj_parameters: dict) -> dict:
    sj_api_url = 'https://api.superjob.ru/2.0/vacancies/'
    sj_headers = {
        'X-Api-App-Id': sj_secret_key,
    }
    response = requests.get(sj_api_url,
                            headers=sj_headers,
                            params=sj_parameters,
                            timeout=20,
                            )
    response.raise_for_status()
    return response.json()


def get_hh_response(parameters: dict) -> dict:
    url = 'https://api.hh.ru/vacancies'
    response = requests.get(url, params=parameters,  timeout=20)
    response.raise_for_status()
    return response.json()


def predict_rub_salary(min_salary, max_salary, coefficient=0.2) -> int:
    if abs(coefficient) >= 1:
        raise ValueError('Расчетный коэффициент должен быть меньше единицы')
    result = 0
    if not min_salary and not max_salary:
        return
    if min_salary == max_salary or not max_salary:
        result = int(min_salary)*(1+coefficient)
    elif not min_salary:
        result = int(max_salary)*(1-coefficient)
    else:
        result = (int(min_salary)+int(max_salary))//2
    return result


def get_hh_rub_salary(vacancy: dict) -> None:
    salary_data = vacancy.get('salary',)
    currency = salary_data['currency']
    min_salary = salary_data['from']
    max_salary = salary_data['to']
    if not currency:
        min_salary = max_salary = 0
    salary = predict_rub_salary(min_salary, max_salary)
    return salary


def get_sj_rub_salary(vacancy) -> None:
    min_salary = vacancy.get('payment_from')
    max_salary = vacancy.get('payment_to')
    currency = vacancy.get('currency')
    if not currency:
        min_salary = max_salary = 0
    salary = predict_rub_salary(min_salary, max_salary)
    return salary


def get_sj_api_query_params(
    count: int = 95,
    page: int = 0,
    keyword: str = ''
) -> dict:
    return {
        'town': 4,
        'catalogues': 33,
        'count': count,
        'page': page,
        'keyword': keyword,
    }


def get_hh_api_query_params(
    per_page: int = 100,
    page: int = 0,
    text: str = ''
) -> dict:
    return {
        'text': text,
        'area': '1',
        'only_with_salary': True,
        'per_page': per_page,
        'page': page
    }


def get_sj_results(sj_secret_key) -> dict:
    results = {}
    for language in LANGUAGES:
        params = get_sj_api_query_params(keyword=language)
        sj_responce = get_sj_response(sj_secret_key, params)
        sj_total_vacancies = sj_responce.get('total')
        if not sj_total_vacancies:
            results[language] = {
                'vacancies_found': 0,
                'vacancies_processed': 0,
                'average_salary': None
            }
            continue
        vacancies = paginate_sj_response(sj_secret_key, params)
        if not vacancies:
            results[language] = {
                'vacancies_found': sj_total_vacancies,
                'vacancies_processed': 0,
                'average_salary': None
            }
            continue
        salaries = [get_sj_rub_salary(vacancy) for vacancy in vacancies]
        filtered_salaries = list(filter(lambda x: x is not None, salaries))
        vacancies_processed = len(filtered_salaries)
        if not filtered_salaries:
            results[language] = {
                'vacancies_found': sj_total_vacancies,
                'vacancies_processed': vacancies_processed,
                'average_salary': None
            }
        else:
            average_salary = int(sum(filtered_salaries)/len(filtered_salaries))
            results[language] = {
                'vacancies_found': sj_total_vacancies,
                'vacancies_processed': vacancies_processed,
                'average_salary': average_salary
            }
    return results


def get_hh_results():
    results = {}
    for language in LANGUAGES:
        params = get_hh_api_query_params(text=language)
        hh_response = get_hh_response(params)
        hh_total_vacancies = hh_response.get('found')
        if not hh_total_vacancies:
            results[language] = {
                'vacancies_found': 0,
                'vacancies_processed': 0,
                'average_salary': None
            }
            continue
        vacancies = paginate_hh_response(params)
        if not vacancies:
            results[language] = {
                'vacancies_found': hh_total_vacancies,
                'vacancies_processed': 0,
                'average_salary': None
            }
            continue

        salaries = [get_hh_rub_salary(vacancy) for vacancy in vacancies]
        filtered_salaries = list(filter(lambda x: x is not None, salaries))
        vacancies_processed = len(filtered_salaries)
        if not filtered_salaries:
            results[language] = {
                'vacancies_found': hh_total_vacancies,
                'vacancies_processed': vacancies_processed,
                'average_salary': None
            }
        else:
            average_salary = int(sum(filtered_salaries)/len(filtered_salaries))
            results[language] = {
                'vacancies_found': hh_total_vacancies,
                'vacancies_processed': vacancies_processed,
                'average_salary': average_salary
            }
    return results


def paginate_sj_response(sj_secret_key, params, pages: int = 5):
    vacancies = []
    for page in range(pages):
        params.update({'page': page})
        vacancies_on_page = []
        try:
            sj_response = get_sj_response(sj_secret_key, params)
            vacancies_on_page = sj_response.get('objects')
        except requests.exceptions.HTTPError:
            pass
        try:
            vacancies.extend(vacancies_on_page)
        except TypeError:
            pass
    return vacancies


def paginate_hh_response(params, pages: int = 10):
    vacancies = []
    for page in range(pages):
        params.update({'page': page})
        vacancies_on_page = []
        try:
            hh_response = get_hh_response(params)
            vacancies_on_page = hh_response.get('items')
        except requests.exceptions.HTTPError:
            pass
        try:
            vacancies.extend(vacancies_on_page)
        except TypeError:
            pass
    return vacancies


def make_ascii_table_data(results):
    table_data = deepcopy(TABLE_DATA)
    for key, subdict in results.items():
        table_row = []
        table_row.append(key)
        for value in subdict.values():
            table_row.append(value)
        table_data.append(table_row)
    return table_data


def main():
    load_dotenv('env.env')
    sj_secret_key = os.environ['SJ_SECRET_KEY']
    hh_results = get_hh_results()
    sj_results = get_sj_results(sj_secret_key)
    hh_table_data = make_ascii_table_data(hh_results)
    sj_table_data = make_ascii_table_data(sj_results)
    hh_table = AsciiTable(hh_table_data, title="HH Moscow")
    sj_table = AsciiTable(sj_table_data, title="SuperJob Moscow")
    print(hh_table.table)
    print(sj_table.table)


if __name__ == '__main__':
    main()
