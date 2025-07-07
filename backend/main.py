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
from datetime import datetime

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import redis
from config import config


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

# API接口（保持不变，与前端交互逻辑不受影响）
@app.get("/")
async def root():
    logger.info("访问根路径，重定向到聊天界面")
    return RedirectResponse(url="/static/index.html")

@app.get("/api")
async def api_info():
    return {"message": "FastAPI LangChain DeepSeek聊天应用演示", "version": "1.0.0"}