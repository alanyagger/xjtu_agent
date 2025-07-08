# -*- coding: utf-8 -*-
"""
FastAPI 交小荣智能教务后端
"""

import json
import time
import uuid
import logging
import os
from typing import List, Dict, Any, AsyncGenerator
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import FastAPI, HTTPException, Query, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import StreamingResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, String, Boolean
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, EmailStr, field_validator
import redis
from config import config
from passlib.context import CryptContext
from agents.demo import EhallAgent  

# ---------- 新增数据库配置（用户表） ----------
SQLALCHEMY_DATABASE_URL = "sqlite:///./users.db"  # 数据库文件存在backend目录
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
UserSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ---------- 新增JWT和密码加密配置 ----------
SECRET_KEY = config.get_secret_key() or "your-secret-key"  # 去config.py里加SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# ---------- 数据库模型（用户表） ----------
class DBUser(Base):
    __tablename__ = "users"
    username = Column(String, primary_key=True, index=True)  # 学号
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

Base.metadata.create_all(bind=engine)  # 创建表（首次运行自动建表）

# ---------- Pydantic模型（接口入参/出参） ----------
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator('username')
    def username_must_be_digits(cls, v):
        if not v.isdigit():
            raise ValueError('学号必须为数字')
        return v

class Token(BaseModel):
    access_token: str
    token_type: str

# ---------- 工具函数（密码、Token、数据库操作） ----------
def get_user_db():
    db = UserSessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_db_user(db: Session, username: str):
    return db.query(DBUser).filter(DBUser.username == username).first()

def create_db_user(db: Session, user: UserCreate):
    db_user = DBUser(
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username: str, password: str):
    user = get_db_user(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_user_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_db_user(db, username)
    if user is None:
        raise credentials_exception
    return user



# 配置日志系统（保持不变）
os.makedirs(config.LOG_DIR, exist_ok=True)
logging.basicConfig(
    level=config.get_log_level(),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(config.get_log_file_path(), encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

# 应用配置（保持不变）
app = FastAPI(
    title=config.APP_NAME,
    description="基于FastAPI、LangChain和DeepSeek的智能教务系统",
    version=config.APP_VERSION
)
app.mount("/static", StaticFiles(directory="static"), name="static")

origins = [
    "http://localhost:5173",
]

# Redis连接配置（保持不变）
try:
    redis_client = redis.Redis(**config.get_redis_config())
    redis_client.ping()
    logger.info(f"Redis连接成功 - 主机: {config.REDIS_HOST}:{config.REDIS_PORT}")
    REDIS_AVAILABLE = True
except Exception as e:
    logger.error(f"Redis连接失败: {e}")
    logger.warning("应用将在没有Redis的情况下运行，会话数据将不会持久化")
    redis_client = None
    REDIS_AVAILABLE = False

# 初始化LangChain的DeepSeek模型
try:
    # 初始化LangChain的DeepSeek聊天模型
    ehall_agent = EhallAgent(verbose=False)
    logger.info("LangChain DeepSeek模型初始化成功")
except Exception as e:
    logger.error(f"LangChain初始化失败: {e}")
    raise

# 数据模型、AI角色配置、工具函数
class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: float

class ChatRequest(BaseModel):
    user_id: str
    message: str
    session_id: str = None

class ChatResponse(BaseModel):
    session_id: str
    message: str
    timestamp: float

AI_ROLES = {
    "assistant": {
        "name": "智能助手",
        "prompt": "你是一个友善、专业的AI助手，能够帮助用户解答各种问题。请保持礼貌和耐心。"
    }
}

MAX_HISTORY_MESSAGES = config.MAX_HISTORY_MESSAGES
MAX_MESSAGE_LENGTH = config.MAX_MESSAGE_LENGTH
CONVERSATION_EXPIRE_TIME = config.CONVERSATION_EXPIRE_TIME
SESSION_EXPIRE_TIME = config.SESSION_EXPIRE_TIME

MEMORY_STORAGE = {
    "conversations": {},
    "sessions": {}
}

def generate_session_id() -> str:
    session_id = str(uuid.uuid4())
    logger.info(f"生成新会话ID: {session_id}")
    return session_id

def get_conversation_key(user_id: str, session_id: str) -> str:
    return f"conversation:{user_id}:{session_id}"

def get_user_sessions_key(user_id: str) -> str:
    return f"user_sessions:{user_id}"




# ---------- 新增接口（注册、登录） ----------
@app.post("/register", response_model=dict)
def register(user: UserCreate, db: Session = Depends(get_user_db)):
    db_user = get_db_user(db, user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="学号已注册"
        )
    create_db_user(db, user)
    return {"message": "注册成功，请登录"}

@app.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_user_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="学号或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# API接口（保持不变，与前端交互逻辑不受影响）
@app.get("/")
async def root():
    logger.info("访问根路径，重定向到聊天界面")
    return RedirectResponse(url="/static/index.html")

@app.get("/api")
async def api_info():
    return {"message": "FastAPI LangChain DeepSeek聊天应用演示", "version": "1.0.0"}