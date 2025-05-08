import datetime
from collections import defaultdict
from http.server import HTTPServer, SimpleHTTPRequestHandler

import pandas as pd
from jinja2 import Environment, FileSystemLoader, select_autoescape
from settings import EXCEL_FILE


TEMPLATE_FILE = 'template.html'
OUTPUT_FILE = 'index.html'
EVENT_DATE = datetime.date(year=1920, month=1, day=1)
SERVER_ADDRESS = ('0.0.0.0', 8000)


def get_year_phrase(n: int) -> str:
    """Возвращает строку с правильным склонением слова 'год' для числа n.

        Args:
            n (int): Количество лет.

        Returns:
            str: Строка с правильной формой слова "год".
    """
    n = abs(n)
    if 11 <= n % 100 <= 14:
        word = "лет"
    else:
        last_digit = n % 10
        if last_digit == 1:
            word = "год"
        elif 2 <= last_digit <= 4:
            word = "года"
        else:
            word = "лет"
    return f"Уже {n} {word} с вами!"


def load_and_process_data(filename: str) -> tuple[dict, list[str]]:
    """Загружает данные из Excel и формирует структуру для шаблона.

        Args:
            filename (str): Путь к Excel-файлу.

        Returns:
            dict: Словарь с категориями и списками вин, а также список категорий.
    """

    df = pd.read_excel(filename)
    df = df.fillna('')

    categories_order = df['Категория'].dropna().unique().tolist()

    min_prices = {
        category: df[df['Категория'] == category]['Цена'].min()
        for category in categories_order
    }

    intermediate_result = defaultdict(list)

    for _, row in df.iterrows():
        category = row['Категория'].strip()
        is_profitable = row['Цена'] == min_prices[category]
        wine = {
            'Картинка': row['Картинка'],
            'Название': row['Название'],
            'Сорт': row['Сорт'],
            'Цена': row['Цена'],
            'Выгодно': is_profitable,
        }
        intermediate_result[category].append(wine)

    result = {
        category: intermediate_result[category]
        for category in categories_order
        if category in intermediate_result
    }
    return result, categories_order


def render_template(template_file: str, context: dict, output_file: str) -> None:
    """Рендерит HTML-шаблон с данными и сохраняет его в файл.

        Args:
            template_file (str): Путь к шаблону.
            context (dict): Данные для шаблона.
            output_file (str): Путь для сохранения HTML-файла.
    """
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html']),
    )
    template = env.get_template(template_file)
    rendered_page = template.render(**context)

    with open(output_file, 'w', encoding='utf8') as file:
        file.write(rendered_page)


def run_server(address: tuple) -> None:
    """Запускает HTTP-сервер на указанном адресе.

        Args:
            address (tuple): Кортеж с IP-адресом и портом.
    """
    server = HTTPServer(address, SimpleHTTPRequestHandler)
    print(f"Serving HTTP on {address[0]} port {address[1]} ...")
    server.serve_forever()


def main():
    wines, categories_order = load_and_process_data(EXCEL_FILE)

    current_date = datetime.date.today()
    delta_years = current_date.year - EVENT_DATE.year
    year_phrase = get_year_phrase(delta_years)

    context = {
        'years_text': year_phrase,
        'wines': wines,
        'categories_order': categories_order,
    }

    render_template(TEMPLATE_FILE, context, OUTPUT_FILE)

    run_server(SERVER_ADDRESS)


if __name__ == '__main__':
    main()
