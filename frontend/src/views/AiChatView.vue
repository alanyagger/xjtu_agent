<template>
  <div class="ai-chat-view">
    <!-- 头部区域 -->
    <header class="page-layout-header">
      <div class="page-layout-row">
        <HeaderView />
      </div>
    </header>
    
    <div class="chat-container">
      <!-- 左侧历史记录栏 -->
      <div class="history-panel">
        <div class="panel-header">
          <h3>历史记录</h3>
          <el-button 
            type="text" 
            @click="clearHistory" 
            class="clear-btn"
            :icon="Delete"
          >清空</el-button>
        </div>
        <div class="history-list">
          <div 
            class="history-item" 
            v-for="(history, historyIndex) of chatHistory" 
            :key="historyIndex"
            @click="jumpToHistory(history)"
            :class="{ active: currentHistoryId === history.id }"
          >
            {{ history.question }}
          </div>
        </div>
      </div>
      
      <!-- 右侧聊天区域 -->
      <div class="chat-main">
        <ul class="ai-chat-list" ref="aiChatListRef">
          <li class="ai-chat-item init-item">
            <!-- 初始化消息内容 -->
            <div class="ai-chat-avatar">
              <el-avatar
                src="https://img1.baidu.com/it/u=2640995470,2945739766&fm=253&fmt=auto&app=120&f=JPEG?w=500&h=500"
                :size="40"
              />
            </div>
            <div class="ai-chat-content-box init-box">
              <div class="ai-chat-title">交小荣</div>
              <div class="ai-chat-text">当前为未登录状态，可进行简单对话</div>
              <div class="ai-chat-text">如需获取教务相关信息，请先登录</div>
         
            </div>
          </li>
          <li
            class="ai-chat-item fade-in"
            :class="item.role + '-item'"
            v-for="(item, index) of chatList"
            :key="index"
            :data-index="index"
            :data-history-id="item.historyId"
          >
            <!-- 对话内容 -->
            <div class="ai-chat-avatar">
              <el-avatar
                v-if="item.role === 'user'"
                :icon="UserFilled"
                :size="40"
                class="user-avatar"
              />
              <el-avatar
                v-if="item.role === 'assistant'"
                src="https://img1.baidu.com/it/u=2640995470,2945739766&fm=253&fmt=auto&app=120&f=JPEG?w=500&h=500"
                :size="40"
                class="ai-avatar"
              />
            </div>
            <div
              class="ai-chat-content-box"
              :class="item.role + '-box'"
              v-if="item.role === 'user'"
            >
              {{ item.content }}
            </div>
            <div
              class="ai-chat-content-box"
              :class="item.role + '-box'"
              v-if="item.role === 'assistant'"
            >
              <v-md-preview
                :text="item.content"
                @copy-code-success="handleCopyCodeSuccess"
              ></v-md-preview>
              <div class="loading-icon-box" v-if="loadingIndex === index">
                <el-icon><Loading /></el-icon>
              </div>
              <div class="ai-chat-operate">
                <span
                  class="re-reply-btn"
                  @click="reReply(index)"
                  :class="{ disabled: sendBtnDisabled }"
                >
                  重新回答
                </span>
                <div class="operate-icon-box" :class="{ disabled: sendBtnDisabled }">
                  <el-icon @click="copyRecord(item, index)" class="icon-btn">
                    <DocumentCopy />
                  </el-icon>
                  <el-icon @click="deleteRecord(index)" class="icon-btn">
                    <Delete />
                  </el-icon>
                </div>
              </div>
            </div>
          </li>
        </ul>
        <!-- 文本发送区域 -->
        <div class="ai-chat-form-wrapper">
          <div class="ai-chat-form-box">
            <textarea
              v-model="problemText"
              :rows="4"
              placeholder="在此输入您想要了解的内容..."
              @keydown.enter.exact.prevent="sendQuestion"
              @keydown.enter.shift.exact.prevent="problemText += '\n'"
              class="chat-input"
            ></textarea>
            <div class="chat-form-footer">
              <div class="btns">
                <span class="content-tips">
                  {{ problemText.length }} / {{ maxCharCount }}
                  <template v-if="problemText.length >= maxCharCount">
                    <span class="text-warning">已达最大字数</span>
                  </template>
                </span>
                <el-button
                  type="primary"
                  :disabled="sendBtnDisabled"
                  @click="sendQuestion"
                  class="send-btn"
                >
                  发送
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// 导入HeaderView组件
import HeaderView from "@/components/HeaderView.vue";
import { UserFilled, Delete, Loading, DocumentCopy } from "@element-plus/icons-vue";
import { onBeforeUnmount, onMounted, ref, watch } from "vue";
import { ElMessage } from "element-plus";
import { copyToClipboard } from "@/utils/commonUtil.ts";
import { getToken } from "@/utils/auth.ts"; // 导入获取token的工具函数

// 新增：登录状态变量
const isLoggedIn = ref(false);

// 组件挂载时检测登录状态
onMounted(() => {
  // 检查localStorage中是否有token（与登录页逻辑一致）
  const token = localStorage.getItem('token');
  isLoggedIn.value = !!token; // 存在token则视为已登录

  if (aiChatListRef.value) createMutationServer(aiChatListRef.value);
});

// 扩展ChatItem类型，增加历史记录关联ID
interface ExtendedChatItem {
  role: string;
  content: string;
  historyId?: string;
}

// 历史记录数据结构
interface HistoryItem {
  id: string;
  question: string;
  userIndex: number;
}

// 状态定义
let chatList = ref<ExtendedChatItem[]>([]);
let loadingIndex = ref<number | null | undefined>();
let problemText = ref<string>("");
let sendBtnDisabled = ref(false);
const maxCharCount = ref<number>(300);

// 历史记录相关
let chatHistory = ref<HistoryItem[]>([]);
let currentHistoryId = ref<string | null>(null);
let currentSessionId = ref<string | null>(null); // 新增：会话ID，用于保持上下文

// 生成唯一ID
const generateId = () => {
  return Date.now().toString(36) + Math.random().toString(36).substr(2, 5);
};

// 发送问题（核心修改）
const sendQuestion = () => {
  if (sendBtnDisabled.value || !problemText.value.trim()) {
    if (!problemText.value.trim()) ElMessage.warning("请输入内容");
    return;
  }

  // 生成唯一ID关联当前对话
  const historyId = generateId();
  // 保存用户提问到对话列表
  const userIndex = chatList.value.length;
  chatList.value.push({
    role: "user",
    content: problemText.value,
    historyId
  });

  // 保存到历史记录
  saveToHistory({
    id: historyId,
    question: problemText.value,
    userIndex
  });

  const userMessage = problemText.value;

  sendBtnDisabled.value = true;
  problemText.value = "";
  // 调用后端/chat/接口
  callChatApi(historyId, userMessage);
};

// 调用后端/chat/接口（核心新增）
const callChatApi = async (historyId: string, userMessage: string) => {
  try {
    const token = getToken();
    console.log("当前token:", token);
    if (!token) {
      ElMessage.error("请先登录");
      sendBtnDisabled.value = false;
      return;
    }

    // 准备请求数据
    const requestData = {
      user_id: localStorage.getItem("userId") || "anonymous", // 从登录信息中获取用户ID
      message: userMessage,
      session_id: currentSessionId.value || "" // 传递当前会话ID保持上下文
    };

    // console.log("当前用户", localStorage.getItem("userId"));
    // console.log("请求问题:", userMessage);

    // 添加AI回复占位符
    const aiIndex = chatList.value.length;
    chatList.value.push({
      role: "assistant",
      content: "",
      historyId
    });
    loadingIndex.value = aiIndex;

    // 调用后端接口
    const response = await fetch("http://localhost:8000/chat/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}` // 添加认证头
      },
      body: JSON.stringify(requestData)
    });

    // console.log("请求数据:", requestData);
    // console.log("响应状态:", response.status);

    if (!response.ok) {
      throw new Error(`请求失败: ${response.statusText}`);
    }

    const result = await response.json();
    // 更新会话ID（首次请求会生成新ID，后续保持不变）
    currentSessionId.value = result.session_id;
    // 更新AI回复内容
    chatList.value[aiIndex].content = result.message;
    ElMessage.success("回复成功");

  } catch (error) {
    console.error("聊天接口调用失败:", error);
    ElMessage.error("获取回复失败，请重试");
    // 移除AI回复占位符
    if (chatList.value.length > 0) {
      chatList.value.pop();
    }
  } finally {
    loadingIndex.value = null;
    sendBtnDisabled.value = false;
  }
};

// 保存到历史记录
const saveToHistory = (history: HistoryItem) => {
  const isDuplicate = chatHistory.value.some(
    item => item.question === history.question
  );
  if (!isDuplicate) {
    if (chatHistory.value.length >= 10) chatHistory.value.shift();
    chatHistory.value.push(history);
  }
};

// 历史记录跳转
const jumpToHistory = (history: HistoryItem) => {
  currentHistoryId.value = history.id;
  const targetEl = document.querySelector(`[data-history-id="${history.id}"]`);
  if (targetEl) {
    targetEl.scrollIntoView({ behavior: "smooth", block: "center" });
    targetEl.classList.add("highlight");
    setTimeout(() => targetEl.classList.remove("highlight"), 2000);
  }
};

// 清空历史记录
const clearHistory = () => {
  chatHistory.value = [];
  currentHistoryId.value = null;
  currentSessionId.value = null; // 同时重置会话ID
  ElMessage.success("历史记录已清空");
};

// 重新回答
const reReply = (index: number) => {
  if (sendBtnDisabled.value) return;
  
  const targetItem = chatList.value[index];
  if (targetItem && targetItem.role === "assistant" && index > 0) {
    const userItem = chatList.value[index - 1];
    if (userItem && userItem.role === "user") {
      // 复用用户问题重新发送
      problemText.value = userItem.content;
      sendQuestion();
    }
  }
};

// 复制记录
const copyRecord = (item: { content: any }) => {
  copyToClipboard({
    content: item.content,
    success: () => ElMessage.success("复制成功"),
    error: () => ElMessage.error("复制失败")
  });
};

// 处理代码复制成功
const handleCopyCodeSuccess = () => ElMessage.success("复制成功");

// 删除记录
const deleteRecord = (index: number) => {
  if (!sendBtnDisabled.value) {
    const element = document.querySelector(`[data-index="${index}"]`);
    if (element) {
      element.classList.add("fade-out");
      setTimeout(() => {
        chatList.value.splice(index, 1);
        // 如果删除的是用户消息，同步删除对应的AI回复
        if (index < chatList.value.length && chatList.value[index].role === "assistant") {
          chatList.value.splice(index, 1);
        }
      }, 300);
    } else {
      chatList.value.splice(index, 1);
    }
  }
};

// 滚动相关
let chatListObserver: MutationObserver;
const aiChatListRef = ref();

const createMutationServer = (targetElement: Element) => {
  chatListObserver = new MutationObserver((_, observer) => {
    const scrollHeight = targetElement.scrollHeight;
    scrollHandle(scrollHeight);
  });
  chatListObserver.observe(targetElement, { childList: true, subtree: true });
};

const scrollHandle = (val: number) => {
  aiChatListRef.value?.scrollTo({ top: val, behavior: "smooth" });
};

// 监听输入长度
const problemTextWatcher = watch(
  () => problemText.value,
  () => {
    if (problemText.value.length > maxCharCount.value) {
      problemText.value = problemText.value.slice(0, maxCharCount.value);
    }
  }
);

// 生命周期
onMounted(() => {
  if (aiChatListRef.value) createMutationServer(aiChatListRef.value);
  // 初始化时尝试从本地存储恢复会话
  const savedSessionId = localStorage.getItem("chatSessionId");
  if (savedSessionId) {
    currentSessionId.value = savedSessionId;
  }
});

onBeforeUnmount(() => {
  problemTextWatcher();
  if (chatListObserver) chatListObserver.disconnect();
  // 保存会话ID到本地存储
  if (currentSessionId.value) {
    localStorage.setItem("chatSessionId", currentSessionId.value);
  }
});
</script>

<style lang="scss" scoped>
// 头部样式（从App.vue迁移）
.page-layout-header {
  display: flex;
  justify-content: center;
  min-width: 760px;
  height: 66px;
  background: #fff;
  border-bottom: 1px solid #eee;
  box-shadow: 0 2px 8px 0 rgba(2, 24, 42, 0.1);
}

.page-layout-row {
  width: 1440px;
  display: flex;
  background: #fff;
  flex-direction: column;
}

// 调整聊天容器样式（减去头部高度）
.ai-chat-view {
  display: flex;
  flex-direction: column; 
  justify-content: center;
  background-color: #f0f7ff;
  min-height: 100vh;
  box-sizing: border-box;

  .chat-container {
    display: flex;
    width: 100%;
    max-width: 1400px;
    /* 高度调整为减去头部高度 */
    height: calc(100vh - 66px);
    box-shadow: 0 0 15px rgba(0, 0, 0, 0.08);
    border-radius: 12px;
    overflow: hidden;
    margin: 0 auto; /* 居中显示 */
  }
}

// 历史记录选中样式增强
.history-item {
  &.active {
    background-color: #e6f7ff;
    font-weight: 500;
    border-left: 3px solid #1890ff; // 左侧高亮边框
  }
}

// 高亮动画
@keyframes highlight {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(64, 150, 255, 0);
  }
  50% {
    box-shadow: 0 0 0 5px rgba(64, 150, 255, 0.2); // 闪烁边框效果
  }
}

// 左侧历史记录面板
.history-panel {
  width: 280px;
  background-color: #fff;
  border-right: 1px solid #e5e9f2;
  display: flex;
  flex-direction: column;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #e5e9f2;
}

.clear-btn {
  padding: 0;
  font-size: 12px;
}

.history-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px 0;
}

.history-item {
  padding: 12px 20px;
  font-size: 14px;
  cursor: pointer;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: background-color 0.2s;
  
  &:hover {
    background-color: #f5f7fa;
  }
}

// 右侧聊天主区域
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #f9fafc;
}

// 对话列表
.ai-chat-list {
  display: flex;
  flex: 1;
  flex-direction: column;
  overflow-y: auto;
  padding: 20px 30px;
  scrollbar-width: thin;
  scrollbar-color: #d1d5db transparent;

  &::-webkit-scrollbar {
    width: 6px;
  }

  &::-webkit-scrollbar-thumb {
    background-color: #d1d5db;
    border-radius: 3px;
  }

  // 会话项
  .ai-chat-item {
    display: flex;
    align-items: flex-start;
    margin-bottom: 25px;
    position: relative;

    // 淡入动画
    &.fade-in {
      animation: fadeIn 0.3s ease-out forwards;
      opacity: 0;
    }

    // 删除动画
    &.fade-out {
      animation: fadeOut 0.3s ease-in forwards;
    }

    // 用户消息项
    &.user-item {
      flex-direction: row-reverse;

      .ai-chat-avatar {
        margin-right:10px;
        margin-left: 20px;
      }
    }

    // 初始化消息项
    &.init-item {
      display: flex;
      align-items: flex-start;
      margin-bottom: 25px;
      position: relative;
    }

    // 历史记录跳转高亮
    &.highlight {
      animation: highlight 0.2s ease-in-out;
    }
  }

  // 会话头像
  .ai-chat-avatar {
    margin-right: 15px;
    flex-shrink: 0;

    .el-avatar {
      transition: transform 0.2s ease;

      &:hover {
        transform: scale(1.05);
      }
    }

    .user-avatar {
      background-color: #4096ff;
    }

    .ai-avatar {
      background-color: #52c41a;
    }
  }

  // 会话盒子
  .ai-chat-content-box {
    padding: 12px 18px;
    position: relative;
    max-width: 80%;
    word-break: break-word;
    border-radius: 12px;

    // 初始化盒子样式
    &.init-box {
      background-color: #e6f7ff;
      box-shadow: 0 2px 8px rgba(0, 95, 219, 0.1);
      border: 1px solid #b3d8ff;

      .ai-chat-title {
        font-size: 18px;
        font-weight: 600;
        color: #1890ff;
        margin-bottom: 12px;
      }

      .ai-chat-text {
        font-size: 14px;
        color: #333;
        line-height: 1.6;
        margin-bottom: 8px;
      }
    }

    // 用户消息盒子
    &.user-box {
      background-color: #4096ff;
      color: #fff;
      border-radius: 12px 12px 4px 12px;
      box-shadow: 0 2px 8px rgba(64, 150, 255, 0.2);
    }

    // AI消息盒子
    &.assistant-box {
      background-color: #ffffff;
      border-radius: 12px 12px 12px 4px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
      border: 1px solid #f0f0f0;
    }

    // 加载图标盒子
    .loading-icon-box {
      padding: 10px 0;
      .el-icon {
        color: #4096ff;
        font-size: 18px;
        animation: rotate 1.5s linear infinite;
      }
    }

    // 会话操作
    .ai-chat-operate {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 1px;
      font-size: 12px;
      opacity: 0.3;
      transition: opacity 0.2s ease;

      // 鼠标悬停时显示操作按钮
      &:hover {
        opacity: 1;
      }

      // 重复回答按钮
      .re-reply-btn {
        color: #1890ff;
        cursor: pointer;
        transition: color 0.2s;

        &:hover {
          color: #096dd9;
        }

        &.disabled {
          color: #ccc;
          cursor: not-allowed;
        }
      }

      // 操作图标
      .operate-icon-box {
        display: flex;
        align-items: center;

        .icon-btn {
          color: #8c8c8c;
          font-size: 14px;
          margin-left: 16px;
          cursor: pointer;
          transition: all 0.2s;

          &:hover {
            color: #1890ff;
            transform: scale(1.1);
          }
        }

        &.disabled .icon-btn {
          color: #ccc;
          cursor: not-allowed;
        }
      }
    }
  }
}

// 发送问题表达
.ai-chat-form-wrapper {
  padding: 15px 30px 20px;
  background-color: #fff;
  border-top: 1px solid #e5e9f2;
}

.ai-chat-form-box {
  border: 1px solid #e5e6eb;
  border-radius: 12px;
  position: relative;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;

  &:focus-within {
    border-color: #4096ff;
    box-shadow: 0 0 0 3px rgba(64, 150, 255, 0.1);
  }
}

// 文本域
.chat-input {
  width: 100%;
  padding: 15px 15px 15px 15px;
  border: none;
  outline: none;
  resize: none;
  border-radius: 12px;
  color: #333;
  font-size: 13px;
  line-height: 1.6;
  box-sizing: border-box;
  background-color: #f9fafc;

  &::-webkit-scrollbar {
    width: 5px;
  }

  &::-webkit-scrollbar-thumb {
    background-color: #ddd;
    border-radius: 5px;
  }

  &::placeholder {
    color: #c9cdd4;
    font-size: 14px;
  }
}

// 发送问题表单footer
.chat-form-footer {
  display: flex;
  justify-content: flex-end;
  padding: 0 15px 15px;
  position: relative;
  bottom: 0;
  right: 0;
  box-sizing: border-box;

  // 内容数字提示
  .btns {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
  }

  .content-tips {
    font-size: 12px;
    color: #8c8c8c;
  }

  .text-warning {
    color: #faad14;
    margin-left: 8px;
  }

  .send-btn {
    min-width: 80px;
    height: 36px;
    border-radius: 6px;
    transition: all 0.2s ease;

    &:not(:disabled):hover {
      transform: translateY(-2px);
      box-shadow: 0 2px 8px rgba(64, 150, 255, 0.3);
    }

    &:not(:disabled):active {
      transform: translateY(0);
    }
  }
}

// 动画定义
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeOut {
  from {
    opacity: 1;
    transform: translateY(0);
  }
  to {
    opacity: 0;
    transform: translateY(10px);
    height: 0;
    margin-bottom: 0;
    overflow: hidden;
  }
}

@keyframes rotate {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

// 响应式设计
@media (max-width: 1024px) {
  .chat-container {
    flex-direction: column;
    height: auto;
  }
  
  .history-panel {
    width: 100%;
    max-height: 200px;
    border-right: none;
    border-bottom: 1px solid #e5e9f2;
  }
  
  .chat-main {
    flex: 1;
  }
}

@media (max-width: 768px) {
  .ai-chat-view {
    padding: 10px 0;
  }
  
  .chat-container {
    border-radius: 0;
  }
  
  .history-panel {
    max-height: 150px;
  }
  
  .ai-chat-list {
    padding: 15px;
  }
  
  .ai-chat-form-wrapper {
    padding: 15px;
  }
}
</style>