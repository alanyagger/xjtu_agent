# -*- coding: utf-8 -*-
import sys
import os

# 获取当前文件的目录（agents/）
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取 backend 目录（agents/ 的上一级目录）
backend_dir = os.path.dirname(current_dir)
# 将 backend 目录添加到 Python 搜索路径
sys.path.append(backend_dir)

from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from  config import config

from tools.ehall_tools import (
    get_my_courses,
    get_term_courses,
    get_grades,
    get_all_courses,
    get_empty_classrooms
)

# 导入我们上一步创建的工具


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
    
    def _initialize_llm(self) -> ChatOpenAI:
        """初始化大语言模型"""
        return ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            api_key=config.OPENAI_API_KEY,
        )
    
    def _get_tools(self) -> list:
        return [
            get_my_courses,
            get_term_courses,
            get_grades,
            get_all_courses,
            get_empty_classrooms,
        ]


    def _create_prompt(self) -> ChatPromptTemplate:
        """创建提示词模板"""
        prompt_template = """
        你是一个风趣幽默且乐于助人的教务信息助手。
        你的任务是根据用户的提问，调用合适的工具来查询信息，并以清晰、友好的方式回答。
        请使用中文回答问题。
        在调用工具后，对返回的JSON数据进行总结和美化，不要直接输出原始的JSON。你不能改动任何原始的数据，只进行格式上的美化，不要编造。
        你可以调用以下功能：
        1. get_my_courses(term)：当用户查询“我的课表”或“我xx学期的课表”或“个人课表”时使用。最终输出的是一个课程表格，课程时间地点是json文件中的"YPSJDD"，课程名称是"KCM"。
        2. get_term_courses(term)：当用户查询“全校课表”“某学期的所有课程”时使用。如果查询某一学期的全校课表，请将查询结果分页显示，每页显示10条课程。
        3. get_grades()：当用户提到“成绩”“分数”“绩点”等时使用。请不要随意输出，最终输出的成绩是原始json文件中的"ZCJ"，而不是"PSCJ"或"PMCJ"，学分是"XF"。输出课程名、成绩、学分和课程类型。
        4. get_empty_classrooms(...)：当用户提到“空闲教室”“哪里可以上自习”等关键词时使用。
        5. get_all_courses()：当用户提到“课程列表”“课程查询”等不限定学期的关键词时使用。
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
        """创建智能体执行器"""
        return AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=verbose
        )
    
    def run(self, user_input: str, chat_history: list = None) -> str:
        """
        执行智能体并获取回复
        :param user_input: 用户输入文本
        :param chat_history: 可选的历史对话记录
        :return: 智能体的文本回复
        """
        chat_history = chat_history or []
        result = self.agent_executor.invoke({
            "input": user_input,
            "chat_history": chat_history
        })
        return result["output"]


# ---- 本地测试 ----
if __name__ == '__main__':
    # 创建智能体实例（verbose=True 显示思考过程）
    agent = EhallAgent(verbose=False)
    
    print("你好，我是智能教务助手交小荣，有什么可以帮你的吗？（输入 exit 退出）")
    while True:
        user_query = input("You: ")
        if user_query.lower() == 'exit':
            break
        response = agent.run(user_query)
        print(f"Agent: {response}")