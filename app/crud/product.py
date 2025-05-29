
from sqlalchemy.orm import Session
from app.models import product 
from app.schemas import product as product_schema

def get_products(db: Session):
    return db.query(product.Product).all()

def create_product(db: Session, product_data: product_schema.ProductCreate):
    db_product = product.Product(**product_data.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product
