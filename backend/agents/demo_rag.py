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
    get_empty_classrooms
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
            text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
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
        在调用工具后，对返回的JSON数据进行总结和美化，不要直接输出原始的JSON。你不能改动任何原始的数据，只进行格式上的美化，不要编造。如果查询成绩，最终输出的成绩是json文件中的"ZCJ"
        
        {knowledge_base_context}
        """
        
        # 如果有知识库，添加知识库提示
        knowledge_base_context = ""
        if self.knowledge_base:
            knowledge_base_context = "你可以利用本地知识库来回答关于课程介绍、专业设置等常见问题。"
        
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
    
    print("你好，我是教务助手，有什么可以帮你的吗？（输入 exit 退出）")
    while True:
        user_query = input("You: ")
        if user_query.lower() == 'exit':
            break
        response = agent.run(user_query)
        print(f"Agent: {response}")    