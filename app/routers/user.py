from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas import user as user_schema
from app.crud import user as user_crud
from app.db.database import get_db
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import status
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/users", tags=["users"])

# تسجيل مستخدم جديد
@router.post("/", response_model=user_schema.User)
def register_user(user: user_schema.UserCreate, db: Session = Depends(get_db)):
    db_user = user_crud.get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    created_user, token = user_crud.create_user(db, user)
    # أرسل الإيميل مع رابط التحقق هنا - يمكنك استخدام مكتبة البريد (مثل FastAPI-Mail)
    verification_link = f"http://localhost:8000/users/verify-email/?token={token}"
    print(f"Send email verification link to user: {verification_link}")  # استبدل بالطريقة المناسبة لإرسال البريد
    return created_user

# التحقق من الإيميل
@router.get("/verify-email/")
def verify_email(token: str, db: Session = Depends(get_db)):
    user = user_crud.verify_user(db, token)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    return {"msg": "Email successfully verified"}

# تسجيل دخول (فقط للمستخدمين الذين تحققوا)
@router.post("/login/")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = user_crud.get_user_by_email(db, form_data.username)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if not user_crud.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if not user.is_verified:
        raise HTTPException(status_code=400, detail="Please verify your email before logging in.")
    # هنا قم بإنشاء توكن JWT أو ما يناسبك
    return {"msg": "Login successful"}
