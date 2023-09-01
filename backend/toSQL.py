import os
import pandas as pd
import sqlite3

import os
import pandas as pd
import sqlite3

class HolidaySQLconn:

    def __init__(self):
        self.hol_path = "./hols/"
        self.db_path = "./Calendar.db"
        self.col_name_list = ["year","month","date","holiday", "holiday_type", "country"]
        self.holiday_df = self.hols_to_df(self.col_name_list)
        self.create_hol_table()
        self.insert_hol_data()
                      

    def hols_to_df(self, col_name_list):
        # 將hol檔案轉成self.holiday_df: pd.dataframe
        holiday_df  = pd.DataFrame(columns=col_name_list)

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

                holiday_df.loc[len(holiday_df )] = [year, month, date, holiday_name, holiday_type, country_name]
        
        return holiday_df
       

    def create_table_by_df_col(self, table_name, col_name):
        # 做一個table，pk為col_name
        create_table_cmd = \
            f'''CREATE TABLE {table_name}
                ({col_name} text PRIMARY KEY)'''
        
        #  執行create_country_table_cmd
        try:
            conn = sqlite3.connect(self.db_path)         
            c = conn.cursor()
            c.execute(create_table_cmd)
            conn.commit()
        
        except Exception as e:
            print(e)

        finally:
            conn.close()                   
        
    
    def insert_data_by_df_col(self, table_name, col_name):
        # 將self.holiday_df內的country_name資料，塞入country table
        unique_array = pd.unique(self.holiday_df[col_name]) # 取得所有不重複的country_name

        # 用迴圈執行update_country_table_cmd將country_array資料寫入country table
        for unique_value in unique_array:
            try:
                update_cmd = f"INSERT INTO {table_name} ({col_name}) VALUES ('{unique_value}')"
                conn = sqlite3.connect(self.db_path)        
                c = conn.cursor()
                c.execute(update_cmd)
                conn.commit()
            except Exception as e:
                print(e)
            finally:
                conn.close()
                
    def select_table_by_df_col(self, table_name):
        # 執行select指令，存入變數country_table，確認資料有塞進去
        select_cmd = f"SELECT * FROM {table_name}"
        
        try:
            conn = sqlite3.connect(self.db_path)        
            c = conn.cursor()
            table_data = c.execute(select_cmd).fetchall()
            
        except Exception as e:
            print(e)
            
        finally:
            conn.close()

        return table_data

    def create_hol_table(self):
        # 用self.holiday_df內的各col建立正規化的各table
        self.table_name_list = [ col_name+"_table" for col_name in self.col_name_list]
        for table_name, col_name in zip(self.table_name_list, self.col_name_list):
            self.create_table_by_df_col( table_name, col_name)
            self.insert_data_by_df_col( table_name, col_name)
            self.select_table_by_df_col( table_name)

        # 依self.holiday_df內的資料，以及前面正規化的各table，用fk建立table
        try:
            conn = sqlite3.connect(self.db_path)        
            c = conn.cursor()
            c.execute('''CREATE TABLE holiday
                    (Year text,
                    Month text,
                    Date text,
                    holiday_name text,
                    holiday_type text,
                    Country_name text,
                    PRIMARY KEY (Year, Month, Date, holiday_name, Country_name),
                    FOREIGN KEY (Year) REFERENCES year_table(year),
                    FOREIGN KEY (Month) REFERENCES month_table(month),
                    FOREIGN KEY (Date) REFERENCES date_table(date),
                    FOREIGN KEY (holiday_name) REFERENCES holiday_table(holiday),
                    FOREIGN KEY (Country_name) REFERENCES country_table(country))''')
            conn.commit()

        except Exception as e:
            print(e)
        
        finally:
            conn.close()

    def insert_hol_data(self):
        # 將self.holiday_df內的資料，塞入holiday table
        for index, row in self.holiday_df.iterrows():
            try:
                update_cmd = f"INSERT INTO holiday VALUES ('{row['year']}', '{row['month']}', '{row['date']}', '{row['holiday']}', '{row['holiday_type']}', '{row['country']}')"
                conn = sqlite3.connect(self.db_path)         
                c = conn.cursor()
                c.execute(update_cmd)
                conn.commit()
            except Exception as e:
                print(e)
            finally:
                conn.close()
    
    def select_hol_table(self, country=None, year=None, month=None):

        select_cmd = "SELECT * FROM holiday WHERE "

        # 依條件執行select指令，存入變數holiday_table，確認資料有塞進去
        if country is not None:
            country_conditions = [f"Country_name = '{c}'" for c in country]
            select_cmd += "(" + " OR ".join(country_conditions) + ")" + "  AND "

        if year is not None:
            year_conditions = [f"Year = '{y}'" for y in year]
            select_cmd += "(" + " OR ".join(year_conditions) + ")" + "  AND "

        if month is not None:
            month_conditions = [f"Month = '{m}'" for m in month]
            select_cmd += "(" + " OR ".join(month_conditions) + ")" + "  AND "


        # 若where或and結尾，則去除
        if "WHERE" or "AND" in select_cmd[-6:]:
            select_cmd = select_cmd[:-6]
        
        print(select_cmd)

        holiday_table = None

        try:
            conn = sqlite3.connect(self.db_path)         
            c = conn.cursor()
            holiday_table = c.execute(select_cmd).fetchall()
            print(holiday_table)
        
        except Exception as e:
            print(e)

        finally:
            conn.close()

        return holiday_table



class OfficeSQLconn:

    def __init__(self):
        self.db_path = "./Calendar.db"        
        self.office_path = "全球辦公室時間資料列表.csv"
        self.office_df = pd.read_csv(self.office_path, encoding='utf-8-sig')
        self.office_table_name = "office"
        self.office_df_to_sql()
    
    def office_df_to_sql(self):
        self.office_df.to_sql( self.office_table_name, sqlite3.connect(self.db_path), if_exists='replace', index=False)

    def check_office_table(self):
        select_cmd = f"SELECT * FROM {self.office_table_name}"
        
        try:
            conn = sqlite3.connect(self.db_path)        
            c = conn.cursor()
            table_data = c.execute(select_cmd).fetchall()
            
        except Exception as e:
            print(e)
            
        finally:
            conn.close()

        return table_data