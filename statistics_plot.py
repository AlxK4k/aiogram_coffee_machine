import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
import PIL.ImageOps
import glob
import os
import datetime as dt
import locale
pd.options.mode.chained_assignment = None

locale.setlocale(category=locale.LC_ALL, locale="Russian")
with open("working directory.txt") as file:
    stats_dir = file.read()


pd.set_option("display.max_columns", 200)
pd.set_option("display.width", 200)
time = dt.datetime.now()
year = time.year
month = time.strftime("%B").title()
day = time.strftime("%d.%m.%Y")

# Создание двух типов графиков,для конкретного автомата
def profit_graph_send(machine_index, days_range, type_of_stat):
    df = pd.read_csv(f"{stats_dir}\stats_machine_{machine_index}.csv", encoding="utf-8-sig")
    df["День"] = pd.to_datetime(df["День"], format="%d.%m.%Y")  # Конвертация столбца в тип данных datetime

    # Диапазон дней за который выводится график
    cutoff_day = df["День"].iloc[-1] - pd.Timedelta(days=days_range)
    df1 = df[df["День"] > cutoff_day]
    df1["День"] = df1["День"].dt.strftime("%d.%m")

    if type_of_stat == "money_stats":
        df1.drop(["Месяц", "Год", "Всего кружек", "Капучино", "Эспрессо", "Латте"], axis=1, inplace=True)
        plt.style.use("ggplot")
        df1.plot(x="День", y="Поступления", )
        plt.title(f"Поступления ₽ за {days_range} дней")
        plt.xlabel("Дни")
        plt.ylabel("Поступления")
        plt.legend()

        plt.savefig("week_money.png", dpi=200)
        image = Image.open("week_money.png")
        rgb = image.convert("RGB")
        inverted_img = PIL.ImageOps.invert(rgb)
        inverted_img.save("send_money_stats.jpg")
        plt.clf()

    elif type_of_stat == "bev_stats":
        try: # Исключение на случай, если покупок не было
            capp = df1["Капучино"].sum()
            latte = df1["Латте"].sum()
            espresso = df1["Эспрессо"].sum()
            # Что-бы выделить самый частый напиток в графике и указать его положение в кортеже
            # сначала определяется его положение в списке
            coffee_list = [capp, latte, espresso]
            list_to_tuple = [0, 0, 0]
            best_coffee_position = coffee_list.index(max(coffee_list))
            for _ in coffee_list:
                list_to_tuple[best_coffee_position] = 0.1

            explode = tuple(list_to_tuple) # Кортеж вида (0, 0.1, 0) или др. в зависимости от того какой напиток

            plt.axis()
            labels = ["Капучино", "Латте", "Эспрессо"]
            colors = ["#678B00", "#00838B", "#00358C"]
            plt.title("Самый популярный кофе")
            plt.pie([capp, latte, espresso], explode=explode, shadow=True, autopct="%.1f %%", colors=colors,
                    labels=labels)

            plt.savefig("best_beverage_stat.png", dpi=200)
            image = Image.open("best_beverage_stat.png")
            rgb = image.convert("RGB")

            inverted_img = PIL.ImageOps.invert(rgb)
            inverted_img.save("best_beverage_stat_send.jpg")
            plt.clf()
        except Exception:
            return False

# Вывод общего графика с поступлениями со всех адресов
def all_stats_graph():
    all_files = glob.glob(os.path.join(stats_dir, "*.csv"))
    df2 = pd.read_csv("Список автоматов.csv")
    df3 = df2[["Улица", "Номер дома"]].copy()
    row_list = df3.values.tolist()
    clean_list = []
    for idx, i in enumerate(row_list):
        clean_list.append(" ".join(str(i) for i in row_list[idx]))

    dataframe_list = []

    plt.figure(figsize=(10, 5))
    for idx, file in enumerate(all_files):
        df = pd.read_csv(file, index_col=None, header=0)
        df["День"] = pd.to_datetime(df["День"], format="%d.%m.%Y")
        df["День"] = df["День"].dt.strftime("%d.%m")
        dataframe_list.append(df)
        x = df["День"]
        y = df["Поступления"]
        plt.style.use("ggplot")
        plt.plot(x, y,  ".-", label=clean_list[idx])

        plt.xlabel("Дни")
        plt.ylabel("Поступления, ₽")
        plt.legend()

    plt.savefig("all_stats.png", dpi=200)
    image = Image.open("all_stats.png")
    rgb = image.convert("RGB")

    inverted_img = PIL.ImageOps.invert(rgb)
    inverted_img.save("all_stats_send.jpg")
    plt.clf()
