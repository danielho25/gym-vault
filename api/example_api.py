from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from fastapi.testclient import TestClient



# tech with tim example

# fruit is the individual fruits that we will create
class Fruit(BaseModel):
    name: str


# fruits is the list of fruits that the
class fruits(BaseModel):
    fruits: List[Fruit]


app = FastAPI()
client = TestClient(app)

origins = [
    "http://localhost:3000"  # we can add a deployment site later
]

# block unauthorized requests using cors

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# setup database with postgres later, ex just uses dictionary

memory_db = {
    "fruits": []
}


# gets the fruits store in memory_db
@app.get("/fruits", response_model=fruits)  # request data from our memory_db
def get_fruits():
    return fruits(fruits=memory_db["fruits"])  # get the memory of fruits db
    # ^^^ using pydantic model, we return an instance of the fruits class defined in the pydantic model
    # returns as a json object


# send data from the fruits pydantic class
@app.post("/fruits", response_model=fruits)  #
def add_fruit(fruit: Fruit):
    memory_db["fruits"].append(fruit)  # a fruit will be added to test during the pytest file
    return fruits(fruits=memory_db["fruits"])



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

