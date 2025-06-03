import os, datetime

from fastapi import FastAPI, HTTPException, Depends
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, create_engine, select
from sqlalchemy.orm import declarative_base, Session

JWT_SECRET = os.getenv("JWT_SECRET", "CHANGE_ME")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKENEXPIRE_MINUTES", 60))

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
# Database setup
DB_PATH = os.getenv("DB_PATH", "/data/users.db")
db_url = os.getenv("DATABASE_URL", DB_PATH)
connect_args = {"check_same_thread": False} if db_url.startswith("sqlite") else {}
engine = create_engine(db_url, connect_args=connect_args)
Base = declarative_base()
session = Session(bind=engine)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    role = Column(String, default="customer")
    pwd_hash = Column(String, nullable=False)

Base.metadata.create_all(engine)

## Schemas
class UserIn(BaseModel):
    username: str
    password: str
    role: str = Field("user", description="User role", pattern="^(user|admin)$")

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Helpers
def create_jwt(username: str, role: str):
    payload = {
        "sub": username,
        "role": role, 
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)

def verify_user(username: str, password: str):
    stmt = select(User).where(User.username == username)
    user = session.scalars(stmt).first()
    if user and pwd_ctx.verify(password, user.pwd_hash):
        return user
    return None

# FastAPI
app = FastAPI(title="Auth Service", version="0.1.0")

@app.post("/register", status_code=201)
def register(user: UserIn):
    if session.scalars(select(User).where(User.username == user.username)).first():
        raise HTTPException(status_code=409, detail="Username already taken")
    hashed = pwd_ctx.hash(user.password)
    session.add(User(username=user.username, pwd_hash=hashed, role=user.role))
    session.commit()
    return {"msg": "registered successfully"}

@app.post("/login", response_model=TokenOut)
def login(user: UserIn):
    db_user = verify_user(user.username, user.password)
    if not db_user:
        raise HTTPException(status_code=401, details="invalid Credentials")
    token = create_jwt(db_user.username, db_user.role)
    return {"access_token": token}

# endpoint for token introspection
@app.get("/verify")
def verify(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(401, "Invalid Token")
    


