# scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models import DBSchedule, DBUser
from email_utils import send_reminder_email
import logging

# 配置日志
logger = logging.getLogger(__name__)

# scheduler.py
def check_upcoming_schedules():
    """检查即将开始的日程并发送提醒"""
    from main import UserSessionLocal
    db: Session = UserSessionLocal()
    try:
        now = datetime.now()
        ten_minutes_later = now + timedelta(minutes=10)
        
        # 查询未提醒的日程
        upcoming_schedules = db.query(DBSchedule).join(
            DBUser, DBSchedule.user_id == DBUser.username
        ).filter(
            DBSchedule.start_time >= now,
            DBSchedule.start_time <= ten_minutes_later,
            DBSchedule.reminder_sent == False
        ).all()
        
        logger.info(f"发现 {len(upcoming_schedules)} 个即将开始的日程需要提醒")
        
        for schedule in upcoming_schedules:
            user = db.query(DBUser).filter(DBUser.username == schedule.user_id).first()
            if not user or not user.email:
                logger.warning(f"用户 {schedule.user_id} 无邮箱，跳过")
                continue
            
            start_time_str = schedule.start_time.strftime("%Y-%m-%d %H:%M")
            
            # 发送邮件并判断是否成功
            if send_reminder_email(
                to_email=user.email,
                schedule_name=schedule.name,
                start_time=start_time_str
            ):
                # 邮件发送成功后，标记为已提醒
                schedule.reminder_sent = True
                db.commit()  # 提交修改到数据库
            else:
                logger.warning(f"邮件发送失败，{schedule.name} 下次仍会尝试提醒")
            
    except Exception as e:
        logger.error(f"检查日程失败：{str(e)}")
    finally:
        db.close()

def start_scheduler():
    """启动定时任务调度器"""
    scheduler = BackgroundScheduler()
    # 每1分钟检查一次
    scheduler.add_job(check_upcoming_schedules, 'interval', minutes=1)
    scheduler.start()
    logger.info("日程提醒调度器已启动")
    return scheduler