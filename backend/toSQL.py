import os
import pandas as pd

import sqlite3


def hols_to_df():
    hol_path = "./hols/"
    holiday_df = pd.DataFrame(columns=["Year","Month","Date","holiday_name", "holiday_type", "Country_name"])
    for file_name in os.listdir(hol_path):
        if ".hol" not in file_name:
            continue
        with open(hol_path+file_name, 'r', encoding='utf-16') as file:
            data = file.read()

        holiday_datas = data.split("\n")

        # holiday_datas[0] = [AUHQ_2023節日假期表] 21
        country_name = holiday_datas[0].split("_")[0].split("[")[1]

        for data in holiday_datas[1:]:
            # data = '開國紀念日(放假),2023/1/1'
            holiday_name = data.split(",")[0].split("(")[0]
            holiday_type = data.split(",")[0].split("(")[1].split(")")[0]

            time = data.split(",")[1]

            year = time.split("/")[0]
            month = time.split("/")[1]
            date = time.split("/")[2]

            holiday_df.loc[len(holiday_df)] = [year, month, date, holiday_name, holiday_type, country_name]
    
    return holiday_df

holiday_df = hols_to_df()

#  將holiday_df正規化寫入sqlite

conn = sqlite3.connect('holiday.db')
c = conn.cursor()

c.execute('''CREATE TABLE holiday
                (Year text, Month text, Date text, holiday_name text, Country_name text)''')

for i in range(len(holiday_df)):
    c.execute("INSERT INTO holiday VALUES (?,?,?,?,?)", (holiday_df.iloc[i][0], holiday_df.iloc[i][1], holiday_df.iloc[i][2], holiday_df.iloc[i][3], holiday_df.iloc[i][4]))

conn.commit()
conn.close()





