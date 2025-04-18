import datetime
from collections import defaultdict
from http.server import HTTPServer, SimpleHTTPRequestHandler

import pandas as pd
from jinja2 import Environment, FileSystemLoader, select_autoescape

df = pd.read_excel('wine3.xlsx')
df = df.fillna('')

category_order = ['Белые вина', 'Красные вина', 'Напитки']

intermediate_result = defaultdict(list)

min_prices = {
    category: df[df['Категория'] == category]['Цена'].min()
    for category in category_order
}

for _, row in df.iterrows():
    category = row['Категория'].strip()
    if category in category_order:
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
    for category in category_order
    if category in intermediate_result
}


def get_year_phrase(n: int) -> str:
    """
    Возвращает строку с правильным склонением слова "год" для числа n.
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


current_date = datetime.date.today()
event_date = datetime.date(year=1920, month=1, day=1)

delta_years = current_date.year - event_date.year

year_phrase = get_year_phrase(delta_years)

env = Environment(
    loader=FileSystemLoader('.'),
    autoescape=select_autoescape(['html']),
)
template = env.get_template('template.html')
rendered_page = template.render(years_text=year_phrase, wines=result)

with open('index.html', 'w', encoding='utf8') as file:
    file.write(rendered_page)

server = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
server.serve_forever()
