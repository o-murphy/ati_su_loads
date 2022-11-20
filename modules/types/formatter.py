import re
from datetime import datetime

from .types import carTypes, cargoTypes


NOTIFY_TEMPLATE = """
<b>📅 {firstDate}</b>
<b>🔀 Маршрут:</b> {distanceTooltip} ({distance}км)
<b>💰 Оплата:</b>
⤷ С НДС: {priceNds}р.
⤷ БЕЗ НДС: {priceNoNds}р.
<b>🚚 Авто:</b>
{carTypes}
<b>📦 Груз:</b>
{loadingCargos}
<b>Рейтинг:</b> {rating}
<b>📞 Контакты:</b>
{contacts}
<b>🗒 Заметка:</b>
<i>{note}</i>
"""

CONTACT_TEMPLATE = """Имя: {name}
{phones}"""

NO_DATA = "Не доступно"


def format_notify(data: dict) -> str:
    loading = data.get('loading', {})
    date = datetime.fromisoformat(loading.get('firstDate', NO_DATA))
    route = data.get('route', {})
    loadings = loading.get('loadingCargos', {})
    cargos = [cargoTypes[f"{cargo_type['nameId']}"].Name for cargo_type in loadings]
    truck = data.get('truck', {})
    car_types = [carTypes[car_type].Name for car_type in truck['carTypes']]
    rate = data.get('rate', {})
    firm = data.get('firm', {})
    note = data.get('note', NO_DATA)
    rating = firm.get('rating', NO_DATA)
    score = rating.get('score', NO_DATA)

    contacts = firm.get('contacts', {})
    contacts_list = []
    for cont in contacts:
        name = cont.get('name', NO_DATA)
        phones = cont.get("phones", {})
        phones_list = [ph.get("number") for ph in phones] if phones else NO_DATA
        phones_list = ['⤷ +' + re.sub(r'\D', r'', f'{ph}') for ph in phones] if phones_list else NO_DATA
        contact_fmt = CONTACT_TEMPLATE.format(
            name=name,
            phones="\n".join(phones_list)
        )
        contacts_list.append(contact_fmt)

    output_data = {  # return last load
        'firstDate': date.strftime("%d.%m.%Y"),
        'distance': route.get('distance', NO_DATA),
        'distanceTooltip': route.get('distanceTooltip', NO_DATA),
        'carTypes': ', '.join(car_types) if truck else NO_DATA,
        'priceNds': rate.get('price', 0) + rate.get('priceNds', 0),
        'priceNoNds': rate.get('price', 0) + rate.get('priceNoNds', 0),
        'rating': f'{"⭐️" * int(score)}' if score else NO_DATA,
        'contacts': "\n".join(contacts_list) if contacts_list else NO_DATA,
        'note': note,
        'loadingCargos': ', '.join(cargos) if loadings else NO_DATA,
    }
    return NOTIFY_TEMPLATE.format(**output_data)

# class LogFormatter(logging.Formatter):
#     grey = "\x1b[38;20m"
#     yellow = "\x1b[33;20m"
#     red = "\x1b[31;20m"
#     bold_red = "\x1b[31;1m"
#     reset = "\x1b[0m"
#     format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
#
#     FORMATS = {
#         logging.DEBUG: grey + format + reset,
#         logging.INFO: grey + format + reset,
#         logging.WARNING: yellow + format + reset,
#         logging.ERROR: red + format + reset,
#         logging.CRITICAL: bold_red + format + reset
#     }
#
#     def format(self, record):
#         log_fmt = self.FORMATS.get(record.levelno)
#         formatter = logging.Formatter(log_fmt)
#         return formatter.format(record)
