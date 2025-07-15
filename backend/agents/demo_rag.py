# -*- coding: utf-8 -*-
import sys
import os

# 获取当前文件的目录（agents/）
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取 backend 目录（agents/ 的上一级目录）
backend_dir = os.path.dirname(current_dir)
# 将 backend 目录添加到 Python 搜索路径
sys.path.append(backend_dir)

import pandas as pd
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import CSVLoader
from config import config

from tools.ehall_tools import (
    get_my_courses,
    get_term_courses,
    get_grades,
    get_all_courses,
    get_empty_classrooms,
    drop_out,
    get_scheme,
    add_schedule_db,
    judge_course
)


class EhallAgent:
    """教务信息智能体，封装了智能体的初始化和执行逻辑"""
    
    def __init__(self, verbose=True, knowledge_base_path=None):
        """
        初始化智能体组件
        :param verbose: 是否显示详细执行过程（调试用）
        :param knowledge_base_path: 本地知识库路径
        """
        self.llm = self._initialize_llm()
        self.tools = self._get_tools()
        self.knowledge_base = self._load_knowledge_base(knowledge_base_path)
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
        return [
            get_my_courses,
            get_term_courses,
            get_grades,
            get_all_courses,
            get_empty_classrooms,
            drop_out,
            add_schedule_db,  # 添加课程表工具
            get_scheme,
            judge_course,
        ]
    
    def _load_knowledge_base(self, knowledge_base_path) -> FAISS:
        """加载本地知识库"""
        if not knowledge_base_path:
            return None
            
        try:
            # 检查文件是否存在
            if not os.path.exists(knowledge_base_path):
                print(f"警告: 知识库文件 {knowledge_base_path} 不存在")
                return None
                
            # 加载CSV文件
            loader = CSVLoader(file_path=knowledge_base_path, encoding='utf-8')
            documents = loader.load()
            #print(documents[:100])
            
            # 文本分割
            text_splitter = CharacterTextSplitter(chunk_size=2000, chunk_overlap=0)
            texts = text_splitter.split_documents(documents)
            
            # 创建向量存储
            embeddings = OpenAIEmbeddings(api_key=config.OPENAI_API_KEY)
            vectorstore = FAISS.from_documents(texts, embeddings)
            
            return vectorstore
        except Exception as e:
            print(f"加载知识库时出错: {e}")
            return None
    
    def _create_prompt(self) -> ChatPromptTemplate:
        """创建提示词模板"""
        prompt_template = """
        你是一个风趣幽默且乐于助人的教务信息助手。
        你的任务是根据用户的提问，调用合适的工具来查询信息，并以清晰、友好的方式回答。
        请使用中文回答问题。
        在调用工具后，对返回的JSON数据进行总结和美化，不要直接输出原始的JSON。你不能改动任何原始的数据，只进行格式上的美化，不要编造。
        特别地，当展示课表信息时，请务必以每周日期的周视图形式进行排版，类似日历或课程表的样子，清晰展示每天的课程安排。
        你可以调用以下功能：
        1. get_my_courses(term)：当用户查询“我的课表”或“我xx学期的课表”或“个人课表”时使用。最终输出的是一个周课表格式的课程表格。输出课程名、上课时间、上课地点和授课教师。
            请将课程信息按星期和节次进行组织。
        2. get_term_courses(term)：当用户查询“全校课表”“某学期的所有课程”时使用。如果查询某一学期的全校课表，请将查询结果分页显示，每页显示10条课程。
        3. get_grades()：此工具用于查询用户的**所有学期课程成绩**和**计算并展示各学期及总体的平均分（绩点）**。
            当用户查询“成绩”、“分数”、“考试结果”、“均分”、“平均分”、“绩点”等相关信息时，请调用此工具。
            调用后，根据用户具体提问的侧重点，选择展示详细的课程成绩列表，或学期及总体的平均分数据，或两者都展示。请以清晰友好的方式呈现。及格线为60分。请对用户的成绩进行分级的评价，并计算百分制均分，做出鼓励或安慰。
        4. get_empty_classrooms(...)：当用户提到“空闲教室”“哪里可以上自习”等关键词时使用。
        5. get_all_courses()：当用户提到“课程列表”“所有课程查询”等不限定学期的关键词时使用。输出全部课程。
        6. drop_out()：当用户提到“退学”“休学”“延期毕业”等消极的关键词时使用。请安慰用户。
        7. add_schedule_db(name: str, start_time: str, end_time: str, user_id: str, color: str = "#2097f3", remark: str = "")：当用户提到“添加日程”“创建日程”等关键词时使用。请确保提供日程名称、开始时间、结束时间、用户ID（学号），并可选择性提供颜色和备注信息。
        8. get_scheme()：当用户提到“培养方案”“培养计划”等关键词时使用，如果用户提到“下学期的课表”“下学期的培养方案”等关键词时，请从json文件中找出“开课学期”为2025-2026-1的课程输出。
        9. judge_course()：当用户提到“评教”“自动评教”“帮我评教”等关键词使用。
        """
        
        # 如果有知识库，添加知识库提示
        knowledge_base_context = ""
        if self.knowledge_base:
            knowledge_base_context = "你可以利用本地知识库来回答关于学校规章制度、某个特定的选修课课程介绍、专业设置等常见问题。如果用户询问全部课程，你不能调用本地知识库。"
        
        prompt_template = prompt_template.format(knowledge_base_context=knowledge_base_context)
        
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
        
        # 如果有知识库，检索相关内容
        knowledge_base_results = ""
        if self.knowledge_base:
            try:
                docs = self.knowledge_base.similarity_search(user_input, k=3)
                if docs:
                    knowledge_base_results = "\n\n本地知识库参考内容:\n"
                    for i, doc in enumerate(docs, 1):
                        knowledge_base_results += f"{i}. {doc.page_content}\n"
            except Exception as e:
                print(f"检索知识库时出错: {e}")
        
        # 添加知识库内容到输入
        modified_input = user_input
        if knowledge_base_results:
            modified_input += knowledge_base_results
        
        result = self.agent_executor.invoke({
            "input": modified_input,
            "chat_history": chat_history
        })
        return result["output"]


# ---- 本地测试 ----
if __name__ == '__main__':
    # 假设知识库文件在data目录下
    kb_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "通识选课2.csv")
    
    # 创建智能体实例（verbose=True 显示思考过程）
    agent = EhallAgent(verbose=False, knowledge_base_path=kb_path)
    
    print("你好，我是智能教务助手交小荣，有什么可以帮你的吗？（输入 exit 退出）")
    while True:
        user_query = input("You: ")
        if user_query.lower() == 'exit':
            break
        response = agent.run(user_query)
        print(f"Agent: {response}")    