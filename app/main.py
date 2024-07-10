import functools
import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# MongoDB connection
# MONGO_DETAILS = os.getenv("MONGO_DETAILS", "mongodb://mongo:27017")
A = os.getenv("MONGO_INITDB_ROOT_USERNAME")
B = os.getenv("MONGO_INITDB_ROOT_PASSWORD")
MONGO_DETAILS = f"mongodb://{A}:{B}@mongo:27017"
client = MongoClient(MONGO_DETAILS)
# db = client.test_database
# collection = db.test_collection


# Pydantic model for the item
class Item(BaseModel):
    name: str


def soft_(func):
    """Print the function signature and return value"""

    @functools.wraps(func)
    def wrapper_soft(*args, **kwargs):
        # args_repr = [repr(a) for a in args]
        # kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
        # signature = ", ".join(args_repr + kwargs_repr)
        # print(f"Calling {func.__name__}({signature})")

        try:
            value = func(*args, **kwargs)
            # print(f"{func.__name__!r} returned {value!r}")
            return value
        except ConnectionFailure:
            print("Failed to connect to MongoDB")
        except OperationFailure as e:
            print(f"Operation failed: {e}")
        except ValueError as ve:
            print(f"Value error: {ve}")

    return wrapper_soft


@app.get("/")
def read_root():
    client.admin.command("ping")
    print("Connected successfully to MongoDB")

    db = client["my_database"]
    db.drop_collection("my_collection")
    # collection = db["my_collection"]

    # # Add a document to the collection
    # document = {"name": "John Doe", "age": 30, "email": "john.doe@example.com"}
    # result = collection.insert_one(document)
    # print(f"Inserted document with ID: {result.inserted_id}")

    # # Read the document back
    # fetched_document = collection.find_one({"_id": result.inserted_id})
    # print("Fetched document:", fetched_document)

    return {"message": "Welcome"}


@soft_
@app.get("/items/")
def read_items():
    db = client["my_database"]
    collection = db["my_collection"]
    items = collection.find()
    return [{"id": str(item["_id"]), "name": item["name"]} for item in items]

@soft_
@app.post("/items/")
def create_item(item: Item):
    # Insert item into MongoDB
    db = client["my_database"]
    collection = db["my_collection"]
    result = collection.insert_one(item.dict())
    if result.inserted_id:
        return {"id": str(result.inserted_id), "name": item.name}
    else:
        raise HTTPException(status_code=500, detail="Item could not be created")
