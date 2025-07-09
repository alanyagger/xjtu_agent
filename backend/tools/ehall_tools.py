# -*- coding: utf-8 -*-
import os
import json
import subprocess
from langchain.tools import tool
from dotenv import load_dotenv

# 明确加载上一级目录下的 .env 文件
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

USERNAME = os.getenv("EHALL_USERNAME")
PASSWORD = os.getenv("EHALL_PASSWORD")

if not USERNAME or not PASSWORD:
    raise ValueError("请在 .env 文件中设置 EHALL_USERNAME 和 EHALL_PASSWORD")

# --- 工具函数：调用 get_data.py 并获取输出文件 ---
def call_get_data(func_name, extra_args=None):
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
    return call_get_data("成绩查询", {})

@tool
def get_all_courses() -> dict:
    """
    获取学校开设的全部课程。
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