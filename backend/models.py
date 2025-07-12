# models.py
from sqlalchemy import Column, String, Boolean, Text, Integer, DateTime
import uuid
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# ---------- 数据库模型（用户表） ----------
class DBUser(Base):
    __tablename__ = "users"
    username = Column(String, primary_key=True, index=True)  # 学号
    email = Column(String, unique=True, index=True)
    encrypted_password = Column(String)  # 改为可逆加密的密码
    is_active = Column(Boolean, default=True)

class DBSchedule(Base):
    __tablename__ = "schedules"
    
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True, nullable=False)  # 关联到用户
    name = Column(String, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    color = Column(String, default="#2097f3")
    remark = Column(Text, nullable=True)
    calendar_id = Column(Integer, default=1)  # 日历分类ID
