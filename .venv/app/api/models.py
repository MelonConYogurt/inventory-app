from typing import Optional, List
from pydantic import BaseModel

class model_product(BaseModel):
    name: str
    price: float
    code: int
    quantity: int
    category: Optional[str] = None
    description: Optional[str] = None
    

