# -*- coding: utf-8 -*-
import os
import json
import subprocess
from langchain.tools import tool
from config import config
import webbrowser
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from models import DBSchedule  # 导入数据库模型
from sqlalchemy import create_engine

# --- 数据库连接配置 ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./users.db"  # 与FastAPI后端一致
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- 工具函数：调用 get_data.py 并获取输出文件 ---
def call_get_data(func_name, extra_args=None):
    credentials = config.get_ehall_credentials()
    USERNAME = credentials["username"]
    PASSWORD = credentials["password"]
    script_path = os.path.join(os.path.dirname(__file__), "get_data.py")
    args = ["python", script_path, "--username", USERNAME, "--password", PASSWORD, "--func", func_name]
    if extra_args:
        for k, v in extra_args.items():
            args.extend([k, v])
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    # print(f"执行命令: {' '.join(args)}")
    # print(f"当前工作目录: {os.getcwd()}")
    
    try:
        result = subprocess.run(
            args, 
            capture_output=True, 
            text=True, 
            check=True,
            timeout=300,  # 设置超时时间，避免脚本卡死
            env=env,
            encoding='utf-8',  # 明确指定编码
        )
        
        output_file = f"{func_name}_data.json"
        
        if os.path.exists(output_file):
            with open(output_file, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            # 列出当前目录下的所有文件，帮助定位问题
            current_files = os.listdir('.')
            return {"error": "没有找到输出文件，可能脚本内部出错", "cwd_files": current_files}
    except subprocess.CalledProcessError as e:
        return {"error": f"调用脚本失败: {e.stderr}", "returncode": e.returncode}
    except subprocess.TimeoutExpired:
        return {"error": "脚本执行超时"}
    except Exception as e:
        return {"error": f"未知错误: {str(e)}"}

def calculate_gpa(data):
    """
    计算各学期加权平均分和总平均分
    
    参数:
        data: 包含成绩数据的字典
    返回:
        包含各学期平均分和总平均分的字典
    """
    # 提取成绩列表
    scores = data['datas']['xscjcx']['rows']
    
    # 按学期分组
    term_scores = {}
    for score in scores:
        term = score['学期']
        # 跳过成绩为0的课程（可能是未完成或无效成绩）
        if score['成绩'] == 0:
            continue
        if term not in term_scores:
            term_scores[term] = []
        term_scores[term].append(score)
    
    # 计算各学期加权平均分
    term_gpa = {}
    total_credits = 0.0  # 总学分
    total_weighted_score = 0.0  # 总加权分数
    
    for term, courses in term_scores.items():
        term_credits = 0.0
        term_weighted = 0.0
        
        for course in courses:
            credit = course['学分']
            score = course['成绩']
            # 跳过学分为0的课程（如某些体育活动）
            if credit <= 0:
                continue
            
            term_credits += credit
            term_weighted += credit * score
        
        # 计算学期加权平均分
        if term_credits > 0:
            term_average = term_weighted / term_credits
            term_gpa[term] = {
                'average': round(term_average, 2),
                'total_credits': round(term_credits, 1),
                'course_count': len(courses)
            }
            
            # 累加至总学分和总加权分数
            total_credits += term_credits
            total_weighted_score += term_weighted
    
    # 计算总加权平均分
    total_average = round(total_weighted_score / total_credits, 2) if total_credits > 0 else 0
    
    sorted_term_gpa = dict(sorted(term_gpa.items(), key=lambda x: x[0]))

    return {
        'term_gpa': sorted_term_gpa,
        'total_average': total_average,
        'total_credits': round(total_credits, 1)
    }

# --- LangChain 工具函数封装 ---

@tool
def get_my_courses(term: str) -> dict:
    """
    获取某学期的个人课表。
    """
    return call_get_data("个人课表", {"--term": term})

@tool
def get_term_courses(term: str) -> dict:
    """
    获取某学期的全校课表。
    """
    return call_get_data("全校课程", {"--term": term})

@tool
def get_grades() -> dict:
    """
    获取全部学期的成绩。
    """
    scores_data = call_get_data("成绩查询", {})
    term_gpa = calculate_gpa(scores_data)
    return scores_data, term_gpa

@tool
def get_all_courses() -> list:
    """
    获取全部课程。
    """
    return call_get_data("课程查询", {})

@tool
def get_empty_classrooms(campus: str, buildings: str, date: str, start: str, end: str) -> dict:
    """
    查询指定时间段、校区、教学楼的空闲教室。
    参数
        campus: 校区中文名，例如 "兴庆校区"
        buildings: 教学楼中文名，例如 "主楼A"
        date: 日期，格式如 "2025-07-15"
        start: 起始节次，字符串数字
        end: 结束节次，字符串数字
    """
    return call_get_data("空闲教室", {
        "--campus": campus,
        "--buildings": buildings,
        "--date": date,
        "--start": start,
        "--end": end
    })

@tool
def drop_out() -> dict:
    """
    一键退学功能。
    当用户提到“退学”时，自动打开退学页面。
    """
    return call_get_data("一键退学", {})

@tool
def add_schedule_db(name: str, start_time: str, end_time: str, user_id: str, color: str = "#2097f3", remark: str = "") -> dict:
    """
    直接操作数据库添加新日程。
    参数:
        name: 日程名称
        start_time: 开始时间，ISO格式字符串，如 "2025-07-15T08:30:00"
        end_time: 结束时间，ISO格式字符串，如 "2025-07-15T09:30:00"
        user_id: 用户ID（学号）
        color: 日程颜色，十六进制颜色码，默认为 "#2097f3"
        remark: 日程备注，默认为空
    """
    credentials = config.get_ehall_credentials()
    user_id = credentials["username"]
    db = SessionLocal()
    try:
        # 转换时间格式
        start_time_obj = datetime.fromisoformat(start_time)
        end_time_obj = datetime.fromisoformat(end_time)
        
        # 验证时间逻辑
        if start_time_obj >= end_time_obj:
            return {"error": "开始时间必须早于结束时间"}
        
        # 创建日程对象
        new_schedule = DBSchedule(
            user_id=user_id,
            name=name,
            start_time=start_time_obj,
            end_time=end_time_obj,
            color=color,
            remark=remark
        )
        
        # 添加到数据库
        db.add(new_schedule)
        db.commit()
        db.refresh(new_schedule)
        
        # 返回成功信息
        return {
            "success": True,
            "schedule_id": new_schedule.id,
            "message": f"日程 '{name}' 已成功添加"
        }
    except Exception as e:
        db.rollback()
        return {"error": f"添加日程失败: {str(e)}"}
    finally:
        db.close()
