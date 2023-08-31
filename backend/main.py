from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()
origins = [                 # 讓後端可以接受前端的request
   "http://localhost:5173", # vue跑在本地的位置
]


app.add_middleware(          # fastapi讀進origins的設定
   CORSMiddleware,
   allow_origins=origins,
   allow_credentials=True,
   allow_methods=["*"],
   allow_headers=["*"],
)

# 設定認證網域及proxy
import os
os.environ['REQUESTS_CA_BUNDLE'] = "TMGCert.crt"                                                # 認證(for nominatim)
os.environ['http_proxy'] = "http://benbllee:Aa0937454850*@auhqproxy.cdn.corpnet.auo.com:8080"   # proxy
os.environ['https_proxy'] = "https://benbllee:Aa0937454850*@auhqproxy.cdn.corpnet.auo.com:8080" # proxy

# SQL lite物件
from  toSQL import HolidaySQLconn
conn_obj = HolidaySQLconn()

# 用來取得座標
import requests

# pydantic定義前端傳來的資料形式
from pydantic import BaseModel
from pydantic import BaseModel 
from typing import Dict, Any

#  a fuction that could take a given address by user from frontend and return the latitude and longitude of that address
@app.get("/latlng_search/{search_keywords}")
def read_address(search_keywords: str):

   nominatim_api_url = 'https://nominatim.openstreetmap.org/search'
   params = {'q': search_keywords, 'format': 'json'}

   response = requests.get( nominatim_api_url, params=params)

   response_json = response.json()

   if response_json:
      lat = response_json[0]['lat']
      lng = response_json[0]['lon']
      company = response_json[0]['display_name']

      return {"status": "ˊsuccess",
               "company": f"{company}",
               "lat": f"{lat}",
               "lng": f"{lng}"}

   else:
      return {"status": "fail",
               "company": "",
               "lat": "",
               "lng": ""}
   



class Month(BaseModel):
    next: int
    pre: int
    this: int

class Year(BaseModel):
    next: int
    pre: int
    this: int

class CalendarQuery(BaseModel):
    month: Month
    year: Year
    countrys: Dict[str, Any]

@app.post("/calendar")
def holiday_data(query: CalendarQuery): # AssertionError: Path params must be of one of the supported types 

   years = [query.year.pre, query.year.this, query.year.next]
   months = [query.month.pre, query.month.this, query.month.next]
   countrys = [query.countrys[num] for num in query.countrys.keys()]

   # 用conn_obj.select_hol_table傳入各參數並取出資料
   hol_datas = conn_obj.select_hol_table(year=years, month=months, country=countrys) # [('2023', '6', '22', '端午節', '放假', 'AUHQ'), ('2023', '6', '22', '端午节', '放假', 'AUCN'),....]
   
   # 將資料整理成前端需要的格式，年、月、日、假日名稱、假日類型、國家
   hol_datas = [{"year": hol_data[0], "month": hol_data[1], "date": hol_data[2], "holiday": hol_data[3], "holiday_type": hol_data[4], "country": hol_data[5]} for hol_data in hol_datas]

   return hol_datas

   # return 




#  command to run the server
#  uvicorn main:app --reload


