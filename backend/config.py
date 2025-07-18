# -*- coding: utf-8 -*-
"""
配置管理模块
集中管理应用的所有配置项
"""

import os
import logging
from typing import Optional
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from crypto_utils import crypto  # 导入加密工具
from models import DBUser  # 导入数据库模型
from thread_local import get_current_username
# 加载环境变量
load_dotenv()

class Config:
    """应用配置类"""
    
    # 应用配置
    DEBUG: bool = os.getenv('DEBUG', 'False').lower() == 'true'
    APP_NAME: str = os.getenv('APP_NAME', 'AI聊天应用演示')
    APP_VERSION: str = os.getenv('APP_VERSION', '1.0.0')
    
    # Redis配置
    REDIS_HOST: str = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT: int = int(os.getenv('REDIS_PORT', 6379))
    REDIS_PASSWORD: Optional[str] = os.getenv('REDIS_PASSWORD')
    REDIS_DB: int = int(os.getenv('REDIS_DB', 0))
    

    SECRET_KEY = os.getenv(
    "SECRET_KEY", 
    "default-jwt-secret-key-for-development-only-change-in-production"
        )  # JWT密钥，生产环境请修改为更复杂的字符串
    
    AES_SECRET_KEY = os.getenv(
        "AES_SECRET_KEY", 
        b'\x1f\x9b\x0c\x8a\x7d\x6e\x5f\x4a\x3b\x2c\x1d\x0e\xfa\xeb\xdc\xba'
        b'\x01\x23\x45\x67\x89\xab\xcd\xef\xfe\xdc\xba\x98\x76\x54\x32\x10'  # 共32字节
        )

    # 数据库配置
    SQLALCHEMY_DATABASE_URL = "sqlite:///./users.db"
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    def get_ehall_credentials(self):
        """从数据库获取教务处账号密码并解密"""

        # 获取当前线程ID，读取对应的学号
        username = get_current_username()
        
        if not username:
            raise ValueError("未获取到当前用户的学号")
        db = self.SessionLocal()
        try:
            user = db.query(DBUser).filter(DBUser.username == username).first()
            if not user:
                raise ValueError("数据库中没有找到用户")
                
            # 解密密码
            decrypted_password = crypto.decrypt(user.encrypted_password)
            return {
                "username": user.username,
                "password": decrypted_password
            }
        finally:
            db.close()


    @classmethod
    def get_secret_key(cls) -> str:
        return cls.SECRET_KEY

    # Redis过期时间配置（秒）
    CONVERSATION_EXPIRE_TIME: int = int(os.getenv('CONVERSATION_EXPIRE_TIME', 7 * 24 * 3600))  # 7天
    SESSION_EXPIRE_TIME: int = int(os.getenv('SESSION_EXPIRE_TIME', 30 * 24 * 3600))  # 30天
    
    # OpenAI配置
    OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY', '')
    OPENAI_BASE_URL: str = os.getenv('OPENAI_BASE_URL', '')
    OPENAI_MODEL: str = os.getenv('OPENAI_MODEL', '')
    OPENAI_MAX_TOKENS: int = int(os.getenv('OPENAI_MAX_TOKENS', 1000))
    OPENAI_TEMPERATURE: float = float(os.getenv('OPENAI_TEMPERATURE', 0.7))

    # DeepSeek配置
    DEEPSEEK_API_KEY: str = os.getenv('DEEPSEEK_API_KEY', '')
    DEEPSEEK_BASE_URL: str = os.getenv('DEEPSEEK_BASE_URL', '')
    
    # 对话配置
    MAX_HISTORY_MESSAGES: int = int(os.getenv('MAX_HISTORY_MESSAGES', 20))  # 最大历史消息数
    MAX_MESSAGE_LENGTH: int = int(os.getenv('MAX_MESSAGE_LENGTH', 50))  # 会话列表中显示的最大消息长度
    
    # 日志配置
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'DEBUG' if DEBUG else 'INFO')
    LOG_DIR: str = os.getenv('LOG_DIR', 'logs')
    LOG_FILE: str = os.getenv('LOG_FILE', 'app.log')
    
    # 服务器配置
    HOST: str = os.getenv('HOST', "127.0.0.1")
    PORT: int = int(os.getenv('PORT', 8000))
        
    @classmethod
    def get_redis_config(cls) -> dict:
        """获取Redis连接配置"""
        config = {
            'host': cls.REDIS_HOST,
            'port': cls.REDIS_PORT,
            'db': cls.REDIS_DB,
            'decode_responses': True
        }
        
        if cls.REDIS_PASSWORD:
            config['password'] = cls.REDIS_PASSWORD
            
        return config
    
    @classmethod
    def get_openai_config(cls) -> dict:
        """获取OpenAI客户端配置"""
        return {
            'api_key': cls.OPENAI_API_KEY,
            'base_url': cls.OPENAI_BASE_URL
        }
    
    @classmethod
    def get_log_level(cls) -> int:
        """获取日志级别"""
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        return level_map.get(cls.LOG_LEVEL.upper(), logging.INFO)
    
    @classmethod
    def validate_config(cls) -> None:
        """验证必需的配置项"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY环境变量未设置")
    
    @classmethod
    def get_log_file_path(cls) -> str:
        """获取日志文件完整路径"""
        return os.path.join(cls.LOG_DIR, cls.LOG_FILE)

# 创建配置实例
config = Config()