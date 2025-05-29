from pydantic import BaseModel

class OrderCreate(BaseModel):
    user_id: int
    product_name: str
    quantity: int

class OrderResponse(OrderCreate):
    id: int

    class Config:
        from_attributes = True  # بديل orm_mode في Pydantic v2
