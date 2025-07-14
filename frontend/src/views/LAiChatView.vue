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
        
        <!-- 通知公告区域 -->
        <div class="notifications-section">
          <div class="notifications-header">
            <h3>通知公告</h3>
          </div>
          <div class="notifications-list">
            <a 
              :href="notice.link" 
              class="notification-item" 
              v-for="(notice, index) of notifications" 
              :key="index"
              target="_blank"
            >
              <div class="notification-title">
                {{ notice.title }}
              </div>
              <div class="notification-time">{{ notice.publish_time }}</div>
            </a>
            
            <!-- 无通知时显示 -->
            <div class="no-notifications" v-if="notifications.length === 0">
              暂无通知
            </div>
          </div>
        </div>
      </div>
      
      <!-- 右侧聊天区域 -->
      <div class="chat-main">
        <!-- 日历快捷键 -->
        <div class="calendar-shortcut" @click="showCalendarInfo">
          <el-icon class="calendar-icon"><Calendar /></el-icon>
        </div>
        <!-- 移动端历史记录切换按钮 -->
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
              <div class="ai-chat-text">已登录成功，可就教务信息进行询问</div>
              <div class="ai-chat-text">所有数据均从ehall大厅获取</div>             
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
import HeaderView from "@/components/LHeaderView.vue";
import { UserFilled, Delete, Loading, DocumentCopy, Menu, ArrowLeft, Calendar, ExternalLink } from "@element-plus/icons-vue";
import { onBeforeUnmount, onMounted, ref, watch } from "vue";
import { ElMessage } from "element-plus";
import { copyToClipboard } from "@/utils/commonUtil.ts";
import { getToken } from "@/utils/auth.ts";
import { useRouter} from "vue-router";
const router = useRouter();

// 日历快捷键
const showCalendarInfo = () => {
  router.push("/calendar");
};

// 切换历史记录显示/隐藏
const toggleHistory = () => {
  showHistory.value = !showHistory.value;
  // 移动端切换历史记录时，禁用背景滚动
  document.body.style.overflow = showHistory.value ? 'hidden' : '';
};

// 组件挂载时初始化
onMounted(() => {
  // 检查登录状态
  const token = localStorage.getItem('token');
  isLoggedIn.value = !!token;
  
  // 初始化屏幕尺寸检测
  checkScreenSize();
  window.addEventListener('resize', checkScreenSize);
  
  if (aiChatListRef.value) createMutationServer(aiChatListRef.value);
  
  // 恢复会话ID
  const savedSessionId = localStorage.getItem("chatSessionId");
  if (savedSessionId) {
    currentSessionId.value = savedSessionId;
  }

  // 初始化通知公告数据
  initNotifications();
});

// 组件卸载时清理
onBeforeUnmount(() => {
  problemTextWatcher();
  if (chatListObserver) chatListObserver.disconnect();
  window.removeEventListener('resize', checkScreenSize);
  
  // 保存会话ID
  if (currentSessionId.value) {
    localStorage.setItem("chatSessionId", currentSessionId.value);
  }
});

// 类型定义
interface ExtendedChatItem {
  role: string;
  content: string;
  historyId?: string;
}

interface HistoryItem {
  id: string;
  question: string;
  userIndex: number;
}

// 通知公告类型定义（根据提供的数据格式）
interface NotificationItem {
  title: string;
  link: string;
  publish_time: string;
  isNew?: boolean;
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
let currentSessionId = ref<string | null>(null);

// 通知公告相关
let notifications = ref<NotificationItem[]>([]);

// 登录状态变量
const isLoggedIn = ref(false);

// 生成唯一ID
const generateId = () => {
  return Date.now().toString(36) + Math.random().toString(36).substr(2, 5);
};

// 初始化通知公告数据（使用提供的格式）
const initNotifications = () => {
  // 使用提供的通知数据
  notifications.value = [
    {
      "title": "[培养方案]关于启动2024级本科生劳动教育并继续做好2023级本科...",
      "link": "https://dean.xjtu.edu.cn/info/1176/8522.htm",
      "publish_time": "12-10",
      "isNew": true
    },
    {
      "title": "[学籍管理]2025年经济与金融学院接收本科生转专业考核安排",
      "link": "https://dean.xjtu.edu.cn/info/1095/9189.htm",
      "publish_time": "07-11",
      "isNew": true
    },
    {
      "title": "[竞赛安排]2025年全国大学生嵌入式芯片与系统设计竞赛FPGA创新...",
      "link": "https://dean.xjtu.edu.cn/info/1172/9187.htm",
      "publish_time": "07-10"
    },
    {
      "title": "[学籍管理]电子与信息学部计算机科学与技术（国家拔尖计划）202...",
      "link": "https://dean.xjtu.edu.cn/info/1095/9185.htm",
      "publish_time": "07-09"
    },
    {
      "title": "[学籍管理]电子与信息学部储能科学与工程（电磁储能）方向2025...",
      "link": "https://dean.xjtu.edu.cn/info/1095/9184.htm",
      "publish_time": "07-09"
    },
    {
      "title": "[学籍管理]法学院2025年转专业笔试和面试安排",
      "link": "https://dean.xjtu.edu.cn/info/1095/9183.htm",
      "publish_time": "07-08"
    },
    {
      "title": "[学籍管理]电气工程学院2025年本科生转专业宣讲会通知",
      "link": "https://dean.xjtu.edu.cn/info/1095/9182.htm",
      "publish_time": "07-08"
    },
    {
      "title": "[课程安排]关于开展中华民族共同体有关讲座的通知",
      "link": "https://dean.xjtu.edu.cn/info/1093/9181.htm",
      "publish_time": "07-07"
    }
  ];
};

// 发送问题
const sendQuestion = () => {
  if (sendBtnDisabled.value || !problemText.value.trim()) {
    if (!problemText.value.trim()) ElMessage.warning("请输入内容");
    return;
  }

  const historyId = generateId();
  // 添加用户提问
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
  
  // 移动端发送后隐藏键盘
  if (isMobile.value) {
    document.activeElement?.blur();
  }
  
  // 调用后端接口
  callChatApi(historyId, userMessage);
};

// 调用后端/chat/接口
const callChatApi = async (historyId: string, userMessage: string) => {
  try {
    const token = getToken();
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
    setTimeout(() => targetEl.classList.remove("highlight"), 100);
    
    // 移动端点击后隐藏历史面板
    if (isMobile.value) {
      showHistory.value = false;
      document.body.style.overflow = '';
    }
  }
};

// 清空历史记录
const clearHistory = () => {
  chatHistory.value = [];
  currentHistoryId.value = null;
  currentSessionId.value = null;
  ElMessage.success("历史记录已清空");
  
  // 移动端清空后关闭面板
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
        // 同步删除对应的AI回复
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

// 移动端检测和历史记录切换状态
const isMobile = ref(false);
const showHistory = ref(false);

// 检查屏幕尺寸，判断是否为移动端
const checkScreenSize = () => {
  // 结合用户代理和屏幕宽度判断
  const userAgent = navigator.userAgent.toLowerCase();
  const mobileRegex = /mobile|android|iphone|ipad|ipod|blackberry|iemobile|opera mini/i;
  isMobile.value = mobileRegex.test(userAgent) || window.innerWidth <= 768;
  
  // 移动端默认隐藏历史记录
  if (isMobile.value) {
    showHistory.value = false;
  } else {
    // 桌面端默认显示历史记录
    showHistory.value = true;
  }
};
</script>

<style lang="scss" scoped>
// 日历快捷键样式
.calendar-shortcut {
  position: absolute;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background-color: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  z-index: 10;

  &:hover {
    transform: translateY(-50%) scale(1.1);
    box-shadow: 0 4px 12px rgba(64, 150, 255, 0.2);
    background-color: #f0f7ff;
  }

  .calendar-icon {
    font-size: 20px;
    color: #4096ff;
  }
}

// 头部样式
.page-layout-header {
  display: flex;
  justify-content: center;
  min-width: 100%; // 适配移动端宽度
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
  background-color: #f0f7ff;
  min-height: 100vh;
  box-sizing: border-box;
  width: 100%;
  overflow-x: hidden; // 防止横向滚动

  .chat-container {
    display: flex;
    width: 100%;
    max-width: 1400px;
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
  background-color: #fff;
  border-right: 1px solid #e5e9f2;
  display: flex;
  flex-direction: column;
  transition: transform 0.3s ease, width 0.3s ease;
  transform: translateX(-100%); // 默认隐藏

  // 显示面板
  &.show-panel {
    transform: translateX(0);
  }

  // 移动端样式
  @media (max-width: 768px) {
    width: 85%;
    max-width: 300px;
    box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
    height: calc(100vh - 66px);
  }

  // 桌面端样式
  @media (min-width: 769px) {
    transform: translateX(0); // 桌面端默认显示
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
    max-height: 50%; // 限制历史记录高度，为通知区域留出空间
  }

  .history-item {
    padding: 15px 20px; // 增大触摸区域
    font-size: 14px;
    cursor: pointer;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    transition: background-color 0.2s;
    
    // 移动端优化
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

  // 通知公告区域样式
  .notifications-section {
    border-top: 1px solid #e5e9f2;
    padding: 10px 0;
    max-height: 50%;
    display: flex;
    flex-direction: column;

    .notifications-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 15px 20px 10px;
      border-bottom: 1px solid #f0f0f0;

      h3 {
        font-size: 15px;
        color: #333;
        margin: 0;
      }
    }

    .notifications-list {
      flex: 1;
      overflow-y: auto;
      padding: 10px 0;

      // 通知项样式 - 链接形式
      .notification-item {
        display: block;
        padding: 12px 20px;
        border-bottom: 1px solid #f5f5f5;
        color: inherit;
        text-decoration: none;
        transition: background-color 0.2s;

        &:hover {
          background-color: #f9f9f9;
        }

        .notification-title {
          font-size: 14px;
          font-weight: 500;
          margin-bottom: 5px;
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
          overflow: hidden;
          line-height: 1.5;
          position: relative;
          padding-right: 20px; // 为外部链接图标留出空间
        }

        .notification-time {
          font-size: 12px;
          color: #999;
          margin-top: 5px;
        }

        // 新通知标签
        .new-tag {
          display: inline-block;
          background-color: #ff4d4f;
          color: white;
          font-size: 12px;
          padding: 0 4px;
          border-radius: 3px;
          margin-left: 5px;
          vertical-align: middle;
        }

        // 外部链接图标
        &::after {
          content: '';
          position: absolute;
          right: 20px;
          top: 50%;
          transform: translateY(-50%);
          width: 14px;
          height: 14px;
          background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23999'%3E%3Cpath d='M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8z'/%3E%3Cpath d='M16 14v-2h2l-3-3-3 3h2v2h4z'/%3E%3C/svg%3E");
          background-size: contain;
          background-repeat: no-repeat;
        }
      }

      .no-notifications {
        padding: 20px;
        text-align: center;
        color: #999;
        font-size: 14px;
      }
    }
  }
}

// 右侧聊天区域
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #f9fafc;
  position: relative; // 容纳切换按钮
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

  // 移动端调整
  @media (max-width: 768px) {
    padding: 15px;
    padding-top: 45px;
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

    // 移动端调整
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

      // 移动端调整
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

        // 移动端调整
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

      // 移动端调整
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

        // 移动端隐藏文字按钮
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
        gap: 15px;

        // 移动端增大间距
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

// 发送区域
.ai-chat-form-wrapper {
  padding: 15px 30px 20px;
  background-color: #fff;
  border-top: 1px solid #e5e9f2;

  // 移动端调整
  @media (max-width: 768px) {
    padding: 15px;
    padding-bottom: 20px;
    // 固定在底部，适配虚拟键盘
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

  // 移动端优化
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
  background-color: #f9fafc;

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

// 发送按钮区域
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

    // 移动端增大按钮
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
  // 响应式下隐藏日历快捷键
  .calendar-shortcut {
    display: none;
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

  // 横屏适配
  @media (orientation: landscape) {
    .ai-chat-list {
      max-height: calc(100vh - 180px);
    }
  }
}
</style>
