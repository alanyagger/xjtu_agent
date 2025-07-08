# -*- coding: utf-8 -*-
import sys
import os
import json
from typing import Dict, Any

# 更安全的路径处理方式
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)  # 使用insert(0)确保优先搜索

from langchain_deepseek import ChatDeepSeek
from langchain.agents import create_openai_tools_agent, AgentExecutor, tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage
from config import config

# ================= 工具函数实现 =================
@tool
def get_current_semester_courses(student_id: str) -> Dict[str, Any]:
    """获取当前学期的课程表信息"""
    # 示例数据 - 实际应用中应连接教务系统API
    return {
        "student_id": student_id,
        "semester": "2024-2025学年第二学期",
        "courses": [
            {"name": "高等数学", "time": "周一 1-2节", "location": "A101"},
            {"name": "大学英语", "time": "周三 3-4节", "location": "B203"},
            {"name": "计算机基础", "time": "周五 5-6节", "location": "C305"}
        ]
    }

@tool
def get_grades_by_semester(student_id: str, semester: str) -> Dict[str, Any]:
    """获取指定学期的成绩信息"""
    # 示例数据 - 实际应用中应连接教务系统API
    return {
        "student_id": student_id,
        "semester": semester,
        "grades": [
            {"course": "高等数学", "score": 92, "credit": 4},
            {"course": "大学英语", "score": 85, "credit": 3},
            {"course": "计算机基础", "score": 88, "credit": 3}
        ]
    }
# ================= 工具函数结束 =================

class EhallAgent:
    """教务信息智能体，封装了智能体的初始化和执行逻辑"""
    
    def __init__(self, verbose=True):
        """
        初始化智能体组件
        :param verbose: 是否显示详细执行过程（调试用）
        """
        self.llm = self._initialize_llm()
        self.tools = self._get_tools()
        self.prompt = self._create_prompt()
        self.agent = self._create_agent()
        self.agent_executor = self._create_agent_executor(verbose)
    
    def _initialize_llm(self) -> ChatDeepSeek:
        """初始化大语言模型 - 使用DeepSeek模型"""
        return ChatDeepSeek(
            model="deepseek-chat",
            temperature=0,
            api_key=config.DEEPSEEK_API_KEY,
            base_url=config.DEEPSEEK_BASE_URL,
        )
    
    def _get_tools(self) -> list:
        """获取工具列表"""
        return [get_current_semester_courses, get_grades_by_semester]

    def _create_prompt(self) -> ChatPromptTemplate:
        """创建更清晰的提示词模板"""
        prompt_template = """
        你是一个风趣幽默且乐于助人的教务信息助手，名字叫"教务小通"。
        你的任务是根据学生的提问，调用合适的工具查询信息，并以清晰友好的方式回答。
        
        重要提示：
        1. 使用中文回答，保持轻松幽默但专业的语气
        2. 调用工具后，对返回的JSON数据进行人性化总结，不要直接输出原始数据
        3. 如果用户没有提供必要参数（如学号/学期），需要礼貌地询问
        4. 遇到无法处理的问题时，不要编造信息
        
        你可以使用的工具：
        - get_current_semester_courses: 查询当前学期课表，需要学号
        - get_grades_by_semester: 查询学期成绩，需要学号和学期名称
        
        示例对话：
        用户：这学期我有哪些课？
        助手：同学你好！请先告诉我你的学号，我来帮你查课表~
        """
        return ChatPromptTemplate.from_messages([
            ("system", prompt_template),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
    
    def _create_agent(self):
        """创建智能体"""
        return create_openai_tools_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
    
    def _create_agent_executor(self, verbose: bool) -> AgentExecutor:
        """创建智能体执行器，添加错误处理"""
        return AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=verbose,
            handle_parsing_errors=True,  # 添加解析错误处理
            max_iterations=5  # 限制最大迭代次数
        )
    
    def run(self, user_input: str, chat_history: list = None) -> str:
        """
        执行智能体并获取回复
        :param user_input: 用户输入文本
        :param chat_history: 可选的历史对话记录
        :return: 智能体的文本回复
        """
        chat_history = chat_history or []
        try:
            result = self.agent_executor.invoke({
                "input": user_input,
                "chat_history": chat_history
            })
            return result["output"]
        except Exception as e:
            # 错误处理
            return f"哎呀，出错了！错误信息: {str(e)}。请稍后再试或联系管理员。"


# ---- 增强的本地测试 ----
if __name__ == '__main__':
    print("初始化教务助手...")
    agent = EhallAgent(verbose=True)
    
    print("\n你好，我是教务小通！输入 'exit' 退出")
    print("试试这些问题：")
    print("1. 我这学期有什么课？")
    print("2. 查询我上学期的成绩")
    print("3. 我的学号是2023001，查下这学期课表")
    
    chat_history = []
    while True:
        try:
            user_query = input("\nYou: ")
            if user_query.lower() in ['exit', 'quit']:
                break
                
            response = agent.run(user_query, chat_history)
            print(f"\n教务小通: {response}")
            
            # 更新对话历史
            chat_history.extend([
                HumanMessage(content=user_query),
                AIMessage(content=response)
            ])
        except KeyboardInterrupt:
            print("\n对话已终止")
            break
        except Exception as e:
            print(f"系统错误: {str(e)}")