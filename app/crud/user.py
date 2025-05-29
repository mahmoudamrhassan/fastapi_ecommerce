from sqlalchemy.orm import Session
from app.models.user import User, EmailVerificationToken
from passlib.context import CryptContext
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user):
    hashed_password = get_password_hash(user.password)
    db_user = User(email=user.email, full_name=user.full_name, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # إنشاء توكن التحقق وحفظه
    token_str = str(uuid.uuid4())
    token = EmailVerificationToken(user_id=db_user.id, token=token_str)
    db.add(token)
    print(token)
    db.commit()
    
    return db_user, token_str

def verify_user(db: Session, token_str: str):
    token = db.query(EmailVerificationToken).filter(EmailVerificationToken.token == token_str).first()
    if not token:
        return None
    user = db.query(User).filter(User.id == token.user_id).first()
    if user:
        user.is_verified = True
        db.delete(token)
        db.commit()
        return user
    return None
