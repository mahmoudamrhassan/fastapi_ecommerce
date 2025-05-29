from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models import order as order_model
from app.models import user as user_model
from app.schemas import order as order_schema

router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)

@router.post("/", response_model=order_schema.OrderResponse)
def create_order(order: order_schema.OrderCreate, db: Session = Depends(get_db)):
    # التحقق من وجود المستخدم
    user = db.query(user_model.User).filter(user_model.User.id == order.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db_order = order_model.Order(**order.dict())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

@router.get("/", response_model=list[order_schema.OrderResponse])
def get_orders(db: Session = Depends(get_db)):
    return db.query(order_model.Order).all()
