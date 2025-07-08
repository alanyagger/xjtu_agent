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
from backend.config import config
# 导入我们上一步创建的工具
from backend.tools.ehall_tools import get_current_semester_courses, get_grades_by_semester


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
            model="gpt-4o",
            temperature=0,
            api_key=config.OPENAI_API_KEY,
        )
    
    def _get_tools(self) -> list:
        """获取工具列表"""
        return [get_current_semester_courses, get_grades_by_semester]
    
    def _create_prompt(self) -> ChatPromptTemplate:
        """创建提示词模板"""
        prompt_template = """
        你是一个风趣幽默且乐于助人的教务信息助手。
        你的任务是根据用户的提问，调用合适的工具来查询信息，并以清晰、友好的方式回答。
        请使用中文回答问题。
        在调用工具后，对返回的JSON数据进行总结和美化，不要直接输出原始的JSON。
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
    agent = EhallAgent(verbose=True)
    
    print("你好，我是教务助手，有什么可以帮你的吗？（输入 exit 退出）")
    while True:
        user_query = input("You: ")
        if user_query.lower() == 'exit':
            break
        response = agent.run(user_query)
        print(f"Agent: {response}")