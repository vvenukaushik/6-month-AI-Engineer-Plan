from fastapi import FastAPI, Query
from enum import Enum
from pydantic import BaseModel, Field
from typing import Annotated, Literal



app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello world!"}


#path params

class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

@app.get("/models/{model_name}")
async def getModels(model_name: ModelName):

    if model_name is ModelName.alexnet:
        return {"model": model_name, "message": "Deep Learning FTW!"}
    if model_name.value == ModelName.lenet.value:
        return {"model_name": model_name, "message": "LeCNN all the images"}
    return {"model_name": model_name, "message": "Have some residuals"}


# Query Params

items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}, {"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}, {"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}, {"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

@app.get("/models")
async def getModels(pageNum: int = 1, pageSize : int = 10,):
    offset = (pageNum - 1) * pageSize
    pag_items = items_db[offset : offset + pageSize]
    
    return {"items_count": len(pag_items), "message": "Items fetched successfully", "items" : pag_items}


#Request Body

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


@app.post("/items/")
async def create_item(item: Item):
    item_dict = item.model_dump()
    if item.tax is not None:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict


# Query params MODEL 

class FilterParams(BaseModel):
    limit: int = Field(default=20, gt=0, le=100)
    offset: int = Field(default=0, ge=0)
    order_By: Literal["created_at", "updated-at"] = "created_at"
    tags: list[str] = []


@app.get("items/anns")
async def filterParams(params: Annotated[FilterParams, Query()]):
    return items_db

