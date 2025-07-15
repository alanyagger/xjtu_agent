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
      <div 
        class="history-panel" 
        :class="{ 'show-panel': showHistory }"
        :style="{ zIndex: showHistory ? 10 : 1 }"
      >
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
        <!-- 历史记录切换按钮 -->
        <div class="toggle-history-btn" @click="toggleHistory">
          <el-icon v-if="showHistory || isMobile">
            <Menu />
          </el-icon>
          <el-icon v-else>
            <ArrowLeft />
          </el-icon>
          <span v-if="!isMobile">{{ showHistory ? '隐藏记录' : '显示记录' }}</span>
        </div>
        
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
              />
              <el-avatar
                v-if="item.role === 'assistant'"
                src="https://img1.baidu.com/it/u=2640995470,2945739766&fm=253&fmt=auto&app=120&f=JPEG?w=500&h=500"
                :size="40"
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
                <div class="ai-chat-operate-icons" :class="{ disabled: sendBtnDisabled }">
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
              :rows="isMobile ? 3 : 4"
              placeholder="在此输入您想要了解的内容..."
              @keydown.enter.exact.prevent="sendQuestion"
              @keydown.enter.shift.exact.prevent="problemText += '\n'"
              class="chat-input"
              :style="{ fontSize: isMobile ? '16px' : '13px' }"
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
                  :size="isMobile ? 'large' : 'default'"
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
// 导入组件和图标
import HeaderView from "@/components/HeaderView.vue";
import { UserFilled, Delete, Loading, DocumentCopy, Menu, ArrowLeft } from "@element-plus/icons-vue";
import { onBeforeUnmount, onMounted, ref, watch } from "vue";
import { ElMessage } from "element-plus";
import { copyToClipboard } from "@/utils/commonUtil.ts";
import { getToken } from "@/utils/auth.ts";

// 响应式相关状态
const isMobile = ref(false);
const showHistory = ref(false);

// 检查屏幕尺寸，判断是否为移动端（更精确的判断）
const checkScreenSize = () => {
  // 使用更精确的移动设备检测
  const userAgent = navigator.userAgent.toLowerCase();
  const mobileRegex = /mobile|android|iphone|ipad|ipod|blackberry|iemobile|opera mini/i;
  isMobile.value = mobileRegex.test(userAgent) || window.innerWidth <= 768;
  
  // 移动端默认隐藏历史记录
  if (isMobile.value) {
    showHistory.value = false;
  }
};

// 切换历史记录显示/隐藏
const toggleHistory = () => {
  showHistory.value = !showHistory.value;
  // 移动端切换历史记录时，禁用背景滚动
  document.body.style.overflow = showHistory.value ? 'hidden' : '';
};

// 组件挂载时检查屏幕尺寸
onMounted(() => {
  checkScreenSize();
  // 监听窗口大小变化
  window.addEventListener('resize', checkScreenSize);
  
  if (aiChatListRef.value) createMutationServer(aiChatListRef.value);
  // 初始化时尝试从本地存储恢复会话
  const savedSessionId = localStorage.getItem("chatSessionId");
  if (savedSessionId) {
    currentSessionId.value = savedSessionId;
  }
});

// 组件卸载时移除事件监听
onBeforeUnmount(() => {
  problemTextWatcher();
  if (chatListObserver) chatListObserver.disconnect();
  window.removeEventListener('resize', checkScreenSize);
  
  // 保存会话ID到本地存储
  if (currentSessionId.value) {
    localStorage.setItem("chatSessionId", currentSessionId.value);
  }
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
let currentSessionId = ref<string | null>(null); // 会话ID，用于保持上下文

// 生成唯一ID
const generateId = () => {
  return Date.now().toString(36) + Math.random().toString(36).substr(2, 5);
};

// 发送问题
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
  
  // 在移动端发送消息后自动隐藏键盘
  if (isMobile.value) {
    document.activeElement?.blur();
  }
};

// 调用后端/chat/接口
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
      user_id: localStorage.getItem("username") || "anonymous",
      message: userMessage,
      session_id: currentSessionId.value || ""
    };

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
        "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify(requestData)
    });

    if (!response.ok) {
      throw new Error(`请求失败: ${response.statusText}`);
    }

    const result = await response.json();
    // 更新会话ID
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
    
    // 移动端点击历史记录后自动隐藏历史面板
    if (isMobile.value) {
      showHistory.value = false;
      document.body.style.overflow = ''; // 恢复滚动
    }
  }
};

// 清空历史记录
const clearHistory = () => {
  chatHistory.value = [];
  currentHistoryId.value = null;
  currentSessionId.value = null;
  ElMessage.success("历史记录已清空");
  
  // 清空历史记录后关闭面板（移动端）
  if (isMobile.value) {
    showHistory.value = false;
    document.body.style.overflow = '';
  }
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
</script>

<style lang="scss" scoped>
// 头部样式
.page-layout-header {
  display: flex;
  justify-content: center;
  min-width: 100%;
  height: 66px;
  background: #fff;
  border-bottom: 1px solid #eee;
  box-shadow: 0 2px 8px 0 rgba(2, 24, 42, 0.1);
}

.page-layout-row {
  width: 100%;
  display: flex;
  background: #fff;
  flex-direction: column;
}

// 聊天容器样式
.ai-chat-view {
  display: flex;
  flex-direction: column; 
  justify-content: center;
  // background-color: #f0f7ff;
  background-image: url('/background.png'); /* 控制图片不重复平铺 */
  background-repeat: no-repeat; /* 让图片覆盖容器，按比例缩放尽量填满 */
  background-size: cover; /* 图片定位，可调整显示位置，比如居中 */
  min-height: 100vh;
  box-sizing: border-box;
  width: 100%;
  overflow-x: hidden; // 防止横向滚动

  .chat-container {
    display: flex;
    width: 100%;
    height: calc(100vh - 66px);
    box-shadow: 0 0 15px rgba(0, 0, 0, 0.08);
    border-radius: 12px;
    overflow: hidden;
    margin: 0 auto;
  }
}

// 历史记录切换按钮
.toggle-history-btn {
  position: absolute;
  top: 15px;
  left: 15px;
  z-index: 10;
  background-color: #fff;
  border: 1px solid #e5e9f2;
  border-radius: 20px;
  padding: 6px 12px;
  display: flex;
  align-items: center;
  cursor: pointer;
  font-size: 14px;
  color: #666;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
  transition: all 0.2s ease;

  // 增大移动端点击区域
  @media (max-width: 768px) {
    width: 44px;
    height: 44px;
    padding: 0;
    display: flex;
    justify-content: center;
    align-items: center;
  }

  &:hover {
    background-color: #f5f7fa;
    color: #4096ff;
  }

  el-icon {
    margin-right: 6px;
    font-size: 16px;

    @media (max-width: 768px) {
      margin-right: 0;
      font-size: 20px;
    }
  }

  span {
    @media (max-width: 768px) {
      display: none;
    }
  }
}

// 历史记录面板
.history-panel {
  width: 280px;
  /* 半透明背景 + 磨砂玻璃效果 */
  background-color: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px); /* Safari 兼容 */
  /* 半透明边框，弱化边缘 */
  border-right: 1px solid rgba(229, 233, 242, 0.2);
  display: flex;
  flex-direction: column;
  transition: transform 0.3s ease, width 0.3s ease;
  transform: translateX(0); // 默认隐藏
  // 在移动端占满屏幕
  @media (max-width: 768px) {
    width: 85%;
    max-width: 300px;
    box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
  }

  // 历史记录面板隐藏状态
  &:not(.show-panel) {
    transform: translateX(-100%);
    position: absolute;
    height: calc(100vh - 66px);
    z-index: 5;
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
    padding: 15px 20px; // 增加内边距，便于触摸
    font-size: 14px;
    cursor: pointer;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    transition: background-color 0.2s;
    
    // 增大移动端点击区域
    @media (max-width: 768px) {
      padding: 18px 20px;
      font-size: 15px;
    }
    
    &:hover {
      background-color: #f5f7fa;
    }
    
    &.active {
      background-color: #e6f7ff;
      font-weight: 500;
      border-left: 3px solid #1890ff;
    }
  }
}

// 右侧聊天主区域
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative; // 为了容纳绝对定位的切换按钮
  width: 100%;
}

// 对话列表
.ai-chat-list {
  display: flex;
  flex: 1;
  flex-direction: column;
  overflow-y: auto;
  padding: 20px 30px;
  padding-top: 45px; // 预留切换按钮空间
  scrollbar-width: thin;
  scrollbar-color: #d1d5db transparent;

  // 移动端调整内边距
  @media (max-width: 768px) {
    padding: 15px;
    padding-top: 60px;
  }

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

    // 移动端增加间距
    @media (max-width: 768px) {
      margin-bottom: 20px;
    }

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

    // 移动端增大头像
    @media (max-width: 768px) {
      margin-right: 10px;
    }

    .el-avatar {
      transition: transform 0.2s ease;

      // 移动端增大头像
      @media (max-width: 768px) {
        width: 44px !important;
        height: 44px !important;
      }

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
    font-size: 14px;

    // 移动端调整样式
    @media (max-width: 768px) {
      padding: 14px 18px;
      max-width: 85%;
      font-size: 16px;
      line-height: 1.6;
      border-radius: 14px;
    }

    // 初始化盒子样式
    &.init-box {
      background-color: #e6f7ff;
      box-shadow: 0 2px 8px rgba(0, 95, 219, 0.1);
      border: 1px solid #b3d8ff;

      // 移动端调整初始化消息
      @media (max-width: 768px) {
        padding: 16px 20px;
      }

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

        // 移动端调整字体
        @media (max-width: 768px) {
          font-size: 15px;
        }
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

      // 移动端调整操作区
      @media (max-width: 768px) {
        margin-top: 8px;
        font-size: 13px;
      }

      &:hover {
        opacity: 1;
      }

      // 重新回答按钮
      .re-reply-btn {
        color: #1890ff;
        cursor: pointer;
        transition: color 0.2s;

        // 移动端隐藏文字，保留图标
        @media (max-width: 768px) {
          display: none;
        }

        &:hover {
          color: #096dd9;
        }

        &.disabled {
          color: #ccc;
          cursor: not-allowed;
        }
      }

      // 操作图标容器（移动端优化）
      .ai-chat-operate-icons {
        display: flex;
        align-items: center;
        gap: 15px; // 增加图标间距

        // 移动端增大图标
        @media (max-width: 768px) {
          gap: 20px;
        }
      }

      // 操作图标
      .icon-btn {
        color: #8c8c8c;
        font-size: 14px;
        margin-left: 16px;
        cursor: pointer;
        transition: all 0.2s;

        // 移动端增大图标和点击区域
        @media (max-width: 768px) {
          font-size: 18px;
          margin: 0;
          width: 36px;
          height: 36px;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        &:hover {
          color: #1890ff;
          transform: scale(1.05);
        }
      }

      &.disabled .icon-btn {
        color: #ccc;
        cursor: not-allowed;
      }
    }
  }
}

// 发送问题表达
.ai-chat-form-wrapper {
  padding: 15px 30px 20px;
  /* 这里设置背景为白色且 90% 不透明，可根据需求调整最后一个数值 */
  background-color: rgba(255, 255, 255, 0.4); 
  border-top: 1px solid #e5e9f2;
  // 移动端调整内边距
  @media (max-width: 768px) {
    padding: 15px;
    padding-bottom: 20px;
    // 适配虚拟键盘
    position: sticky;
    bottom: 0;
    z-index: 5;
  }
}

.ai-chat-form-box {
  border: 1px solid #e5e6eb;
  border-radius: 12px;
  position: relative;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;

  // 移动端优化输入框样式
  @media (max-width: 768px) {
    border-radius: 16px;
  }

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
  background-color: rgba(249, 250, 252, 0.7);

  // 移动端优化
  @media (max-width: 768px) {
    padding: 18px 20px;
    font-size: 16px;
    border-radius: 16px;
    min-height: 50px;
  }

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

    // 移动端调整
    @media (max-width: 768px) {
      font-size: 16px;
    }
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

  // 移动端调整
  @media (max-width: 768px) {
    padding: 0 20px 15px;
  }

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

    // 移动端调整
    @media (max-width: 768px) {
      font-size: 13px;
    }
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

    // 移动端增大发送按钮
    @media (max-width: 768px) {
      min-width: 90px;
      height: 42px;
      font-size: 16px;
      border-radius: 8px;
    }

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

@keyframes highlight {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(64, 150, 255, 0);
  }
  50% {
    box-shadow: 0 0 0 5px rgba(64, 150, 255, 0.2);
  }
}

// 响应式设计
@media (max-width: 1024px) {
  .chat-container {
    flex-direction: column;
    height: auto;
  }
  
  .history-panel {
    position: absolute;
    height: calc(100vh - 66px);
    z-index: 5;
    transform: translateX(-100%);
  }
  
  .history-panel.show-panel {
    transform: translateX(0);
  }
  
  .chat-main {
    flex: 1;
    width: 100%;
  }
  
  .ai-chat-list {
    padding: 15px;
    padding-top: 45px;
  }
  
  .ai-chat-form-wrapper {
    padding: 15px;
  }
  
  .ai-chat-content-box {
    max-width: 85%;
  }
}

@media (max-width: 768px) {
  .ai-chat-view {
    padding: 0;
  }
  
  .chat-container {
    border-radius: 0;
    height: calc(100vh - 66px);
  }
  
  .ai-chat-content-box {
    max-width: 80%;
  }
  
  .toggle-history-btn {
    padding: 6px;
    
    span {
      display: none;
    }
    
    el-icon {
      margin-right: 0;
    }
  }

  // 修复移动端输入框被键盘遮挡问题
  .ai-chat-form-wrapper {
    position: sticky;
    bottom: 0;
    background-color: white;
  }

  // 确保在移动设备横屏时也有良好体验
  @media (orientation: landscape) and (max-width: 768px) {
    .ai-chat-list {
      max-height: calc(100vh - 180px);
    }
  }
}
</style>