import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
import logging
from config import config
from dotenv import load_dotenv
import os
load_dotenv()
logger = logging.getLogger(__name__)

SMTP_SERVER = os.getenv("SMTP_SERVER") or "smtp.qq.com"
SMTP_PORT = os.getenv("SMTP_PORT") or 465
SMTP_USER = os.getenv("SMTP_USER")  or "your-email@qq.com"
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD") or "your-auth-code"  # 

def send_reminder_email(to_email: str, schedule_name: str, start_time: str):
    try:
        mail_msg = f"""
        <p>您好！</p>
        <p>您的日程 <strong>{schedule_name}</strong> 将于 <strong>{start_time}</strong> 开始。</p>
        <p>请做好准备。</p>
        """
        
        msg = MIMEText(mail_msg, 'html', 'utf-8')
        msg['From'] = formataddr(["交小荣智能教务助手", SMTP_USER])
        msg['To'] = formataddr(["用户", to_email])
        msg['Subject'] = f"日程提醒：{schedule_name}"

        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.set_debuglevel(0)  # 关闭调试日志
            server.login(SMTP_USER, SMTP_PASSWORD)
            
            # 分离邮件发送和 QUIT 阶段
            send_result = server.sendmail(SMTP_USER, [to_email], msg.as_string())
            
            # 只要 sendmail 返回空字典，说明邮件已成功入队
            if not send_result:
                logger.info(f"邮件发送成功到 {to_email}，内容：{schedule_name}")
                return True
            else:
                logger.error(f"邮件发送失败，返回结果：{send_result}")
                return False
                
    except smtplib.SMTPException as e:
        # 仅在发送阶段（login/sendmail）报错时返回 False
        if "login" in str(e).lower() or "sendmail" in str(e).lower():
            return False
        else:
            # QUIT 阶段的异常不影响邮件发送结果，仍返回 True
            return True
    except Exception as e:
        logger.error(f"未知异常：{str(e)}")
        return False