import os
from copy import deepcopy
from contextlib import suppress
import requests
from dotenv import load_dotenv
from terminaltables import AsciiTable


TABLE_DATA = [
    [
        "Язык программирования",
        "Вакансий найдено",
        "Вакансий обработано",
        "Средняя зарплата",
    ]
]

LANGUAGES = [
    "TypeScript",
    "Swift",
    "Scala",
    "Shell",
    "C#",
    "C++",
    "Ruby",
    "Python",
    "Java",
    "Go",
]


def get_sj_response(sj_secret_key: str, sj_parameters: dict) -> dict:
    sj_api_url = "https://api.superjob.ru/2.0/vacancies/"
    sj_headers = {
        "X-Api-App-Id": sj_secret_key,
    }
    response = requests.get(
        sj_api_url,
        headers=sj_headers,
        params=sj_parameters,
        timeout=20,
    )
    response.raise_for_status()
    return response.json()


def get_hh_response(parameters: dict) -> dict:
    url = "https://api.hh.ru/vacancies"
    response = requests.get(url, params=parameters, timeout=20)
    response.raise_for_status()
    return response.json()


def predict_rub_salary(min_salary, max_salary, coefficient=0.2) -> int:
    if abs(coefficient) >= 1:
        raise ValueError("Расчетный коэффициент должен быть меньше единицы")
    result = 0
    if not min_salary and not max_salary:
        return
    if min_salary == max_salary or not max_salary:
        result = int(min_salary) * (1 + coefficient)
    elif not min_salary:
        result = int(max_salary) * (1 - coefficient)
    else:
        result = (int(min_salary) + int(max_salary)) // 2
    return result


def get_hh_rub_salary(vacancy: dict) -> None:
    salary_data = vacancy.get(
        "salary",
    )
    currency = salary_data["currency"]
    min_salary = salary_data["from"]
    max_salary = salary_data["to"]
    if not currency:
        min_salary = max_salary = 0
    salary = predict_rub_salary(min_salary, max_salary)
    return salary


def get_sj_rub_salary(vacancy) -> None:
    min_salary = vacancy.get("payment_from")
    max_salary = vacancy.get("payment_to")
    currency = vacancy.get("currency")
    if not currency:
        min_salary = max_salary = 0
    salary = predict_rub_salary(min_salary, max_salary)
    return salary


def get_sj_statistics(
    sj_secret_key,
    town_index: int = 4,
    catalogues: int = 33,
    count: int = 95,
) -> dict:
    sj_statistics = {}
    for language in LANGUAGES:
        params = {
            "town": town_index,
            "catalogues": catalogues,
            "count": count,
            "keyword": language,
        }

        vacancies, sj_total_vacancies = get_sj_vacancies(sj_secret_key, params)

        salaries = [get_sj_rub_salary(vacancy) for vacancy in vacancies]

        sj_statistics[language] = make_statistics(sj_total_vacancies, salaries)

    return sj_statistics


def get_hh_statistics(per_page: int = 100, area: str = "1") -> dict:
    hh_statistics = {}
    for language in LANGUAGES:
        params = {
            "text": language,
            "area": area,
            "only_with_salary": True,
            "per_page": per_page,
        }

        vacancies, hh_total_vacancies = get_hh_vacancies(params)

        salaries = [get_hh_rub_salary(vacancy) for vacancy in vacancies]

        hh_statistics[language] = make_statistics(hh_total_vacancies, salaries)

    return hh_statistics


def make_statistics(total_vacancies: int, salaries: list) -> dict:
    statistics = {
        "vacancies_found": total_vacancies,
        "vacancies_processed": 0,
        "average_salary": None,
    }
    filtered_salaries = [salary for salary in salaries if salary]
    if filtered_salaries:
        vacancies_processed = len(filtered_salaries)
        average_salary = int(sum(filtered_salaries) / len(filtered_salaries))
        statistics.update(
            {
                "vacancies_processed": vacancies_processed,
                "average_salary": average_salary,
            }
        )

    return statistics


def get_sj_vacancies(sj_secret_key: str, params: dict) -> tuple:
    vacancies = []
    sj_total_vacancies = 0
    more = True
    page = 0
    while more:
        params["page"] = page
        vacancies_on_page = []
        with suppress(requests.exceptions.HTTPError):
            sj_response = get_sj_response(sj_secret_key, params)
            vacancies_on_page = sj_response.get("objects")
            if not sj_total_vacancies:
                sj_total_vacancies = sj_response.get("total")
        vacancies.extend(vacancies_on_page)
        if not sj_response.get("more"):
            more = False
        else:
            page += 1
    return vacancies, sj_total_vacancies


def get_hh_vacancies(params: dict) -> tuple:
    vacancies = []
    hh_total_vacancies = 0
    with suppress(requests.exceptions.HTTPError):
        hh_response = get_hh_response(params)
        pages = hh_response.get("pages")
        hh_total_vacancies = hh_response.get("found")
        vacancies.extend(hh_response.get("items"))
        for page in range(1, pages):
            params["page"] = page
            vacancies_on_page = []
            hh_response = get_hh_response(params)
            vacancies_on_page = hh_response.get("items")
            vacancies.extend(vacancies_on_page)
    return vacancies, hh_total_vacancies


def make_ascii_table_data(statistics) -> list:
    table_data = deepcopy(TABLE_DATA)
    for language, language_stats in statistics.items():
        table_row = []
        table_row.append(language)
        for stat_value in language_stats.values():
            table_row.append(stat_value)
        table_data.append(table_row)
    return table_data


def main():
    load_dotenv("env.env")
    sj_secret_key = os.environ["SJ_SECRET_KEY"]
    hh_statistics = get_hh_statistics()
    sj_statistics = get_sj_statistics(sj_secret_key)
    hh_table_data = make_ascii_table_data(hh_statistics)
    sj_table_data = make_ascii_table_data(sj_statistics)
    hh_table = AsciiTable(hh_table_data, title="HH Moscow")
    sj_table = AsciiTable(sj_table_data, title="SuperJob Moscow")
    print(hh_table.table)
    print(sj_table.table)


if __name__ == "__main__":
    main()
