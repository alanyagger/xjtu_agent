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
import HeaderView from "@/components/HeaderView.vue";
import { UserFilled, Delete, Loading, DocumentCopy } from "@element-plus/icons-vue";
import { onBeforeUnmount, onMounted, ref, watch } from "vue";
import {
  getWebsocketUrl,
  ChatItem,
  WSReqParams,
  WSResParams,
  wsSendMsgFormat,
} from "@/ts/AiChatWebsocket.ts";
import { sparkConfig } from "@/config/config.ts";
import { ElMessage } from "element-plus";
import { copyToClipboard } from "@/utils/commonUtil.ts";



// 扩展ChatItem类型，增加历史记录关联ID
interface ExtendedChatItem extends ChatItem {
  historyId?: string; // 用于关联历史记录的唯一ID
}

// 历史记录数据结构：包含问题、关联ID和对应对话索引
interface HistoryItem {
  id: string; // 唯一ID
  question: string; // 问题内容
  userIndex: number; // 用户提问在chatList中的索引
}

// 状态定义
let sparkWS: WebSocket;
let chatList = ref<ExtendedChatItem[]>([]);// 存储所有对话（用户提问+AI回答）
let loadingIndex = ref<number | null | undefined>();
let problemText = ref<string>("");// 用户输入的问题
let wsMsgReceiveStatus = ref<"receiveIng" | "receiveFinished">();
const maxCharCount = ref<number>(300);
let sendBtnDisabled = ref(false);// 发送按钮是否禁用

// 历史记录相关
let chatHistory = ref<HistoryItem[]>([]); // 存储完整历史信息
let currentHistoryId = ref<string | null>(null); // 当前选中的历史记录ID

// 生成唯一ID用于关联历史记录和对话
const generateId = () => {
  return Date.now().toString(36) + Math.random().toString(36).substr(2, 5);
};

// 发送问题
const sendQuestion = () => {
  if (sendBtnDisabled.value || !problemText.value.trim()) {
    if (!problemText.value.trim()) ElMessage.warning("请输入内容");
    return;
  }

  if (wsMsgReceiveStatus.value !== "receiveIng") {
    // 生成唯一ID关联当前对话
    const historyId = generateId();
    // 保存用户提问到对话列表
    const userIndex = chatList.value.length;
    chatList.value.push({
      role: "user",
      content: problemText.value,
      historyId // 关联历史记录ID
    });

    // 保存到历史记录
    saveToHistory({
      id: historyId,
      question: problemText.value,
      userIndex // 记录用户提问在chatList中的索引
    });

    sendBtnDisabled.value = true;
    problemText.value = "";
    askSpark(historyId); // 传递ID用于AI回答关联
  }
};

// 保存到历史记录
const saveToHistory = (history: HistoryItem) => {
  // 限制历史记录数量（最多20条）
  if (chatHistory.value.length >= 20) {
    chatHistory.value.shift();
  }
  chatHistory.value.push(history);
};

// 点击历史记录跳转对应对话
const jumpToHistory = (history: HistoryItem) => {
  currentHistoryId.value = history.id; // 高亮当前选中项
  // 找到对应的用户提问元素
  const targetEl = document.querySelector(`[data-history-id="${history.id}"]`);
  if (targetEl) {
    // 滚动到目标元素（带平滑动画）
    targetEl.scrollIntoView({ behavior: "smooth", block: "center" });
    // 高亮目标对话（添加闪烁动画）
    targetEl.classList.add("highlight");
    setTimeout(() => targetEl.classList.remove("highlight"), 100);
  }
};

// 清空历史记录
const clearHistory = () => {
  chatHistory.value = [];
  currentHistoryId.value = null;
  ElMessage.success("历史记录已清空");
};

// 连接AI
const askSpark = (historyId: string) => {
  const wsUrl = getWebsocketUrl(sparkConfig);
  if (!("WebSocket" in window)) {
    ElMessage.error("不支持WebSocket");
    return;
  }

  sparkWS = new WebSocket(wsUrl as string);
  sparkWS.onopen = () => {
    const sendData: WSReqParams = wsSendMsgFormat(sparkConfig, chatList.value);
    sparkWS.send(JSON.stringify(sendData));
    // AI回答关联相同的历史ID
    chatList.value.push({
      role: "assistant",
      content: "",
      historyId
    });
    loadingIndex.value = chatList.value.length - 1;
  };
  
  sparkWS.onmessage = (res: MessageEvent) => {
    const resObj: WSResParams = JSON.parse(res.data);
    if (resObj.header.code !== 0) {
      ElMessage.error("提问失败");
      sparkWS.close();
      return;
    }
    wsMsgReceiveHandle(resObj);
  };

  sparkWS.onerror = () => ElMessage.error("连接失败");
  sparkWS.onclose = () => {};
};

// 处理AI响应
const wsMsgReceiveHandle = (res: WSResParams) => {
  const dataArray = res?.payload?.choices?.text || [];
  dataArray.forEach(item => {
    if (item?.content != null) {
      chatList.value[chatList.value.length - 1].content += item.content;
    }
  });

  if (res.payload.choices.status === 0) {
    problemText.value = "";
    wsMsgReceiveStatus.value = "receiveIng";
  } else if (res.payload.choices.status === 2) {
    wsMsgReceiveStatus.value = "receiveFinished";
    loadingIndex.value = null;
    sendBtnDisabled.value = false;
    sparkWS.close();
  }
};

// 重新回答功能（核心修改）
const reReply = (index: number) => {
  if (wsMsgReceiveStatus.value !== "receiveIng") {
    // 1. 找到对应的用户提问内容
    let userQuestion = '';
    let i = index - 1;
    while (i >= 0) {
      if (chatList.value[i].role === "user") {
        userQuestion = chatList.value[i].content;
        break;
      }
      i--;
    }

    if (!userQuestion) {
      ElMessage.warning("未找到对应的提问内容");
      return;
    }

    // 2. 生成新的历史记录ID（模拟新提问）
    const newHistoryId = generateId();
    
    // 3. 添加新的用户提问到聊天列表
    const newUserIndex = chatList.value.length;
    chatList.value.push({
      role: "user",
      content: userQuestion,
      historyId: newHistoryId
    });

    // 4. 在历史记录中添加新项
    saveToHistory({
      id: newHistoryId,
      question: userQuestion,
      userIndex: newUserIndex
    });

    // 5. 自动跳转到新添加的提问
    currentHistoryId.value = newHistoryId;
    setTimeout(() => {
      const targetEl = document.querySelector(`[data-history-id="${newHistoryId}"]`);
      if (targetEl) {
        targetEl.scrollIntoView({ behavior: "smooth", block: "center" });
        targetEl.classList.add("highlight");
        setTimeout(() => targetEl.classList.remove("highlight"), 100);
      }
    }, 0);

    // 6. 调用AI接口获取新回答
    sendBtnDisabled.value = true;
    askSpark(newHistoryId);
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

onMounted(() => {
  if (aiChatListRef.value) createMutationServer(aiChatListRef.value);
});

// 复制记录
const copyRecord = (item: { content: any }) => {
  copyToClipboard({
    content: item.content,
    success: () => ElMessage.success("复制成功"),
    error: () => ElMessage.error("复制失败")
  });
};

// 复制代码成功
const handleCopyCodeSuccess = () => ElMessage.success("复制成功");

// 删除记录
const deleteRecord = (index: number) => {
  if (!sendBtnDisabled.value) {
    const element = document.querySelector(`[data-index="${index}"]`);
    if (element) {
      element.classList.add("fade-out");
      setTimeout(() => chatList.value.splice(index, 1), 300);
    } else {
      chatList.value.splice(index, 1);
    }
  }
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

onBeforeUnmount(() => {
  problemTextWatcher();
  if (chatListObserver) chatListObserver.disconnect();
  if (sparkWS) sparkWS.close();
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