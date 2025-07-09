# -*- coding: utf-8 -*-
"""
FastAPI 交小荣智能教务后端
"""

import json
import time
import uuid
import logging
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import FastAPI, HTTPException, Query, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import StreamingResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, String, Boolean
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, EmailStr, field_validator
import redis
from config import config
from passlib.context import CryptContext
from agents.demo import EhallAgent  
from crypto_utils import crypto 
from models import DBUser,Base

# ---------- 新增数据库配置（用户表） ----------
SQLALCHEMY_DATABASE_URL = "sqlite:///./users.db"  # 数据库文件存在backend目录
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
UserSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ---------- 新增JWT和密码加密配置 ----------
SECRET_KEY = config.get_secret_key() or "your-secret-key"  # 去config.py里加SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

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

# def verify_password(plain_password, hashed_password):
#     return pwd_context.verify(plain_password, hashed_password)

# def get_password_hash(password):
#     return pwd_context.hash(password)

def get_db_user(db: Session, username: str):
    return db.query(DBUser).filter(DBUser.username == username).first()

def create_db_user(db: Session, user: UserCreate):
    db_user = DBUser(
        username=user.username,
        email=user.email,
        encrypted_password=crypto.encrypt(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username: str, password: str):
    user = get_db_user(db, username)
    decrypted_password = crypto.decrypt(user.encrypted_password)
    if password != decrypted_password:
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 前端地址
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有请求头
)

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

async def save_message_to_redis(user_id: str, session_id: str, message: ChatMessage):
    """将消息保存到Redis或内存"""
    try:
        message_data = {
            "role": message.role,
            "content": message.content,
            "timestamp": message.timestamp
        }
        
        if REDIS_AVAILABLE and redis_client:
            # 使用Redis存储
            conversation_key = get_conversation_key(user_id, session_id)
            
            # 将消息添加到对话历史
            redis_client.lpush(conversation_key, json.dumps(message_data))
            
            # 设置过期时间
            redis_client.expire(conversation_key, config.CONVERSATION_EXPIRE_TIME)
            
            # 更新用户会话列表
            sessions_key = get_user_sessions_key(user_id)
            session_info = {
                "session_id": session_id,
                "last_message": message.content[:config.MAX_MESSAGE_LENGTH] + "..." if len(message.content) > config.MAX_MESSAGE_LENGTH else message.content,
                "last_timestamp": message.timestamp
            }
            redis_client.hset(sessions_key, session_id, json.dumps(session_info))
            redis_client.expire(sessions_key, config.SESSION_EXPIRE_TIME)
            
            logger.info(f"消息已保存到Redis - 用户: {user_id}, 会话: {session_id[:8]}..., 角色: {message.role}, 内容长度: {len(message.content)}")
        else:
            # 使用内存存储
            if user_id not in MEMORY_STORAGE["conversations"]:
                MEMORY_STORAGE["conversations"][user_id] = {}
            if session_id not in MEMORY_STORAGE["conversations"][user_id]:
                MEMORY_STORAGE["conversations"][user_id][session_id] = []
            
            MEMORY_STORAGE["conversations"][user_id][session_id].append(message_data)
            
            # 更新会话信息
            if user_id not in MEMORY_STORAGE["sessions"]:
                MEMORY_STORAGE["sessions"][user_id] = {}
            
            MEMORY_STORAGE["sessions"][user_id][session_id] = {
                "session_id": session_id,
                "last_message": message.content[:config.MAX_MESSAGE_LENGTH] + "..." if len(message.content) > config.MAX_MESSAGE_LENGTH else message.content,
                "last_timestamp": message.timestamp
            }
            
            logger.info(f"消息已保存到内存 - 用户: {user_id}, 会话: {session_id[:8]}..., 角色: {message.role}, 内容长度: {len(message.content)}")
            
    except Exception as e:
        logger.error(f"保存消息失败 - 用户: {user_id}, 会话: {session_id[:8]}..., 错误: {e}")
        raise

async def get_conversation_history(user_id: str, session_id: str) -> List[Dict[str, Any]]:
    """从Redis或内存获取对话历史"""
    try:
        if REDIS_AVAILABLE and redis_client:
            # 从Redis获取
            conversation_key = get_conversation_key(user_id, session_id)
            messages = redis_client.lrange(conversation_key, 0, -1)
            
            # 反转消息顺序（Redis中是倒序存储的）
            messages.reverse()
            
            history = [json.loads(msg) for msg in messages]
            logger.info(f"从Redis获取对话历史 - 用户: {user_id}, 会话: {session_id[:8]}..., 消息数量: {len(history)}")
            return history
        else:
            # 从内存获取
            if (user_id in MEMORY_STORAGE["conversations"] and 
                session_id in MEMORY_STORAGE["conversations"][user_id]):
                history = MEMORY_STORAGE["conversations"][user_id][session_id]
                logger.info(f"从内存获取对话历史 - 用户: {user_id}, 会话: {session_id[:8]}..., 消息数量: {len(history)}")
                return history
            else:
                logger.info(f"对话历史为空 - 用户: {user_id}, 会话: {session_id[:8]}...")
                return []
    except Exception as e:
        logger.error(f"获取对话历史失败 - 用户: {user_id}, 会话: {session_id[:8]}..., 错误: {e}")
        return []

async def generate_ai_response(messages: List[Dict[str, Any]]) -> str:
    """调用EhallAgent生成响应"""
    try:
        logger.info(f"生成AI响应 - 消息数量: {len(messages)}")
        
        # 转换历史消息为EhallAgent需要的格式: 列表 of (role, content) 元组
        chat_history = []
        for msg in messages[-MAX_HISTORY_MESSAGES:]:
            if msg["role"] == "user":
                chat_history.append(("human", msg["content"]))
            elif msg["role"] == "assistant":
                chat_history.append(("ai", msg["content"]))
        
        # 提取最新用户消息
        user_message = messages[-1]["content"] if messages and messages[-1]["role"] == "user" else "请回答"
        
        # 调用EhallAgent（同步方法，无需await）
        start_time = time.time()
        response = ehall_agent.run(
            user_input=user_message,
            chat_history=chat_history
        )
        latency = time.time() - start_time
        logger.info(f"AI响应生成成功 - 耗时: {latency:.2f}s, 长度: {len(response)}")
        return response
        
    except Exception as e:
        logger.error(f"生成AI响应失败: {e}")
        return "抱歉，处理请求时出现错误，请稍后再试。"
    
async def generate_streaming_response(user_id: str, session_id: str, user_message: str, role: str = "assistant", provider: Optional[str] = None, model: Optional[str] = None):
    """生成流式响应"""


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

@app.post("/chat/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    user_id = request.user_id.strip()
    session_id = request.session_id or generate_session_id()
    user_message = request.message.strip()
    
    # 可选：添加 user_id 格式校验（如是否为数字）
    if not user_id.isdigit():
        raise HTTPException(status_code=400, detail="用户ID必须为数字")
    
    if not user_message:
        raise HTTPException(status_code=400, detail="消息内容不能为空")
    
    logger.info(f"用户 {user_id} 发起聊天 - 会话: {session_id[:8]}..., 消息: {user_message[:50]}...")
    
    # 保存用户消息
    user_msg = ChatMessage(role="user", content=user_message, timestamp=time.time())
    await save_message_to_redis(user_id, session_id, user_msg)
    
    # 获取对话历史
    history = await get_conversation_history(user_id, session_id)
    
    # 生成AI响应
    ai_response = await generate_ai_response(history)
    
    # 保存AI响应
    ai_msg = ChatMessage(role="assistant", content=ai_response, timestamp=time.time())
    await save_message_to_redis(user_id, session_id, ai_msg)
    
    return ChatResponse(
        session_id=session_id,
        message=ai_response,
        timestamp=ai_msg.timestamp
    )