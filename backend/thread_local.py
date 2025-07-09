import threading

# 创建线程本地存储
thread_local = threading.local()

def set_current_username(username: str):
    """设置当前线程的用户名"""
    thread_local.username = username

def get_current_username() -> str:
    """获取当前线程的用户名"""
    return getattr(thread_local, 'username', None)