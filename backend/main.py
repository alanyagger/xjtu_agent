# -*- coding: utf-8 -*-
"""
FastAPI 交小荣智能教务后端
"""

from models import DBUser, Base, DBSchedule
from sqlalchemy import DateTime, create_engine, Column, String, Boolean, Text, Integer, func
from sqlalchemy.orm import sessionmaker, Session
from config import config
from crypto_utils import crypto 
import os
from datetime import datetime
import uuid
import logging
from scheduler import start_scheduler

current_user_context = {}
# 数据库配置
SQLALCHEMY_DATABASE_URL = "sqlite:///./users.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
UserSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 数据库初始化单例
class DatabaseInitializer:
    _initialized = False
    
    @classmethod
    def initialize(cls):
        if not cls._initialized:
            # 创建所有表
            Base.metadata.create_all(bind=engine)
            # 插入初始用户（直接使用 DBUser 模型）
            cls._insert_default_user()
            
            cls._initialized = True
    
    @classmethod
    def _insert_default_user(cls):
        db = UserSessionLocal()
        try:
            if not db.query(DBUser).first():
                # 直接创建 DBUser 实例，绕过 UserCreate
                default_user = DBUser(
                    username="2021000000",
                    email="default@example.com",
                    # 使用 crypto 工具加密密码
                    encrypted_password=crypto.encrypt("default_password")
                )
                db.add(default_user)
                db.commit()
            if not db.query(DBSchedule).first():
                # 创建默认日程
                default_schedule = DBSchedule(
                    id=str(uuid.uuid4()),  # 使用 UUID 生成唯一 ID
                    user_id="2021000000",
                    name="默认日程",
                    start_time=datetime.fromisoformat("2023-10-01T08:00:00Z"),
                    end_time=datetime.fromisoformat("2023-10-01T09:00:00Z"),
                    color="#2097f3",
                    remark="这是一个默认日程"
                )
                db.add(default_schedule)
                db.commit()
        finally:
            db.close()

# 立即初始化数据库（在任何导入前）
DatabaseInitializer.initialize()


import json
import time
import uuid
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import FastAPI, HTTPException, Query, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import StreamingResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, field_validator
import redis
from passlib.context import CryptContext
from agents.demo_rag import EhallAgent  
from thread_local import set_current_username, get_current_username


# ---------- 数据库配置（用户表） ----------
SQLALCHEMY_DATABASE_URL = "sqlite:///./users.db"  # 数据库文件存在本地的backend目录
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
UserSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ---------- JWT和密码加密配置 ----------
SECRET_KEY = config.get_secret_key() or "your-secret-key"  
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

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

# ---------- 新增日程相关Pydantic模型 ----------
class ScheduleCreate(BaseModel):
    name: str
    start_time: str  # ISO格式字符串
    end_time: str    # ISO格式字符串
    color: Optional[str] = "#2097f3"
    remark: Optional[str] = ""
    
    @field_validator('start_time', 'end_time')
    def validate_datetime(cls, v):
        try:
            # 尝试解析ISO格式
            datetime.fromisoformat(v.replace("Z", "+00:00"))
            return v
        except ValueError:
            raise ValueError('日期时间格式错误，应为ISO 8601格式（如YYYY-MM-DDTHH:mm:ss）')


class ScheduleResponse(BaseModel):
    id: str
    name: str
    start_time: str
    end_time: str
    color: str
    remark: Optional[str]
    schedule_calendar: dict

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

def get_db_email(db: Session, email: str):
    return db.query(DBUser).filter(DBUser.email == email).first()

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
    allow_origins=origins,  # 前端地址
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
    kb_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend/data", "通识选课2.csv")
    ehall_agent = EhallAgent(verbose=False, knowledge_base_path=kb_path)
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


try:
    scheduler = start_scheduler()
    logger.info("日程提醒功能已启用")
except Exception as e:
    logger.error(f"启动日程提醒调度器失败：{e}")

# ---------- 新增接口（注册、登录） ----------
@app.post("/register", response_model=dict)
def register(user: UserCreate, db: Session = Depends(get_user_db)):
    db_user = get_db_user(db, user.username)
    db_emali = get_db_email(db, user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"field": "username", "msg": "学号已被注册"}
        )
    
    if db_emali:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"field": "email", "msg": "邮箱已被注册"}  # 返回错误字段和信息
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
    
    set_current_username(user_id)

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
    set_current_username(None)
    return ChatResponse(
        session_id=session_id,
        message=ai_response,
        timestamp=ai_msg.timestamp
    )

# ---------- 新增日程相关工具函数 ----------
def schedule_to_dict(schedule: DBSchedule) -> dict:
    """将数据库日程对象转换为前端需要的字典格式"""
    return {
        "id": schedule.id,
        "name": schedule.name,
        "start_time": schedule.start_time.strftime("%Y-%m-%dT%H:%M:%S"),
        "end_time": schedule.end_time.strftime("%Y-%m-%dT%H:%M:%S"),
        "color": schedule.color,
        "remark": schedule.remark,
        "schedule_calendar": {
            "color": schedule.color,
            "name": "默认日历"
        }
    }


def get_schedule_by_id(db: Session, schedule_id: str, user_id: str):
    """获取指定用户的指定日程"""
    return db.query(DBSchedule).filter(
        DBSchedule.id == schedule_id,
        DBSchedule.user_id == user_id
    ).first()


def create_schedule(db: Session, schedule: ScheduleCreate, user_id: str):
    """创建新日程"""
    try:
        start_time = datetime.fromisoformat(schedule.start_time.replace("Z", "+00:00"))
        end_time = datetime.fromisoformat(schedule.end_time.replace("Z", "+00:00"))
    except ValueError:
        raise HTTPException(status_code=400, detail="日期时间格式错误")
    
    if start_time >= end_time:
        raise HTTPException(status_code=400, detail="开始时间必须早于结束时间")
    
    db_schedule = DBSchedule(
        user_id=user_id,
        name=schedule.name,
        start_time=start_time,
        end_time=end_time,
        color=schedule.color,
        remark=schedule.remark
    )
    
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule

# ---------- 新增日历API接口 ----------
@app.get("/api/schedules/", response_model=List[dict])
def get_schedules(
    start: Optional[str] = Query(None, description="开始日期（YYYY-MM-DD）"),
    end: Optional[str] = Query(None, description="结束日期（YYYY-MM-DD）"),
    db: Session = Depends(get_user_db),
    current_user: DBUser = Depends(get_current_user)
):
    """获取当前用户的日程列表（支持日期范围筛选）"""
    query = db.query(DBSchedule).filter(DBSchedule.user_id == current_user.username)
    
    # 日期筛选
    if start and end:
        try:
            # 将输入的日期字符串转换为datetime对象，时间部分设为00:00:00
            start_date = datetime.strptime(start, "%Y-%m-%d")
            # 结束日期设为当天的23:59:59，覆盖一整天
            end_date = datetime.strptime(end, "%Y-%m-%d") + timedelta(hours=23, minutes=59, seconds=59)
            
            # 查询条件：日程的结束时间晚于开始日期，且日程的开始时间早于结束日期
            query = query.filter(
                DBSchedule.end_time >= start_date,
                DBSchedule.start_time <= end_date
            )
        except ValueError:
            raise HTTPException(status_code=400, detail="日期格式错误，应为YYYY-MM-DD")

    return [schedule_to_dict(s) for s in query.all()]

@app.post("/api/schedules/", response_model=dict)
def create_schedule_api(
    schedule: ScheduleCreate,
    db: Session = Depends(get_user_db),
    current_user: DBUser = Depends(get_current_user)
):
    """创建新日程（仅当前用户可见）"""
    try:
        # 验证时间逻辑
        start_time = datetime.fromisoformat(schedule.start_time.replace("Z", "+00:00"))
        end_time = datetime.fromisoformat(schedule.end_time.replace("Z", "+00:00"))
    except ValueError:
        raise HTTPException(status_code=400, detail="日期时间格式错误，应为ISO 8601格式")
    
    if start_time >= end_time:
        raise HTTPException(status_code=400, detail="开始时间必须早于结束时间")
    
    # 创建日程，关联当前用户
    new_schedule = create_schedule(db, schedule, current_user.username)
    return schedule_to_dict(new_schedule)


@app.delete("/api/schedules/{schedule_id}", response_model=dict)
def delete_schedule(
    schedule_id: str,
    db: Session = Depends(get_user_db),
    current_user: DBUser = Depends(get_current_user)
):
    """删除当前用户的日程"""
    schedule = get_schedule_by_id(db, schedule_id, current_user.username)
    
    if not schedule:
        raise HTTPException(status_code=404, detail="日程不存在或无权访问")
    
    db.delete(schedule)
    db.commit()
    return {"message": "日程已成功删除", "id": schedule_id}


@app.get("/api/schedules/search/", response_model=List[dict])
def search_schedules(
    keyword: str = Query(..., description="搜索关键词"),
    db: Session = Depends(get_user_db),
    current_user: DBUser = Depends(get_current_user)
):
    """搜索当前用户的日程（按标题或描述）"""
    schedules = db.query(DBSchedule).filter(
        DBSchedule.user_id == current_user.username,
        (DBSchedule.name.contains(keyword)) | 
        (DBSchedule.remark.contains(keyword))
    ).all()
    logger.info("f{schedules} schedules found for keyword '{keyword}'")
    
    return [schedule_to_dict(s) for s in schedules]

@app.get("/api/schedules/last-updated/", response_model=dict)
def get_last_schedule_update(
    db: Session = Depends(get_user_db),
    current_user: DBUser = Depends(get_current_user)
):
    """获取当前用户最后更新的日程时间戳"""
    # 查询当前用户所有日程中最新的更新时间
    last_updated = db.query(
        func.max(func.julianday(DBSchedule.end_time)).label('max_time')
    ).filter(DBSchedule.user_id == current_user.username).scalar()
    
    # 如果没有日程，返回当前时间戳
    if not last_updated:
        timestamp = datetime.now().timestamp()
    else:
        # 将Julian日期转换为Unix时间戳
        # SQLite的julianday从公元前4714年11月24日开始，需要转换偏移量
        timestamp = (last_updated - 2440587.5) * 86400
    
    return {
        "timestamp": str(int(timestamp)),  # 转为整数时间戳字符串
        "user_id": current_user.username
    }