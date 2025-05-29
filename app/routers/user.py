from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas import user as user_schema
from app.crud import user as user_crud
from app.db.database import get_db
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import status
from fastapi.responses import JSONResponse
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr


conf = ConnectionConfig(
    MAIL_USERNAME="apifast065@gmail.com",
    MAIL_PASSWORD="nelk wfsi aiud tbxq",
    MAIL_FROM="apifast065@gmail.com",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,     # بدل MAIL_TLS
    MAIL_SSL_TLS=False,     # بدل MAIL_SSL
    USE_CREDENTIALS=True,
    # TEMPLATE_FOLDER='templates/email'  # تأكد من وجود هذا المجلد فعليًا
)


async def send_verification_email(email_to: EmailStr, token: str):
    verify_link = f"http://localhost:8000/users/verify-email/?token={token}"
    message = MessageSchema(
        subject="Please verify your email",
        recipients=[email_to],
        body=f"Welcome! Please verify your email by clicking on the link: {verify_link}",
        subtype="plain"
    )
    fm = FastMail(conf)
    await fm.send_message(message)

router = APIRouter(prefix="/users", tags=["users"])

# تسجيل مستخدم جديد
@router.post("/", response_model=user_schema.User)
async def register_user(user: user_schema.UserCreate, db: Session = Depends(get_db)):
    db_user = user_crud.get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    created_user, token = user_crud.create_user(db, user)
    # أرسل الإيميل مع رابط التحقق هنا - يمكنك استخدام مكتبة البريد (مثل FastAPI-Mail)
    verification_link = f"http://localhost:8000/users/verify-email/?token={token}"
    print(f"Send email verification link to user: {verification_link}")  # استبدل بالطريقة المناسبة لإرسال البريد
    await send_verification_email(email_to=user.email,token=token)
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

