import json
import os
import pandas
from Machine import Machine
import csv
import datetime as dt

time = dt.datetime.now()
day = time.strftime("%d.%m.%Y")
clock = time.strftime("%H:%M:%S")
current_time = f"{day}  {clock}"

with open ("working directory.txt") as file:
    stats_dir = file.read()


with open("data.json", 'r') as coffee_data:
    menu = json.load(coffee_data)


# Функция сортировки автоматов в списке по индексу, т.е приведение к виду 1-2-3-4 и т.д
def machines_list_sorter():
    with open("Список автоматов.csv", encoding="utf-8-sig") as file:
        data = pandas.read_csv(file)
        sorted_data = data.sort_values(by="Номер")
        sorted_data.set_index("Номер", inplace=True)
        sorted_data.to_csv("Список автоматов.csv", encoding="utf-8-sig")


# Функция приведения списка автоматов к словарю, что-бы читались двузначные номера автоматов
def address_list_to_dict():
    d = {}
    with open("Список автоматов.csv", encoding='utf8') as file:  # Читаем csv со списком адресов автоматов
        data = csv.reader(file)
        next(data)
        for number, city, street, house, date in data:
            # Форматируем csv в словарь, где ключ это номер автомата, а значение - это адрес в виде списка ({номер:[адрес]}
            d.setdefault(number, []).append("г. " + city + ", ул. " + street + ", дом " + house)
    # Убираем список из словаря,приводя к виду {номер: адрес}
    new_dict = {key: str(value[0]) for (key, value) in d.items()}
    return new_dict


# Функция первого запуска, при отсутствии файла
def first_start():
    if not os.path.isfile("Список автоматов.csv"):
        data = pandas.DataFrame(columns=["Номер", "Город", "Улица", "Номер дома", "Дата установки"])
        data.set_index("Номер", inplace=True)
        data.to_csv("Список автоматов.csv", encoding="utf-8-sig", lineterminator='\n')
    else:
        pass


# Функция определяющая есть ли пробелы в нумерации автоматов. Если есть - пробел заполняется.
# Если нет - добавляется индекс  к концу списка
def index_sorter():
    data = pandas.read_csv("Список автоматов.csv")
    index_list = data['Номер'].tolist()
    number_of_indexes = range(len(data) + 1)
    sliced_indexes = number_of_indexes[1:]
    new_index = int
    if index_list:
        for index in sliced_indexes:
            if index not in index_list:
                new_index = index
                return new_index
            else:
                new_index = len(data) + 1
    else:
        new_index = 1
    return new_index

# Добавление записи в общий список автоматов с присованием индекса
def add_machine(new_address):
    index = index_sorter()
    new_row = {"Номер": index, "Город": new_address['city'], "Улица": new_address['street'],
               "Номер дома": new_address['house'], "Дата установки": [current_time]}

    data = pandas.DataFrame(new_row)
    data.set_index("Номер", inplace=True)
    data.to_csv("Список автоматов.csv", encoding="utf-8-sig", mode="a", header=False)
    machines_list_sorter()
    new_machine = Machine(f"{index}", menu)
    new_machine.load_resources()


def remove_machine(machine_index):
    with open("Список автоматов.csv", encoding="utf-8-sig") as file:
        data = pandas.read_csv(file)
        new_data = data[data['Номер'] != machine_index]
        new_data.set_index("Номер", inplace=True)
        new_data.to_csv("Список автоматов.csv", encoding="utf-8-sig", mode="w")
    os.remove(f"Автомат{machine_index}.json")
    os.remove(f"{stats_dir}\stats_machine_{machine_index}.csv")
