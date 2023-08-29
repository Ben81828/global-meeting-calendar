from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 用來取得座標
import requests
import os
os.environ['REQUESTS_CA_BUNDLE'] = "TMGCert.crt"                                                # 認證(for nominatim)
os.environ['http_proxy'] = "http://benbllee:Aa0937454850*@auhqproxy.cdn.corpnet.auo.com:8080"   # proxy
os.environ['https_proxy'] = "https://benbllee:Aa0937454850*@auhqproxy.cdn.corpnet.auo.com:8080" # proxy

app = FastAPI()

# 讓後端可以接受前端的request
origins = [
   "http://localhost:5173", # vue跑在本地的位置
]



# fastapi讀進origins的設定
app.add_middleware(
   CORSMiddleware,
   allow_origins=origins,
   allow_credentials=True,
   allow_methods=["*"],
   allow_headers=["*"],
)

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




#  command to run the server
#  uvicorn main:app --reload


