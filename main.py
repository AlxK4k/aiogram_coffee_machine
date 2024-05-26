import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
import buttons
import json
import machine_create
from Machine import Machine
from aiogram.types import FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from machine_create import add_machine, remove_machine, address_list_to_dict
from cash_register import stats_send, stats_writer, all_data, pivot_table
from statistics_plot import *

data = dict
machine_index = 0

BOT_TOKEN = "token"
bot = Bot(BOT_TOKEN)
dp = Dispatcher()


class Address(StatesGroup):
    city = State()
    street = State()
    house = State()
    validate = State()


with open("data.json", 'r', encoding="utf-8-sig") as coffee_data:
    MENU = json.load(coffee_data)
beverage_list = [beverage for beverage in MENU]

print("запуск")


@dp.message(Command("start"))
async def start(message: Message):
    await message.answer("☕")
    machine_create.first_start()
    await message.answer(text="Выберите действие ☕", reply_markup=buttons.main_kb)


# Возврат в главное меню
@dp.callback_query(F.data == "back_to_root")
async def root(callback: CallbackQuery):
    await callback.message.answer("☕")
    await callback.message.answer(text="Выберите действие ☕", reply_markup=buttons.main_kb)


@dp.callback_query(F.data == "check_id")
async def check_id(callback: CallbackQuery):
    await callback.message.answer(text=f"Ваш ID:{callback.from_user.id}")


# Добавление автомата-город
@dp.callback_query(F.data == "add_machine")
async def add_machine_city(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Address.city)
    await callback.message.answer(text="Укажите город")


# Добавление автомата-улица
@dp.message(Address.city, F.text)
async def add_machine_street(message: Message, state: FSMContext):
    await state.update_data(city=message.text.title())
    await state.set_state(Address.street)
    await message.answer(text="Укажите улицу")


# Добавление автомата-номер дома
@dp.message(Address.street, F.text)
async def add_machine_street(message: Message, state: FSMContext):
    await state.update_data(street=message.text.title())
    await state.set_state(Address.house)
    await message.answer(text="Укажите номер дома")


# Добавление автомата-всё ли верно
@dp.message(Address.house, F.text)
async def add_machine_house(message: Message, state: FSMContext):
    global data
    data = await state.update_data(house=message.text)
    await state.set_state(Address.validate)
    text = f"г.{data['city']}, ул.{data['street']}, №{data['house']}"
    await message.answer(text=f"Добавленный адрес: {text}, всё верно?", reply_markup=buttons.yes_no_buttons)


# Подтверждение введённого адреса
@dp.callback_query(Address.validate, F.data == "address_yes")
async def add_machine_confirm(callback: CallbackQuery, state: FSMContext):
    global data
    data = await state.get_data()
    await state.clear()
    symbol = "✔️"
    add_machine(data)  # Вызов функции из файла Machine_create, с передачей данных от пользователя об адресе автомата
    await callback.message.answer(text=f"Автомат добавлен {symbol}", reply_markup=buttons.automat_list())


# Отказ от введённого адреса,переключение на ввод адреса заново
@dp.callback_query(Address.validate, F.data == "address_no")
async def add_machine_confirm(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Address.city)
    await callback.message.answer(text="Введите город", reply_markup=buttons.back_button_to_root)


# Удаление автомата
@dp.callback_query(F.data == "delete_machine")
async def delete_machine(callback: CallbackQuery):
    await callback.message.answer(text="Вы уверены?", reply_markup=buttons.yes_no_buttons_delete_machine)


@dp.callback_query(lambda call: call.data == "delete_yes" or call.data == "delete_no")
async def delete_machine(callback: CallbackQuery):
    if callback.data == "delete_yes":
        remove_machine(machine_index)
        await callback.message.answer(text="Автомат удалён ❌", reply_markup=buttons.automat_list())
    else:
        await callback.message.answer("👍", reply_markup=buttons.machine_kb)


# Список автоматов
@dp.callback_query(F.data == "m_list")
async def machines_list(callback: CallbackQuery):
    await callback.message.answer(text="Список автоматов 🗃️", reply_markup=buttons.automat_list())


# Отчёт о ресурсах конкретного автомата
@dp.callback_query(F.data == "m_resources")
async def machine_resources(callback: CallbackQuery):
    global machine_index
    report = Machine(f"{machine_index}", MENU).report()
    await callback.message.answer(text=report, reply_markup=buttons.machine_kb)


@dp.callback_query(F.data == "refill_machine")
async def machine_resources(callback: CallbackQuery):
    global machine_index
    Machine(f"{machine_index}", MENU).load_resources()
    await callback.message.answer(text="Автомат заправлен", reply_markup=buttons.machine_kb)


# "Касса"
@dp.callback_query(F.data == "m_money")
async def machine_resources(callback: CallbackQuery):
    global machine_index
    await callback.message.answer(text=f"{stats_send(machine_index)}", reply_markup=buttons.machine_kb)


@dp.callback_query(F.data == "coffee_list")
async def coffee_list(callback: CallbackQuery):
    await callback.message.answer(text="Выберите напиток", reply_markup=buttons.coffee_list(machine_index))


@dp.callback_query(F.data == "m_stats")
async def machine_stats(callback: CallbackQuery):
    global machine_index
    await callback.message.answer(text="Выберите действие", reply_markup=buttons.stats_kb(machine_index))


@dp.callback_query(F.data == "all_stats")
async def month_money_stats(callback: CallbackQuery):
    await callback.message.answer(text=all_data(), reply_markup=buttons.all_stats_kb)


@dp.callback_query(F.data == "send_pivot_table")
async def pivot_table_stats(callback: CallbackQuery):
    all_stats_graph()
    pivot_table()
    file_path = "Общая статистика.csv"
    send_document = FSInputFile(path=file_path)
    await bot.send_document(document=send_document, chat_id=callback.message.chat.id,
                            reply_markup=buttons.back_button_to_root)


@dp.callback_query(F.data == "sell_graph")
async def month_money_stats(callback: CallbackQuery):
    all_stats_graph()
    file_path = "all_stats_send.jpg"
    plot_file = FSInputFile(path=file_path)
    await bot.send_photo(photo=plot_file, chat_id=callback.message.chat.id, reply_markup=buttons.back_button_to_root)


@dp.callback_query(F.data == "money_stats_month")
async def month_money_stats(callback: CallbackQuery):
    profit_graph_send(machine_index, 31, "money_stats")
    file_path = "send_money_stats.jpg"
    plot_file = FSInputFile(path=file_path)
    await bot.send_photo(photo=plot_file, chat_id=callback.message.chat.id,
                         reply_markup=buttons.stats_kb(machine_index))


@dp.callback_query(F.data == 'money_stats_week')
async def week_money_stats(callback: CallbackQuery):
    profit_graph_send(machine_index, 7, "money_stats")
    file_path = "send_money_stats.jpg"
    plot_file = FSInputFile(path=file_path)
    await bot.send_photo(photo=plot_file, chat_id=callback.message.chat.id,
                         reply_markup=buttons.stats_kb(machine_index))


@dp.callback_query(F.data == 'customers_choice')
async def best_beverage(callback: CallbackQuery):
    check = profit_graph_send(machine_index, 7, "bev_stats")
    if check == False:
        await callback.message.answer(text="Покупок пока не было", reply_markup=buttons.machine_kb)
    else:
        file_path = "best_beverage_stat_send.jpg"
        plot_file = FSInputFile(path=file_path)
        await bot.send_photo(photo=plot_file, chat_id=callback.message.chat.id,
                             reply_markup=buttons.stats_kb(machine_index))


# Функция проверяющая возможность выполнить заказаз, монитор ресурсов и "приготовления" кофе
@dp.callback_query(lambda call: call.data in beverage_list)
async def buy_coffee(callback: CallbackQuery):
    user_beverage_choice = callback.data
    machine = Machine(machine_index, MENU)
    if machine.check_resources(user_beverage_choice):
        machine.coffee_maker(user_beverage_choice)
        stats_writer(user_beverage_choice, machine_index)
        await callback.message.answer(text="☕")
        await callback.message.answer(text=f"Вот ваш {user_beverage_choice}☕", reply_markup=buttons.machine_kb)
    else:
        machine = Machine(machine_index, MENU)
        await bot.send_message(chat_id=callback.message.chat.id,
                               text=f"Необходимо заправить автомат ❗ \n{machine.report()}",
                               reply_markup=buttons.machine_kb)


# Эхо-функция. Ловит коллбэки от конкретной машины по индексу
@dp.callback_query()
async def current_machine(callback: CallbackQuery):
    global machine_index  # Индекс машины с которой работаем
    machine_index = callback.data  # Присваиваем коллбэк к переменной
    address_list = address_list_to_dict()
    current_address = address_list[machine_index]
    machine_index = int(callback.data)
    await callback.message.answer(text=f"{current_address} Выберите действие:",
                                  reply_markup=buttons.machine_kb)


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
