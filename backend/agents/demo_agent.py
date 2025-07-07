import os
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from dotenv import load_dotenv

# 导入我们上一步创建的工具
from backend.tools.ehall_tools import get_current_semester_courses, get_grades_by_semester

load_dotenv()

# 1. 初始化大语言模型 (LLM)
# 我们使用 OpenAI 的 gpt-4o 模型，因为它在工具使用方面表现很好
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0, # 温度设为0，让输出更稳定
    api_key=os.getenv("OPENAI_API_KEY")
)

# 2. 定义智能体的工具箱
# 把我们所有想让 Agent 使用的工具都放在一个列表里
tools = [get_current_semester_courses, get_grades_by_semester]

# 3. 创建 Prompt (提示词)
# 这是我们给 Agent 的指令，告诉它它的身份和该如何行动。
# MessagesPlaceholder 是一个占位符，后续会把对话历史和用户输入放进来。
prompt_template = """
你是一个风趣幽默且乐于助人的教务信息助手。
你的任务是根据用户的提问，调用合适的工具来查询信息，并以清晰、友好的方式回答。
请使用中文回答问题。
在调用工具后，对返回的JSON数据进行总结和美化，不要直接输出原始的JSON。
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", prompt_template),
    MessagesPlaceholder(variable_name="chat_history", optional=True), # 对话历史
    ("human", "{input}"), # 用户的当前输入
    MessagesPlaceholder(variable_name="agent_scratchpad"), # Agent 思考过程的记录区
])

# 4. 创建 Agent
# create_openai_tools_agent 是一个专门用于创建能使用工具的 Agent 的函数
agent = create_openai_tools_agent(llm, tools, prompt)

# 5. 创建 Agent 执行器 (AgentExecutor)
# AgentExecutor 负责实际运行 Agent，循环执行"思考->行动"的过程
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True # 设置为 True 可以在终端看到 Agent 的思考过程，便于调试
)

# 我们可以创建一个简单的函数来调用它
def run_agent(user_input: str, chat_history: list = None):
    """运行智能体并返回结果"""
    chat_history = chat_history or []
    result = agent_executor.invoke({
        "input": user_input,
        "chat_history": chat_history
    })
    return result["output"]

# # ---- 本地测试 ----
# if __name__ == '__main__':
#     print("你好，我是教务助手，有什么可以帮你的吗？（输入 exit 退出）")
#     while True:
#         user_query = input("You: ")
#         if user_query.lower() == 'exit':
#             break
#         response = run_agent(user_query)
#         print(f"Agent: {response}")