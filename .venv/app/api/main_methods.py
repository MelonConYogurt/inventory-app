from fastapi.responses import RedirectResponse
from fastapi import FastAPI, HTTPException
from typing import Optional, List
from pydantic import BaseModel

#Data base pg
from app.sql.pg_data_base import *

#Models
from app.api.models import *

app = FastAPI()
db = data_base()


@app.get("/")
def read_root():
    return RedirectResponse(url="/docs")

@app.post("/add/product", response_model= model_product)
async def add_new_product(product : model_product):
    try:
        new_product = db.insert_products(
            name = product.name,
            price = product.price,
            code = product.code,
            quantity = product.quantity,
            category = product.category,
            description =  product.description
        )
        return new_product    
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error {e}")
    
    
    
    
