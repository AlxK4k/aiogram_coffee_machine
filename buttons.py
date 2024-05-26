from aiogram.types import (InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from Machine import Machine
import json
from machine_create import address_list_to_dict


with open("data.json", 'r', encoding="utf-8-sig") as coffee_data:
    MENU = json.load(coffee_data)

# Главное меню
main_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Список автоматов", callback_data='m_list')],
        [InlineKeyboardButton(text="Добавить автомат", callback_data="add_machine")],
        [InlineKeyboardButton(text="Общая статистика", callback_data="all_stats")],
    ]

)

#Кнопки общей статистики
all_stats_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="График продаж", callback_data="sell_graph")],
        [InlineKeyboardButton(text="Выслать сводную таблицу", callback_data="send_pivot_table")],
        [InlineKeyboardButton(text="Главное меню", callback_data="back_to_root")]
    ]
)


# Кнопки выбранного автомата. Ресурсы, "касса"
machine_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Проверить ресурсы", callback_data='m_resources'), InlineKeyboardButton(text="Касса", callback_data='m_money')],
        [InlineKeyboardButton(text="Статистика", callback_data='m_stats')],

        [InlineKeyboardButton(text="Удалить автомат", callback_data='delete_machine')],
        [InlineKeyboardButton(text="Заправить автомат", callback_data='refill_machine')],
        [InlineKeyboardButton(text="Купить кофе", callback_data='coffee_list')],
        [InlineKeyboardButton(text="Назад", callback_data='m_list')]

    ]
)

def stats_kb(machine_index):
    callback_for_machine = str(machine_index)
    stats_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Поступления ₽ за месяц", callback_data='money_stats_month')],
            [InlineKeyboardButton(text="Поступления ₽ за неделю", callback_data='money_stats_week')],
            [InlineKeyboardButton(text="Самый покупаемый напиток за месяц", callback_data='customers_choice')],
            [InlineKeyboardButton(text="Назад", callback_data=callback_for_machine)]
        ]
    )
    return stats_kb


# Генерация кнопок для покупки кофе
def coffee_list(machine_index):
    callback_for_machine = str(machine_index)
    items = []
    with open("data.json", "r", encoding="utf-8-sig") as file:
        menu = json.load(file)
        for beverage in menu:
            items.append(beverage)
    builder = InlineKeyboardBuilder()
    [builder.button(text=item.title(), callback_data=item) for item in items]
    builder.button(text="Назад", callback_data=callback_for_machine)
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)


# Индикатор загрузки ресурсов
def warning(item):
    machine = Machine(int(item), MENU).resource_monitor()
    if machine == "ok":
        return "🟢"
    elif machine == "refill": #убрать функцию check_resources оставив только resource monitor
        return "🔴"
    else:
        return "🟠"


# Генерация кнопок по списку адресов автоматов
def automat_list():
    new_dict = address_list_to_dict() #Через эту функцию получаем список адресов приведённый к словарю см. в machine_create
    builder = InlineKeyboardBuilder()
    # Генерируем кнопки с адресами из словаря,где коллбэк задаётся по ключу (номеру)
    [builder.button(text=(item + ": " + new_dict[item] + f"   {warning(item)}"), callback_data=item) for item in
     new_dict]  # Задаём "колл-бэк" для кнопок по ключам словаря
    builder.button(text="Главное меню", callback_data="back_to_root")
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)


# Кнопки да/нет при вводе адреса автомата
def yes_no():
    builder = InlineKeyboardBuilder()
    builder.button(text="Да", callback_data="address_yes")
    builder.button(text="Нет", callback_data="address_no")
    builder.adjust(1)
    return builder.as_markup()


yes_no_buttons = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Да", callback_data="address_yes"),
         InlineKeyboardButton(text="Нет", callback_data="address_no")],
        [InlineKeyboardButton(text="ОТМЕНА", callback_data="back_to_root")]
    ]
)
yes_no_buttons_delete_machine = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Да", callback_data="delete_yes"),
         InlineKeyboardButton(text="Нет", callback_data="delete_no")]

    ]
)

back_button_to_machines_list = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="НАЗАД", callback_data="m_list")]
    ]
)

back_button_to_root = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Главное меню", callback_data="back_to_root")]
    ]
)
