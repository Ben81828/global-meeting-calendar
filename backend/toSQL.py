import os
import pandas as pd
import sqlite3


class HolidaySQLconn:

    def __init__(self):
        self.hol_path = "./hols/"
        self.db_path = "./holiday.db"  

    def hols_to_df(self):
        
        self.holiday_df  = pd.DataFrame(columns=["Year","Month","Date","holiday_name", "holiday_type", "Country_name"])
        for file_name in os.listdir(self.hol_path):
            if ".hol" not in file_name:
                continue
            with open(self.hol_path+file_name, 'r', encoding='utf-16') as file:
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

                self.holiday_df .loc[len(self.holiday_df )] = [year, month, date, holiday_name, holiday_type, country_name]
        
        return self.holiday_df 

    def create_conn(self):
        self.conn = sqlite3.connect(self.db_path)
        self.c = self.conn.cursor()
    
    def df_to_sqlite(self):
        # create table and use Year, Month, Date, holiday_name Country_name, as primary key
        # add try except to avoid possible error
        self.holiday_df  = self.hols_to_df()
        create_hol_table_cmd = \
        '''CREATE TABLE holiday
            (Year text, 
            Month text, 
            Date text, 
            holiday_name text, 
            holiday_type text, 
            Country_name text, 
            PRIMARY KEY (Year, Month, Date, holiday_name, Country_name))''' 

        insert_hol_cmd = "INSERT INTO holiday VALUES (?,?,?,?,?)"

        self.create_conn()

        try:
            self.c.execute(create_hol_table_cmd)
            self.conn.commit()
        except Exception as e:
            print(e)
        finally:
            self.conn.close()

        for i in range(len(self.holiday_df )):
            try:
                year = self.holiday_df .iloc[i][0]
                month = self.holiday_df .iloc[i][1]
                date = self.holiday_df .iloc[i][2]
                holiday_name = self.holiday_df .iloc[i][3]
                holiday_type = self.holiday_df .iloc[i][4]
                country_name = self.holiday_df .iloc[i][5]

                self.create_conn()
                self.c.execute(insert_hol_cmd, (year, month, date, holiday_name, holiday_type, country_name))
                self.conn.commit()
            except Exception as e:
                print(e)
            finally:
                self.conn.close()


if __name__ == '__main__':
    conn_obj = HolidaySQLconn()
    conn_obj.df_to_sqlite()





