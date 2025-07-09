# models.py
from sqlalchemy import Column, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# ---------- 数据库模型（用户表） ----------
class DBUser(Base):
    __tablename__ = "users"
    username = Column(String, primary_key=True, index=True)  # 学号
    email = Column(String, unique=True, index=True)
    encrypted_password = Column(String)  # 改为可逆加密的密码
    is_active = Column(Boolean, default=True)