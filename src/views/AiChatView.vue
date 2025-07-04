<script lang="ts" setup>
import { UserFilled } from "@element-plus/icons-vue";
import { onBeforeUnmount, onMounted, ref, watch } from "vue";
import {
  getWebsocketUrl,
  ChatItem,
  WSReqParams,
  WSResParams,
  wsSendMsgFormat,
} from "@/ts/AiChatWebsocket.ts";
import { sparkConfig } from "@/config/config.ts";
import { ElMessage, ElLoading } from "element-plus";
// 引入需要的图标
import { Loading, DocumentCopy, Delete } from "@element-plus/icons-vue";

// 定义websocket 实例
let sparkWS: WebSocket;
// 会话列表
let chatList = ref<ChatItem[]>([]);
// 加载当前回答的index
let loadingIndex = ref<number | null | undefined>();
// 提问问题内容
let problemText = ref<string>("");
// websocket 响应数据的状态
let wsMsgReceiveStatus = ref<"receiveIng" | "receiveFinished">();
// 提问的最大字数
const maxCharCount = ref<number>(300);
// 发送按钮的禁用状态
const sendBtnDisabled = ref(false);

// 发送问题的函数
const sendQuestion = () => {
  if (sendBtnDisabled.value) {
    // 阻止内容发送
    return;
  }
  if (problemText.value?.trim()?.length <= 0) {
    // 输入问题文字是空字符串的提示
    ElMessage.warning({ message: "请输入您想要了解的内容..." });
    return;
  }
  // 不在接受消息的时候才可以发送问题
  if (wsMsgReceiveStatus.value !== "receiveIng") {
    chatList.value.push({
      role: "user",
      content: problemText.value,
    });
    sendBtnDisabled.value = true;
    // 调用连接星火认知大模型并发送问题的函数
    askSpark();
  }
};

// 连接星火认知大模型并发送问题
const askSpark = () => {
  // 1. 生成鉴权URL
  let wsUrl = getWebsocketUrl(sparkConfig);
  // 2. 判断浏览器是否支持websocket
  if ("WebSocket" in window) {
    // 创建websocket 实例
    sparkWS = new WebSocket(wsUrl as string);
  } else {
    ElMessage.error("当前浏览器不支持websocket");
    return;
  }
  // 3. 建立websocket连接
  // 3.1 打开连接
  sparkWS.onopen = () => {
    // 发送数据
    const sendData: WSReqParams = wsSendMsgFormat(sparkConfig, chatList.value);
    console.log("发送数据", JSON.stringify(sendData));
    sparkWS.send(JSON.stringify(sendData));

    chatList.value.push({
      role: "assistant",
      content: "",
    });
    loadingIndex.value = chatList.value.length - 1;
  };
  // 3.2 消息监听
  sparkWS.onmessage = (res: MessageEvent) => {
    // 响应消息
    let resObj: WSResParams = JSON.parse(res.data);
    if (resObj.header.code !== 0) {
      ElMessage.error("提问失败");
      console.error(
        `提问失败：${resObj.header.code} - ${resObj.header.message}`
      );
      // 连接关闭
      sparkWS.close();
    } else {
      // 处理响应回来的数据
      wsMsgReceiveHandle(resObj);
    }
  };
  // 3.3 连接异常
  sparkWS.onerror = (e) => {
    ElMessage.error("WebSocket 连接失败");
    console.error(`WebSocket 连接失败,连接的URL${wsUrl}`, e);
  };
  // 3.4 连接关闭
  sparkWS.onclose = () => {};
};

/**
 * 处理websocket 返回的数据
 * @param res WSResParams
 */
const wsMsgReceiveHandle = (res: WSResParams) => {
  let dataArray = res?.payload?.choices?.text || [];
  for (let i = 0; i < dataArray.length; i++) {
    chatList.value[chatList.value.length - 1].content += dataArray[i].content;
  }
  // 开始接受消息
  if (res.payload.choices.status === 0) {
    problemText.value = "";
    wsMsgReceiveStatus.value = "receiveIng";
  }
  // 继续接受消息
  if (res.payload.choices.status === 1) {
    wsMsgReceiveStatus.value = "receiveIng";
  }
  // 接受消息完毕
  if (res.payload.choices.status === 2) {
    wsMsgReceiveStatus.value = "receiveFinished";
    loadingIndex.value = null;
    sendBtnDisabled.value = false;
    sparkWS.close();
  }
};

// 定义会话列表的观察对象（观察子元素的变化，当会话有变化时，自动滚动到变化的位置，用于提高用户的体验度）
let chatListObserver: MutationObserver;
// 聊天列表引用对象
const aiChatListRef = ref();

/**
 * 聊天列表变化的观察对象：用于监听目标元素的高度变化
 * @param targetElement
 */
const createMutationServer = (targetElement: Element) => {
  // 创建MutationServer 实例，用于监测Dom变化
  chatListObserver = new MutationObserver((mutationList, observer) => {
    // 当子元素变化发生变化时，获取元素滚动的高度
    const scrollHeight = targetElement.scrollHeight;
    // 调用滚动处理函数
    scrollHandle(scrollHeight);
  });
  // 启动检测器并配置所需的观察选项
  chatListObserver.observe(targetElement, { childList: true, subtree: true });
};

/**
 * 滚动定位处理
 * @param val
 */
const scrollHandle = (val: number) => {
  aiChatListRef.value?.scrollTo({
    // scrollTo 把内容滚动到指定的坐标
    top: val,
    behavior: "smooth", // 平滑滚动
  });
};

onMounted(() => {
  // 调用监听目标元素高度变化的函数
  if (aiChatListRef.value) {
    createMutationServer(aiChatListRef.value);
  }
});

// 导入复制内容到剪贴板的ts库
import { copyToClipboard } from "@/utils/commonUtil.ts";

/**
 * 复制会话内容到剪贴板
 * @param item
 * @param index
 */
const copyRecord = (item: { content: any }, index: any) => {
  const content = item.content;
  copyToClipboard({
    content,
    success() {
      ElMessage({
        message: "复制成功",
        type: "success",
      });
    },
    error() {
      ElMessage({
        message: "复制失败",
        type: "error",
      });
    },
  });
};

/**
 * markdown内容复制
 */
const handleCopyCodeSuccess = () => {
  ElMessage({
    message: "复制成功",
    type: "success",
  });
};

/**
 * 删除聊天记录
 * @param index
 */
const deleteRecord = (index: number) => {
  if (!sendBtnDisabled.value) {
    // 添加删除动画类
    const element = document.querySelector(`[data-index="${index}"]`);
    if (element) {
      element.classList.add('fade-out');
      // 等待动画完成后再删除数据
      setTimeout(() => {
        chatList.value.splice(index, 1);
      }, 300);
    } else {
      chatList.value.splice(index, 1);
    }
  }
};

/**
 * 重新回答
 */
const reReply = (index: number) => {
  if (wsMsgReceiveStatus.value !== "receiveIng") {
    // 如果是最后一条内容的重新回答，直接删除最后一条回答记录并重新作答
    if (chatList.value.length - 1 === index) {
      deleteRecord(index);
      sendBtnDisabled.value = true;
      askSpark();
    } else {
      // 如果不是最后一条重新回答，则在后面重新添加问题继续进行询问
      // 有可能上一条回答内容已被删除，所以需要循环找到最近的一条问题记录进行作答
      let i = index - 1;
      while (i >= 0) {
        // 角色为用户并且有问题内容
        if (chatList.value[i].role === "user" && chatList.value[i].content) {
          chatList.value.push({
            role: "user",
            content: chatList.value[index - 1].content,
          });
          sendBtnDisabled.value = true;
          askSpark();
          break;
        }
        i--;
      }
    }
  }
};

/**
 * 监听问题内容长度的函数
 */
const problemTextWatcher = watch(
  () => problemText.value,
  () => {
    // 限制最大字数
    if (problemText.value.length > maxCharCount.value) {
      problemText.value = problemText.value.slice(0, maxCharCount.value);
    }
  }
);

/**
 * 组件销毁之前的监听处理
 */
onBeforeUnmount(() => {
  // 停止监听问题内容长度
  problemTextWatcher();
  // 停止会话内容监听
  if (chatListObserver) {
    chatListObserver.disconnect();
  }
  // 关闭websocket连接
  if (sparkWS) {
    sparkWS.close();
  }
});
</script>

<template>
  <div class="ai-chat-view">
    <ul class="ai-chat-list" ref="aiChatListRef">
      <li class="ai-chat-item init-item">
        <!-- 头像 -->
        <div class="ai-chat-avatar">
          <el-avatar
            src="https://img1.baidu.com/it/u=2640995470,2945739766&fm=253&fmt=auto&app=120&f=JPEG?w=500&h=500"
            :size="40"
          />
        </div>
        <!-- 聊天内容 -->
        <div class="ai-chat-content-box init-box">
          <div class="ai-chat-title">AI助手</div>
          <div class="ai-chat-text">能够学习和理解人类的语言，进行多轮对话</div>
          <div class="ai-chat-text">
            回答问题，高效便捷地帮助人们获取信息、知识和灵感
          </div>
        </div>
      </li>
      <li
        class="ai-chat-item fade-in"
        :class="item.role + '-item'"
        v-for="(item, index) of chatList"
        :key="index"
        :data-index="index"
      >
        <!-- 头像 -->
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
        <!-- 聊天内容 -->
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
          <!-- 支持md 预览 -->
          <v-md-preview
            :text="item.content"
            @copy-code-success="handleCopyCodeSuccess"
          ></v-md-preview>
          <!-- 加载图标 -->
          <div class="loading-icon-box" v-if="loadingIndex === index">
            <el-icon>
              <Loading />
            </el-icon>
          </div>
          <div class="ai-chat-operate">
            <!--重新回答  -->
            <span
              class="re-reply-btn"
              @click="reReply(index)"
              :class="{ disabled: sendBtnDisabled }"
            >
              重新回答
            </span>
            <div
              class="operate-icon-box"
              :class="{ disabled: sendBtnDisabled }"
            >
              <!-- 聊天内容复制 -->
              <el-icon @click="copyRecord(item, index)" class="icon-btn">
                <DocumentCopy />
              </el-icon>
              <!-- 删除聊天内容 -->
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
        >
        </textarea>
        <div class="chat-form-footer">
          <div class="btns">
            <span class="content-tips">
              {{ problemText.length }} / {{ maxCharCount }}
              <template v-if="problemText.length >= maxCharCount">
                <span class="text-warning">已达最大字数</span>
              </template>
            </span>
            <span>
              <el-button
                type="primary"
                :disabled="sendBtnDisabled"
                @click="sendQuestion"
                class="send-btn"
                >发送</el-button
              >
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.ai-chat-view {
  display: flex;
  background-color: #f5f7fa;
  flex-direction: column;
  flex: 1;
  overflow: hidden;
  padding: 20px 30px;
  min-height: 100vh;
  box-sizing: border-box;

  // 对话列表
  .ai-chat-list {
    display: flex;
    flex: 1;
    flex-direction: column;
    overflow-y: auto;
    padding-right: 15px;
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
          margin-right: 0;
          margin-left: 25px;
        }
      }

      // 初始化消息项
      &.init-item {
        margin-bottom: 35px;
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
      padding: 16px 20px;
      position: relative;
      max-width: 80%;
      word-break: break-word;

      // 初始化盒子样式
      &.init-box {
        background-color: #e6f7ff;
        border-radius: 12px;
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
        margin-top: 12px;
        font-size: 12px;
        opacity: 0;
        transition: opacity 0.2s ease;

        // 鼠标悬停时显示操作按钮
        .ai-chat-content-box:hover & {
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
}

// 发送问题表达
.ai-chat-form-wrapper {
  padding: 20px 0;
  padding-left: calc(40px + 15px);

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
    font-size: 14px;
    line-height: 1.6;
    box-sizing: border-box;

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
@media (max-width: 768px) {
  .ai-chat-view {
    padding: 15px 10px;
  }

  .ai-chat-list .ai-chat-content-box {
    max-width: 70%;
  }

  .ai-chat-form-wrapper {
    padding-left: calc(40px + 5px);
  }
}
</style>