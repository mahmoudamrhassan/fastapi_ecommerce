from fastapi import FastAPI
from app.db.database import engine, Base
# from app.models import user, order  # ضروري لاستدعاء الجداول

# استيراد الراوتر
from app.routers import order, product, user

app = FastAPI()

# تضمين الراوتر
app.include_router(product.router)
app.include_router(user.router)
app.include_router(order.router)

# إنشاء الجداول
Base.metadata.create_all(bind=engine)
