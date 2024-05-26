import pandas as pd
import datetime as dt
import locale
import glob
import os
from Machine import Machine
import json

with open("working directory.txt") as file:
    stats_dir = file.read()

locale.setlocale(category=locale.LC_ALL, locale="Russian")

pd.set_option("display.max_columns", 100)
pd.set_option("display.width", 500)

time = dt.datetime.now()
year = time.year
month = time.strftime("%B").lower()
day = time.strftime("%d.%m.%Y")
today = time.strftime("%d")
clock = time.strftime("%H:%M:%S")

pd.set_option("display.max_columns", 100)
pd.set_option("display.width", 200)


with open("data.json", 'r', encoding="utf-8-sig") as coffee_data:
    menu = json.load(coffee_data)


# отправка статистики в телеграм бот,для конкретного автомата
def stats_send(machine_index):
    df = pd.read_csv(f"{stats_dir}\stats_machine_{machine_index}.csv", encoding="utf-8-sig")
    if not df.empty:
        df["День"] = pd.to_datetime(df["День"], format="%d.%m.%Y")
        last_day = df["День"].iloc[-1]  # Присваиваем последнюю запись (день) к переменной
        # Текущий день. Обнуляем данные о часах и минутах (normalize) что-бы сравнивать два datetime объекта
        current_day = pd.Timestamp.today().normalize()
        cups_list = []
        if current_day != last_day:
            day_sum = "пока не было"
            day_cups = "пока не было"
        else:
            day_sum = df["Поступления"].iloc[-1]
            for i in range(df["Всего кружек"].iloc[-1]):
                cups_list.append("☕")
            day_cups = " ".join(cups_list)

        # Определяем диапазон времени за который выводим статистику
        cutoff_day = df["День"].iloc[-1] - pd.Timedelta(days=7)
        df1 = df[df["День"] > cutoff_day]
        df1["День"] = df1["День"].dt.strftime("%d.%m")
        income_week = df1["Поступления"].sum()

        return (f"Поступления за день, ₽: {day_sum} \nПоступления за неделю {income_week}, ₽ "
                f"\nКружек за сегодня - {day_cups}")
    else:
        return "Покупок пока не было"


# Общая информация о поступлениях, состоянии автоматов
def all_data():
    csv_files = glob.glob(os.path.join(stats_dir, "*.csv"))
    df = pd.read_csv("Список автоматов.csv")
    df2 = df[["Номер", "Улица", "Номер дома"]].copy().set_index("Номер")
    temp_list = df2.values.tolist()
    refill_list = []
    warning_list = []
    number_list = df["Номер"].tolist()
    # Через метод класса (resource_monitor) формируем в списки адреса тех автоматов где заканчиваются ресурсы
    for idx, i in enumerate(number_list):
        machine = Machine(i, menu)
        if machine.resource_monitor() == "refill":
            refill_list.append(", ".join(map(str, temp_list[idx])))
        elif machine.resource_monitor() == "ok":
            pass
        else:
            warning_list.append(", ".join(map(str, temp_list[idx])))

    if warning_list:
        warning_message = " ; ".join(warning_list)
    else:
        warning_message = "--"
    if  refill_list:
        refill_message = " ; ".join(refill_list)
    else:
        refill_message = "--"

    li = []
    # чтение всех файлов со статистикой в датафреймы с последующим объединением в один датафрейм для вывода общей информации
    for file in csv_files:
        df = pd.read_csv(file, index_col=None, header=0)
        li.append(df)
    df_all = pd.concat(li, axis=0, ignore_index=True)
    profit = df_all["Поступления"].sum()
    cups_total = df_all["Всего кружек"].sum()


    return (f"Всего поступлений, ₽: {profit}  \nВсего кружек - {cups_total} \nЗаканчиваются ресурсы: {warning_message} "
            f"\nНеобходимо заправить: {refill_message}")


# Проверка даты последней записи в статистике и добавление новой строки на новый день
def date_check(machine_index):
    df = pd.read_csv(f"{stats_dir}\stats_machine_{machine_index}.csv", encoding="utf-8-sig")
    last_day = df.loc[len(df.index) - 1]["День"]

    if last_day != day:
        new_day_row = {"День": [day], "Месяц": month, "Год": year, "Капучино": 0, "Эспрессо": 0, "Латте": 0,
                       "Всего кружек": 0, "Поступления": 0}
        df2 = pd.DataFrame(new_day_row)
        df2.to_csv(f"{stats_dir}\stats_machine_{machine_index}.csv", encoding="utf-8-sig", mode="a",
                   index=False, header=False)


# Запись информации о покупке
def stats_writer(coffee_name, machine_index):
    date_check(machine_index)
    df = pd.read_csv(f"{stats_dir}\stats_machine_{machine_index}.csv", encoding="utf-8-sig")
    coffee_cup_cost = menu[coffee_name]["cost"]  # Читаем стоимость кружки кофе из json файла с меню
    df.at[len(df.index) - 1, coffee_name] += 1
    df.at[len(df.index) - 1, "Всего кружек"] += 1
    df.at[len(df.index) - 1, "Поступления"] += coffee_cup_cost
    df.to_csv(f"{stats_dir}\stats_machine_{machine_index}.csv", encoding="utf-8-sig", index=False)


# Формирование общей таблицы из файла каждого автомата
def pivot_table():
    df_main = pd.read_csv("Список автоматов.csv")
    all_files = glob.glob(os.path.join(stats_dir, "*.csv"))
    week_profit_list = []
    month_profit_list = []
    best_beverage_list = []
    warning_list = []
    for idx, file in enumerate(all_files):
        df = pd.read_csv(file, header=0)
        df.set_index("День")
        df["День"] = pd.to_datetime(df["День"], format="%d.%m.%Y")
        week_range = df["День"].iloc[-1] - pd.Timedelta(days=7)
        month_range = df["День"].iloc[-1] - pd.Timedelta(days=31)
        df_week = df[df["День"] > week_range]
        df_month = df[df["День"] > month_range]
        week_profit = df_week["Поступления"].sum()
        month_profit = df_month["Поступления"].sum()
        week_profit_list.append(week_profit)
        month_profit_list.append(month_profit)

        capp_count = df_week["Капучино"].sum()
        latte_count = df_week["Латте"].sum()
        esp_count = df_week["Эспрессо"].sum()

        d = {
            "Капучино": capp_count,
            "Латте": latte_count,
            "Эспрессо": esp_count
        }
        best_beverage = max(d, key=d.get)
        if all(value == 0 for value in d.values()):
            best_beverage_list.append("Пока никакого")
        else:
            best_beverage_list.append(best_beverage)

        machine = Machine(idx + 1, menu)
        machine_state = machine.resource_monitor()
        if machine_state == "refill":
            warning_list.append("Необходимо заправить")
        elif machine_state == "ok":
            warning_list.append("Автомат заправлен")
        else:
            warning_list.append(f"Заканчивается {machine.resource_monitor()}")

    df5 = df_main.assign(Поступления_за_неделю=week_profit_list)
    df6 = df5.assign(Поступления_за_месяц=month_profit_list)
    df7 = df6.assign(Самый_покупаемый_напиток=best_beverage_list)
    df_total = df7.assign(Состояние=warning_list)
    df_total.set_index("Номер")
    df_total.to_csv("Общая статистика.csv", index=False, encoding="utf-8-sig")
