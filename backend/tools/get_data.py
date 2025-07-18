# -*- coding: utf-8 -*-
import time
import json
import requests
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from get_assess import main11

LOGIN_URL = "https://ehall.xjtu.edu.cn/login"
#CHROME_DRIVER_PATH = "D://study//internship_2025//xjtu_agent\\backend\\tools\\chromedriver-win64\\chromedriver.exe" #官网下载chrome驱动，替换为自己的驱动路径
import os

# 获取当前脚本所在目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 修改为相对路径
CHROME_DRIVER_PATH = os.path.join(BASE_DIR, "chromedriver-win64", "chromedriver.exe")

campus_map = {
    "兴庆校区": "1",
    "雁塔校区": "2",
    "曲江校区": "3",
    "苏州校区": "4",
    "创新港校区": "5"
}

building_map = {
    "东1东": "1011",
    "东2": "1012",
    "主楼A": "1001",
    "主楼B": "1002",
    "主楼C": "1003",
    "主楼D": "1004",
    "中2": "1005",
    "中3": "1006",
    "西2东": "1007",
    "西2西": "1008",
    "外文楼A": "1010",
    "外文楼B": "1011",
    "仲英楼": "1013",
    "东1西": "1014",
    "教2西": "1015",
    "教2楼": "1016"
}

room_type_map = {
    "普通教室": "1",
}
func_map = {
    "个人课表": {
        "url": "https://ehall.xjtu.edu.cn/jwapp/sys/wdkb/modules/xskcb/xskcb.do",
        "data": lambda args: {
            "XNXQDM": args.term,
            "SKZC": 2,
            "XH": USERNAME
        },
        "referer": "https://ehall.xjtu.edu.cn/jwapp/sys/wdkb/*default/index.do"
    },
    "全校课程": {
        "url": "https://ehall.xjtu.edu.cn/jwapp/sys/kcbcx/modules/qxkcb/qxfbkccx.do",
        "data": lambda args: {
            # "pageSize": args.pageSize,
            # "pageNumber": args.pageNumber,
            "pageSize": 478,
            "pageNumber": 1,
            "querySetting": json.dumps([
                {"name": "XNXQDM", "value": args.term, "linkOpt": "and", "builder": "equal"},
                [
                    {"name": "RWZTDM", "value": "1", "linkOpt": "and", "builder": "equal"},
                    {"name": "RWZTDM", "linkOpt": "or", "builder": "isNull"}
                ]
            ]),
            "*order": "+KKDWDM,+KCH,+KXH"
        },
        "referer": "https://ehall.xjtu.edu.cn/jwapp/sys/kcbcx/*default/index.do"
    },
    "课程查询": {
        "url": "https://ehall.xjtu.edu.cn/jwapp/sys/kccx/modules/kccx/kcxxcx.do",
        "data": lambda args: {
            "KCZTDM": "1",
            # "pageSize": args.pageSize,
            # "pageNumber": args.pageNumber
            "pageSize": "12000",
            "pageNumber": "1"
        },
        "referer": "https://ehall.xjtu.edu.cn/jwapp/sys/kcbcx/*default/index.do"
    },
    "成绩查询": {
        "url": "https://ehall.xjtu.edu.cn/jwapp/sys/cjcx/modules/cjcx/xscjcx.do",
        "data": lambda args: {
            "querySetting": json.dumps([
                {"name": "SFYX", "caption": "是否有效", "linkOpt": "AND", "builderList": "cbl_m_List", "builder": "m_value_equal", "value": "1", "value_display": "是"},
                {"name": "XNXQDM", "value": "2024-2025-21", "builder": "notEqual", "linkOpt": "and"}
            ]),
            "pageSize": "100",
            "pageNumber": "1"
        },
        "referer": "https://ehall.xjtu.edu.cn/jwapp/sys/kcbcx/*default/index.do"
    },
    "空闲教室": {
        "url": "https://ehall.xjtu.edu.cn/jwapp/sys/kxjas/modules/kxjscx/cxkxjs.do",
        "data": lambda args: {
            "querySetting": json.dumps([
                {"name": "XXXQDM", "caption": "学校校区", "linkOpt": "AND", "builderList": "cbl_m_List", "builder": "m_value_equal", "value": campus_map[args.campus], "value_display": args.campus},
                {"name": "JXLDM", "caption": "教学楼", "linkOpt": "AND", "builderList": "cbl_m_List", "builder": "m_value_equal", "value": building_map[args.buildings], "value_display": args.buildings},
                {"name": "JASLXDM", "caption": "教室类型", "linkOpt": "AND", "builderList": "cbl_m_List", "builder": "m_value_equal", "value": room_type_map[args.room_type], "value_display": args.room_type},
                {"name": "KXRQ", "caption": "空闲日期", "linkOpt": "AND", "builderList": "cbl_Other", "builder": "equal", "value": args.date},
                {"name": "KXJC", "caption": "空闲节次", "builder": "lessEqual", "linkOpt": "AND", "builderList": "cbl_Other", "value": args.end},
                {"name": "KXJC", "caption": "空闲节次", "linkOpt": "AND", "builderList": "cbl_String", "builder": "moreEqual", "value": args.start}
            ], ensure_ascii=False),
            "XXXQDM": campus_map[args.campus],
            "JXLDM": building_map[args.buildings],
            "JASLXDM": room_type_map[args.room_type],
            "KXRQ": args.date,
            "JSJC": args.end,
            "KSJC": args.start,
            "pageSize": 100,
            "pageNumber": 1
        },
        "referer": "https://ehall.xjtu.edu.cn/jwapp/sys/kcbcx/*default/index.do"
    },
        
    "一键退学": {
        "url": "https://ehall.xjtu.edu.cn/jwapp/sys/xjydgl/*default/index.do",
        "data": lambda args: {},
        "referer": "https://ehall.xjtu.edu.cn/jwapp/sys/xjydgl/*default/index.do"
    },

    "培养方案":{"url": "https://ehall.xjtu.edu.cn/jwapp/sys/jwpubapp/modules/pyfa/kzkccx.do",
        "data": lambda args: {
            "PYFADM": "24ac40bb3d594cb0b1e036f7ce354120",
        },
        "referer": "https://ehall.xjtu.edu.cn/jwapp/sys/kcbcx/*default/index.do"
    },

    "自动评教": {
        "url": "https://ehall.xjtu.edu.cn/jwapp/sys/wspjyyapp/*default/index.do?",
        "data": lambda args: {},
        "referer": "https://ehall.xjtu.edu.cn/jwapp/sys/xjydgl/*default/index.do"
    }

    

}

def wait_for_mask_disappear(driver, url, timeout=30):
    #print("正在等待遮罩层消失...")
    try:
        WebDriverWait(driver, timeout).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".el-loading-mask")))
    except Exception:
        print("遮罩层可能未成功消失（或选择器不匹配）")

def save_json_to_file(data, filename="xjtu_course.json"):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"JSON数据已保存到：{filename}")
    except Exception as e:
        print(f"保存失败: {e}")

def selenium_login():
    options = ChromeOptions()
   
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    service = ChromeService(executable_path=CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)

    driver.minimize_window()  # 最小化
    #driver.set_window_position(-2000, 0)

    wait = WebDriverWait(driver, 20)

    driver.get(LOGIN_URL)
    time.sleep(1)
    #print(driver.page_source)  # 打印页面 HTML，用于调试
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[placeholder="学工号/手机号"]'))).send_keys(USERNAME)
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[placeholder="请输入登录密码"]'))).send_keys(PASSWORD + Keys.RETURN)

    time.sleep(2)
    driver.get("https://ehall.xjtu.edu.cn/jwapp/sys/wdkb/*default/index.do")
    wait_for_mask_disappear(driver, driver.current_url)
    time.sleep(2)

    if "login" in driver.current_url:
        driver.quit()
        raise Exception("登录失败")

    cookies = {c['name']: c['value'] for c in driver.get_cookies()}
    driver.quit()
    return cookies

def fetch_course(cookie_dict, func_name, args):
    cfg = func_map.get(func_name)
    if not cfg:
        print(f"Unknown function: {func_name}")
        return

    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://ehall.xjtu.edu.cn",
        "Referer": cfg["referer"],
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "X-Requested-With": "XMLHttpRequest",
    }

    data = cfg["data"](args)
    response = requests.post(cfg["url"], headers=headers, cookies=cookie_dict, data=data)

    if response.status_code == 200:
        try:
            json_data = response.json()
            print(f"✅ [{func_name}] 接口返回成功，解析并保存过滤后的 JSON：")
            
            # 字段筛选配置：按功能名称区分
            if func_name == "成绩查询":
                # 成绩查询：保留4个字段
                keep_fields = {
                    "KCM": "课程名称",
                    "ZCJ": "成绩",
                    "XF": "学分",
                    "KCXZDM_DISPLAY": "课程类型",
                    "XNXQDM": "学期"
                }
                target_key = "xscjcx"  # 成绩数据的外层键
            elif func_name == "课程查询":
                # 课程查询：保留4个字段
                keep_fields = {
                    "KCM": "开课名称",
                    "KKDWDM_DISPLAY": "开课学院",
                    "XS": "学时",
                    "XF": "学分"
                }
                target_key = "kcxxcx"  # 课程查询数据的外层键
            elif func_name == "全校课程":
                # 全校课程：保留6个字段
                keep_fields = {
                    "KCM": "开课名称",
                    "KKDWDM_DISPLAY": "开课学院",
                    "XS": "学时",
                    "XF": "学分",
                    "SKJS": "授课教师",
                    "XXXQDM_DISPLAY": "开课校区"
                }
                target_key = "qxfbkccx"  # 全校课程数据的外层键（根据实际JSON结构确定）
            elif func_name == "培养方案":
                keep_fields = {
                    "KCM": "开课名称",
                    "KCH": "课程号",
                    "KCXZDM_DISPLAY": "修读类型",
                    "KZM": "课程种类",
                    "KKDWDM_DISPLAY": "开课学院",
                    "XS": "学时",
                    "XF": "学分",
                    "XNXQ": "开课学期"
                }
                target_key = "kzkccx"
            else:
                # 其他功能不筛选
                keep_fields = None
                target_key = None

            # 执行筛选逻辑
            if keep_fields and target_key and "datas" in json_data and target_key in json_data["datas"] and "rows" in json_data["datas"][target_key]:
                filtered_rows = []
                for row in json_data["datas"][target_key]["rows"]:
                    # 提取并映射需要的字段（忽略不存在的字段）
                    filtered_row = {new_key: row[old_key] for old_key, new_key in keep_fields.items() if old_key in row}
                    filtered_rows.append(filtered_row)
                # 替换原始数据为筛选后的数据
                json_data["datas"][target_key]["rows"] = filtered_rows
                json_data["datas"][target_key]["totalSize"] = len(filtered_rows)  # 更新总条数

            save_json_to_file(json_data, f"{func_name}_data.json")
        except Exception as e:
            print(f"JSON解析失败: {e}")
    else:
        print(f"请求失败，状态码：{response.status_code}")
        print(response.text)

def handle_dropout(func):
    """自动打开界面"""
    options = ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    service = ChromeService(executable_path=CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)

    driver.maximize_window()
    wait = WebDriverWait(driver, 20)

    driver.get(LOGIN_URL)
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[placeholder="学工号/手机号"]'))).send_keys(USERNAME)
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[placeholder="请输入登录密码"]'))).send_keys(PASSWORD + Keys.RETURN)

    time.sleep(2)

    if "login" in driver.current_url:
        driver.quit()
        raise Exception("登录失败，请检查用户名和密码")

    # 成功登录
    print("✅ 登录成功")
    js = f'window.open("{func_map[func]["url"]}");'
    driver.execute_script(js)

    input("exit")
    driver.quit()
    


def main():
    parser = argparse.ArgumentParser(description="爬取西安交大教务系统数据")
    parser.add_argument("--username", required=True, help="统一认证用户名/学号")
    parser.add_argument("--password", required=True, help="统一认证密码")
    parser.add_argument("--func", type=str, required=True, help=f"功能名称，可选：{', '.join(func_map.keys())}")
    parser.add_argument("--term", type=str, help="学期，如 2024-2025-2")
    parser.add_argument("--campus", type=str, default="1", help="校区（用于空闲教室）")
    parser.add_argument("--buildings", type=str, default="1001", help="教学楼（可用逗号分隔）")
    parser.add_argument("--room_type", type=str, default="1", help="教室类型代码，默认普通教室")
    parser.add_argument("--date", type=str, default="2025-07-15", help="空闲教室日期")
    parser.add_argument("--start", type=str, default="1", help="起始节次")
    parser.add_argument("--end", type=str, default="8", help="结束节次")
    parser.add_argument("--pageSize", type=int, default=10, help="每页条数")
    parser.add_argument("--pageNumber", type=int, default=1, help="页码")

    args = parser.parse_args()
    
    global USERNAME, PASSWORD
    USERNAME = args.username
    PASSWORD = args.password
    
    print(f"Func: {args.func}")
    if (args.func == "自动评教"):
        main11(USERNAME, PASSWORD)
        return 

    elif (args.func == "一键退学"):
        handle_dropout(args.func)
        return
    cookies = selenium_login()
    fetch_course(cookies, args.func, args)
    

if __name__ == "__main__":
    main()
