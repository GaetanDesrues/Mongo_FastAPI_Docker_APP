import os
import functools
import random
import string

from pydantic import BaseModel
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from gridfs import GridFS
from io import BytesIO
from PIL import Image

from app.qrsrc.qr_main import generate_qr

app = FastAPI(
    title="QR Kerga",
    openapi_url=None,
)

# MongoDB connection
# MONGO_DETAILS = os.getenv("MONGO_DETAILS", "mongodb://mongo:27017")
A = os.getenv("MONGO_INITDB_ROOT_USERNAME")
B = os.getenv("MONGO_INITDB_ROOT_PASSWORD")
# MONGO_DETAILS = f"mongodb://{A}:{B}@mongo:27017"
MONGO_DETAILS = f"mongodb://{A}:{B}@192.168.1.159:27017"
client = MongoClient(MONGO_DETAILS)
db = client["qr_db"]
fs = GridFS(db)
collection = db["collection_qr_refs"]


# Pydantic model for the item
class QR_Ref(BaseModel):
    name: str
    text: str
    code: str = None
    qr_file_id: str = None


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
    db.drop_collection("collection_qr_refs")
    return {"message": "Welcome"}


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return FileResponse("imgs/favicon.ico")


@soft_
@app.get("/c/")
def read_items():
    def g(x):
        # if "_id" not in x:
        #     return x
        x["id"] = str(x["_id"])
        del x["_id"]
        return x

    items = collection.find()
    xx = [{"id": str(item["_id"]), **g(item)} for item in items]
    return xx


def generate_random_string(length=8):
    characters = string.ascii_letters + string.digits
    random_string = "".join(random.choice(characters) for _ in range(length))
    return random_string


@soft_
@app.post("/c/")
def create_item(item: QR_Ref):
    item.code = generate_random_string()
    b_qr = generate_qr(f"https://qr.kerga.fr/c/{item.code}")
    item.qr_file_id = str(fs.put(b_qr, filename=f"qr_{item.code}_"))

    result = collection.insert_one(item.model_dump())
    if result.inserted_id:
        return {"id": str(result.inserted_id), **item.model_dump()}
    else:
        raise HTTPException(status_code=500, detail="Item could not be created")


@app.get("/{qr_code}", response_model=QR_Ref)
def read_item(qr_code: str):
    item = collection.find_one({"code": qr_code})
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    item["id"] = str(item["_id"])
    del item["_id"]
    return QR_Ref(**item)


# @soft_
# @app.get("/svg/{code_qr}")
# async def get_svg(code_qr: str):
#     grid_out = fs.get_last_version(filename=f"qr_{code_qr}_")
#     return StreamingResponse(BytesIO(grid_out.read()), media_type="image/svg+xml")


@soft_
@app.get("/png/{code_qr}")
async def get_png(code_qr: str):
    grid_out = fs.get_last_version(filename=f"qr_{code_qr}_")
    return StreamingResponse(BytesIO(grid_out.read()), media_type="image/png")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
