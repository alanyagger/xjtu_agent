import httpx
import os
from langchain.tools import tool
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()


# --- 模拟教务系统的爬虫类 ---
# 这个类负责登录和维持会话，具体的实现需要根据你的学校系统定制
class EhallScraper:
    def __init__(self, username, password):
        self.base_url = "https://ehall.your-university.edu"  # 换成你的学校域名
        self.username = username
        self.password = password
        # httpx.Client 可以像浏览器一样保持 cookie
        self.client = httpx.Client(base_url=self.base_url, timeout=20.0, follow_redirects=True)
        self._login()

    def _login(self):
        """
        模拟登录获取 cookie。
        【这是最需要定制的部分】
        你可能需要先 POST 用户名和密码到一个登录 URL，然后服务器会返回 Set-Cookie。
        httpx.Client 会自动处理这些 cookie。
        """
        try:
            # 这是一个示例，实际的 URL 和载荷需要你自己分析
            login_url = "/login_api"
            response = self.client.post(login_url, data={
                "username": self.username,
                "password": self.password
            })
            response.raise_for_status()  # 如果登录失败会抛出异常
            print("✅ 登录成功！")
        except Exception as e:
            print(f"❌ 登录失败: {e}")
            # 实际应用中应该处理这个错误

    def get_json_data(self, api_endpoint):
        """通用的获取 JSON 数据的方法"""
        try:
            response = self.client.get(api_endpoint)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": f"获取数据失败: {e}"}


# --- 实例化爬虫 ---
# 在真实应用中，这个实例应该被更好地管理（例如，单例模式），以避免重复登录。
scraper = EhallScraper(
    username=os.getenv("EHALL_USERNAME"),
    password=os.getenv("EHALL_PASSWORD")
)


# --- 定义 LangChain 工具 ---
# @tool 装饰器把一个普通 Python 函数变成了 LangChain Agent 可以使用的工具。
# 函数的 docstring (文档字符串) 非常重要！LLM 会读取它来理解这个工具的用途。

@tool
def get_current_semester_courses() -> dict:
    """
    获取当前学期的课程表信息。
    此工具不需要任何参数。
    它会返回一个包含课程信息的 JSON 对象。
    """
    # 假设这是你分析出来的课程 API 地址
    course_api = "/api/v1/courses/current"
    return scraper.get_json_data(course_api)


@tool
def get_grades_by_semester(semester: str) -> dict:
    """
    根据指定的学期查询成绩。
    例如，你可以查询 '2023-2024-1' 或 '2022-2023-2' 学期的成绩。
    参数 semester: 一个表示学期的字符串。
    """
    # 假设成绩 API 接受一个学期参数
    grade_api = f"/api/v1/grades?semester={semester}"
    return scraper.get_json_data(grade_api)

# 你可以根据需要添加更多工具，比如查询考试安排、空教室等。
# @tool
# def get_exam_schedule():
#     """获取本学期的考试安排"""
#     ...