import json
import os
import pandas as pd
import datetime as dt
import locale


with open ("working directory.txt") as file:
    stats_dir = file.read()
locale.setlocale(category=locale.LC_ALL, locale="Russian")
time = dt.datetime.now()
year = time.year
month = time.strftime("%B").title()
day = time.strftime("%d.%m.%Y")


class Machine():

    def __init__(self, number, menu):
        self.menu = menu
        self.number = number
        self.working = True

    def load_resources(self):
        machine_resources = {"вода": 9000,  "кофе": 9000, "молоко": 9000}
        self.data_writer(machine_resources)

    def check_resources(self, user_input):  # Функция проверки возможности выполнить заказ.
        machine_resources = self.data_reader()  # Информация считывается из json файла через data.reader()
        for ingredients in self.menu[user_input]["ingredients"]:
            if machine_resources[ingredients] >= self.menu[user_input]["ingredients"][ingredients]:  # Проверка на достаточность ресурсов в кофе-машине
                return True
            else:
                return False
# отслеживания состояния ресурсов на разных стадиях
    def resource_monitor(self):
        machine_resources = self.data_reader()
        for i in machine_resources:
            if machine_resources[i] < 300:
                return "refill"
            elif machine_resources[i] < 6000:
                resource_list = []
                resource_list.append(i)
                message = ", ".join(i for i in resource_list)
                formatted_message = message.replace(",", "", 1)
                return formatted_message
            else:
                return "ok"

# "Наливаем" кофе
    def coffee_maker(self, user_input):  # Функция вычитания ресурсов из json файла
        machine_resources = self.data_reader()  # Читаем данные из json о текущих ресурсах
        for ingredients in self.menu[user_input]["ingredients"]:
            machine_resources[ingredients] -= self.menu[user_input]["ingredients"][ingredients]  # Вычитаем ресурсы на чашку из ресурсов машины
            self.data_writer(machine_resources)  # Здесь пишутся обновлённые данные в json с ресурсами

    def data_reader(self):  # Функция чтения файла с ресурсами машины
        with open(f"Автомат{self.number}.json", "r", encoding="utf-8-sig") as data_file:
            machine_resources = json.load(data_file)
            return machine_resources

    def data_writer(self, machine_resources):  # Функция записи обновлённых данных
        with open(f"Автомат{self.number}.json", "w", encoding="utf-8-sig") as data_file:
            json.dump(machine_resources, data_file, ensure_ascii=False)
        # Если создан новый автомат, создаётся файл под статистику автомата
        if not os.path.isfile(f"{stats_dir}\stats_machine_{self.number}.csv"):
            d = {"День": [day], "Месяц": month, "Год": year, "Капучино": 0, "Эспрессо": 0, "Латте": 0,
                       "Всего кружек": 0, "Поступления": 0}
            df = pd.DataFrame(d)
            df.set_index("День", inplace=True)
            df.to_csv(f"{stats_dir}\stats_machine_{self.number}.csv")
        else:
            pass
# Отправка информации о состоянии ресурсов
    def report(self):
        machine_resources = self.data_reader()
        water = machine_resources["вода"]
        coffee = machine_resources["кофе"]
        milk = machine_resources["молоко"]
        return f"Вода: {water} мл. \nКофе: {coffee} гр. \nМолоко: {milk} гр."
