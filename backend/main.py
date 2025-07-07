from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# 导入我们的 agent 执行器
from agents.demo_agent import run_agent

# 初始化 FastAPI 应用
app = FastAPI(
    title="教务信息智能体 API",
    description="一个使用 LangChain 和 FastAPI 构建的智能教务助手",
    version="1.0.0"
)

# --- 配置跨域中间件 (CORS) ---
# 这允许你的 Vue 前端 (通常在不同的端口) 访问后端 API
origins = [
    "http://localhost:5173",  # 假设你的 Vue dev server 运行在这个地址
    # 如果有其他前端地址，也一并加入
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 定义 API 的请求体和响应体模型 ---
class ChatRequest(BaseModel):
    query: str
    # 你可以加入 conversation_id 等来实现多轮对话
    # chat_history: list = []

class ChatResponse(BaseModel):
    answer: str

# --- 创建 API 接口 ---
@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    """
    与教务智能体进行对话的接口
    """
    print(f"收到用户问题: {request.query}")
    # 调用 agent 执行器处理用户请求
    response_text = run_agent(request.query)
    print(f"Agent 回答: {response_text}")
    return ChatResponse(answer=response_text)

@app.get("/")
def read_root():
    return {"message": "欢迎使用教务信息智能体 API"}

# --- 运行服务器 ---
# 在终端中，进入 backend 目录，运行:
# uvicorn main:app --reload