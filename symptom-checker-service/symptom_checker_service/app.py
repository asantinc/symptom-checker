from fastapi import FastAPI
import os


app = FastAPI()

@app.get("/")
def index():
    return {"Hello": "World"}

#
# @app.post("/users/{user_id}")
# def read_item(user_id: int):
#     return {"user_id": user_id}