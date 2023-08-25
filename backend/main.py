from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 這邊的設定是讓後端可以接受前端的request
origins = [
   "http://localhost:5173", # vue跑在本地的位置
]

# 如何讓fastapi讀進origins的設定
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

   test_company = search_keywords
   test_lat = 0
   test_lng = 0

   company = test_company
   lat = test_lat
   lng = test_lng
   return {"company": f"{company}",
           "lat": f"{lat}",
           "lng": f"{lng}"}






#  command to run the server
#  uvicorn main:app --reload


