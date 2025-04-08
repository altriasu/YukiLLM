<template>
  <div class="ai-practice-container">
    <!-- 左侧历史对话记录 -->
    <div class="history-panel">
      <div class="new-chat-container">
        <button class="new-chat-btn" @click="newConversation">
          新建任务
          <el-icon class="plus-icon">
            <Plus />
          </el-icon>
        </button>
      </div>
      <ul class="history-list">
        <li
          v-for="(item, index) in historyList"
          :key="index"
          @click="selectConversation(index)"
          :class="{ active: currentConversationIndex === index }"
        >
          <span class="history-list-title">
          {{ item.title }}
          </span>
          <input v-if="isInputTitle === index" v-model = InputTitleValue class="inputTitle"></input>
          <el-icon @click.stop="editItem(index)" class="history-list-icon history-list-edit"><Edit /></el-icon>
          <el-icon v-show="chatCount > 1" @click.stop="deleteItem(index)" class="history-list-icon history-list-delete"><Delete /></el-icon>
        </li>
      </ul>
    </div>

    <!-- 右侧对话页面 -->
    <div class="chat-wrapper">
      <div class="chat-panel">
        <!-- 上半部分聊天界面 -->
        <div class="chat-messages" ref="chatMessagesRef">
          <div
            v-for="(message, index) in currentConversation.messages"
            :key="index"
            :class="['message', message.role]"
          >
            <div class="avatar">
              <div v-if="message.role !== 'user'" class="ai-avatar">
                <img src="@/assets/images/hailuo2.png" alt="AI Avatar" />
              </div>
              <div v-else>
                <img src="@/assets/images/user.png" alt="Me" />
              </div>
            </div>
            <div class="content">
              <div v-html="renderMarkdown(message.content)" class="message-text"></div>
              <div class="image-container">
                <img v-for="(img, index) in message.images" :key="index" :src="img" class="streamed-img"/>
              </div>
            </div>
          </div>
        </div>

        <!-- 输入框 -->
        <div class="input-area">
          <div class="input-wrapper">
            <el-icon @click="triggerFileInput('file')" v-if="isTxt2ImgRetrieve" class="input-icon">
              <input type="file" ref="fileInput" style="display: none" @change="handleFileUpload" />
              <DocumentAdd />
            </el-icon>
            <el-icon @click="triggerFileInput('file')" v-else class="input-icon">
              <input type="file" ref="fileInput" style="display: none" @change="handleFileUpload" />
              <Picture/>
            </el-icon>
            <input
              v-model="userInput"
              @keyup.enter="sendMessage"
              placeholder="输入消息，按回车发送..."
              type="text"
              :disabled="isInputDisabled"
            />
            <div class="button-group">
              <div class="separator"></div>
              <el-popover
                placement="top"
                :width="200"
                trigger="hover"
                :disabled="!!userInput.trim()"
              >
                <template #reference>
                  <el-button
                    class="send-button"
                    circle
                    @click="sendMessage"
                    :disabled="!userInput.trim()"
                  >
                    <el-icon>
                      <Top />
                    </el-icon>
                  </el-button>
                </template>
                <span>请上传图片/文字回复</span>
              </el-popover>
            </div>
          </div>
        </div>

        <div class="disclaimer">
          服务生成的所有内容均由程序自动生成，其生成内容的准确性和完整性无法保证
        </div>
      </div>
    </div>
    <div v-if="isShowConfTask"  class="backdrop"></div>
      <div v-if="isShowConfTask" class="pop-window">
          <ConfTask @emitClosePopWindow="closePopWindow" @emitConfirm="createNewConversation"/>
      </div>
    </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted, onBeforeUnmount } from "vue";
import { Link, Microphone } from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";
import { get, post } from "@/utils/request";
import { BASE_URL, API } from "@/api/config";
import { v4 as uuidv4 } from 'uuid';

import { useApiConfigStore } from "@/stores/apiConfig";
import { renderMarkdown } from "@/assets/js/markdown";
import ConfTask from "@/views/content/components/ConfTask.vue";

const apiConfigStore = useApiConfigStore();
const historyList = ref([
  {
    title: "直接使用大模型",
    task_id: "default",
    messages: [
      {
        role: "assistant",
        content:
          `您好！我是${apiConfigStore.config[0].platform}平台的${apiConfigStore.config[0].modelName}，你可以向我提出一些问题？`,
      },
    ],
  },
]);

// <---------------------------------- 弹窗 -------------------------------------------->
const currentConversationIndex = ref(0);
const userInput = ref("");
const isListening = ref(false);
const chatMessagesRef = ref(null);
const isInputDisabled = ref(false);
const isTxt2ImgRetrieve = ref(false);
const isShowConfTask = ref(false);
let chatCount = ref(1)

const openPopWindow = () => {
  isShowConfTask.value = true;
}

const closePopWindow = (value) => {
  isShowConfTask.value = value;
}

const newConversation = () => {
  openPopWindow();
};


// <---------------------------------- 新建任务 ------------------------------------------->
const createNewConversation = (flag, taskId) => {
  closePopWindow();
  historyList.value.unshift({
    title: "新任务",
    task_id: taskId,
    // 实际上这里要和后端交互的话，messages 最好用 map 格式，key 是对应的 id，这样方便后端根据 id 来操作消息
    messages: [
      {
        role: "assistant",
        content:
          "您好！我是蟹堡王的神奇海螺，很高兴为您服务！我可以回答关于蟹堡王和汉堡制作的任何问题，您有什么需要帮助的吗？",
      },
    ],
  });
  currentConversationIndex.value = 0;
  chatCount.value = chatCount.value + 1;
}

const isInputTitle = ref(null);
const InputTitleValue = ref("");
let editIndex = null;


const editItem = (index) => {
  isInputTitle.value = index;
  editIndex = index;
  InputTitleValue.value = historyList.value[index].title;
}

const deleteItem = (index) => {
  historyList.value.splice(index, 1);
  currentConversationIndex.value = 0;
  chatCount.value = chatCount.value - 1;
}

const currentConversation = computed(
  () => historyList.value[currentConversationIndex.value]
);

const selectConversation = (index) => {
  currentConversationIndex.value = index;
  nextTick(() => {
    scrollToBottom();
  });
};


// <---------------------------------- 发送信息 ------------------------------------------->
const fileInput = ref(null);
let uploadFile = null;

const triggerFileInput = () => {
  fileInput.value.click()
}

const handleFileUpload = (event) => {
  uploadFile = event.target.files[0];
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function typeWriter(text, message, delay = 10) {
  for (let char of text) {
    await sleep(delay);
    message.content += char;
  }
}



const useEmbeding = async (taskConfig) => {
  const formdata = new FormData();
  formdata.append("dataset_name", taskConfig.dataset);
  formdata.append("task_id", taskConfig.id);
  formdata.append("retrieve_type", taskConfig.task);
  formdata.append("file", uploadFile)

  const loadingMessage = ref({
    role: "assistant",
    content: "检索开始...<br>",
    loading: true, // 标记为加载状态
    images: []
  });

  fetch(BASE_URL + API.REMOTECLIP, {
    method: 'POST',
    body: formdata
  })
  .then(response => {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    function read() {
      reader.read().then(async ({ done, value }) => {
        if (done) return;

        buffer += decoder.decode(value, { stream: true });
        const parts = buffer.split("\n\n");
        buffer = parts.pop();

        for (const part of parts) {
          try {
            const msg = JSON.parse(part);

            if (msg.type === "progress") {
              await typeWriter(`检索中...${msg.data}`, loadingMessage.value);
            } else if (msg.type === "hint") {
              await typeWriter(msg.data, loadingMessage.value);
            } else if (msg.type === "result_img") {
              loadingMessage.value.images.push(msg.data);
            } else if (msg.type === "result_txt") {
              await typeWriter(msg.data, loadingMessage.value);
            } else if (msg.type === "error") {
              loadingMessage.value.content = "检索失败，请稍后重试";
            }
          } catch (e) {
            console.error("JSON parse error", e);
          }
        }

        read();
      });
    }

    read();
  });

  currentConversation.value.messages.push(loadingMessage.value);
  nextTick(() => {
    scrollToBottom();
  });
}

const useLLM = async (taskConfig) => {
  const loadingMessage = ref({
    role: "assistant",
    content: "思考中，请稍候...<br>",
    loading: true, // 标记为加载状态
    images: []
  });

  const formdata = new FormData();
  formdata.append("platform", taskConfig.platform);
  formdata.append("model", taskConfig.modelName);
  formdata.append("taskId", taskConfig.id);
  formdata.append("messages", JSON.stringify(historyList.value[currentConversationIndex.value].messages));
  if (uploadFile) {
    formdata.append("img", uploadFile);
  }

  fetch(BASE_URL + API.LLM, {
    method: 'POST',
    body: formdata
  })
  .then(response => {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    function read() {
      reader.read().then(async ({ done, value }) => {
        if (done) return;

        buffer += decoder.decode(value, { stream: true });
        const parts = buffer.split("\n\n");
        buffer = parts.pop();

        for (const part of parts) {
          try {
            let msg = JSON.parse(part);
            console.log(msg);
            loadingMessage.value.loading = false;
            //latex格式要求严格
            await typeWriter(msg, loadingMessage.value);
            // loadingMessage.value.content += msg;
          } catch (e) {
            ElMessage.error("网络问题, 请稍后重试");
          }
        }

        read();
      });
    }

    read();
  });

  currentConversation.value.messages.push(loadingMessage.value);
  nextTick(() => {
    scrollToBottom();
  });
}

const sendMessage = async () => {
  if (userInput.value.trim()) {
    // 添加用户消息
    currentConversation.value.messages.push({
      role: "user",
      content: userInput.value,
    });
    const prompt = userInput.value;
    userInput.value = "";
    nextTick(() => {
      scrollToBottom();
    });

    const taskId = historyList.value[currentConversationIndex.value].task_id;
    if (taskId === "default") {
      useLLM(apiConfigStore.config[0]);
      // console.log(renderMarkdown("\[ \cos(x) = 1 - \frac{x^2}{2!} + \frac{x^4}{4!} - \cdots \]"))
    } else {
      const taskConfig = apiConfigStore.getConfigById(taskId).value;
      useEmbeding(taskConfig);
    }
  }
};


const scrollToBottom = () => {
  const chatMessages = chatMessagesRef.value;
  chatMessages.scrollTop = chatMessages.scrollHeight;
};

function handleClickOutside(event) {
  const selectListLeftElements = document.querySelectorAll(".inputTitle");
  let clickedInside = false;

  selectListLeftElements.forEach((element) => {
    if (element.contains(event.target)) {
      clickedInside = true;
    }
  });

  if (!clickedInside) {
    if (editIndex !== null){
      historyList.value[editIndex].title = InputTitleValue.value;
      editIndex = null;
    }
    isInputTitle.value = null;
  }
}

onMounted(() => {
  document.addEventListener("click", handleClickOutside);
  
});

onBeforeUnmount(() => {
  document.removeEventListener("click", handleClickOutside);
});
</script>

<style scoped>
@import 'katex/dist/katex.min.css';

.katex {
  background-color: red;
  font-size: 1.2em;
  position: relative;
  top: 0.2em;
}


/* 样式保持不变 */
.ai-practice-container {
  display: flex;
  height: 100vh;
  font-family: Arial, sans-serif;
}

.image-container {
  margin-top: 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.streamed-img {
  max-width: 200px;
  max-height: 200px;
  border-radius: 8px;
  object-fit: cover;
}


.history-panel {
  width: 280px;
  background: linear-gradient(
    135deg,
    rgba(230, 240, 255, 0.01),
    rgba(240, 230, 255, 0.01)
  );
  background-color: #ffffff;
  padding: 20px;
  overflow-y: auto;
}

.new-chat-container {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.new-chat-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  padding: 13px; /* 略微增加内边距 */
  margin-top: 10px;
  margin-bottom: 5px;
  background: linear-gradient(
    to right,
    #0069e0,
    #0052bc
  ); /* 改用更深的蓝色渐变 */
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: opacity 0.3s;
  font-size: 14px; /* 加大字号 */
  font-weight: bold; /* 加粗字体 */
}

.new-chat-btn:hover {
  opacity: 0.9;
}

.history-list {
  list-style-type: none;
  padding: 0;
}

.history-list li {
  padding: 10px;
  display: flex;
  align-items: center;
  justify-content:  space-between;
  margin-bottom: 10px;
  background-color: #ffffff;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.history-list li:hover {
  box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2);
}

.history-list li.active {
  background-color: rgba(0, 105, 224, 0.15);
  color: #0052bc;
}
 
.history-list-title {
  height: auto;
  width: 175px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.inputTitle{
  background-color: rgba(255, 255, 255);
  font-size: 13px;
  text-align: left;
  position: fixed;
  padding: 0;
  padding-left: 5px;
  text-indent: 0;
  height: 20px;
  width: 175px;
  transform: translateX(-5px);
  z-index: 100;
}

.history-list-icon{
  height: auto;
  weight: 50px;
  font-size: 18px;
  opacity: 0;
}

.history-list li:hover .history-list-icon{
  opacity: 1;
}

.history-list-icon:hover{
  transform: scale(1.1);
  transition: scale 1s;
}

.history-list-edit{
  
}

.history-list-delete{
  color: red;
}

.chat-wrapper {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(
    135deg,
    rgba(0, 105, 224, 0.08),
    rgba(0, 56, 148, 0.08)
  );
}

.chat-panel {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: transparent;
  box-shadow: none;
  padding-top: 12px; /* 添加顶部内边距 */
  /* padding-left: 10%;
  padding-right: 10%; */
}

.visitor-info {
  background-color: transparent; /* 背透明 */
  padding: 15px 20px; /* 增加内边距 */
  margin-bottom: 20px; /* 增加与第一条对话的距离 */
  font-weight: bold;
  color: #333;
  text-align: left;
  font-size: 18px; /* 增大字体大小 */
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding-top: 20px;
  padding-left: 10%;
  padding-right: 10%;
  background-color: transparent;
  /* 修改滚动条颜色 */
  scrollbar-width: thin;
  scrollbar-color: rgba(0, 105, 224, 0.3) transparent;
}

/* 为 Webkit 浏览器（如 Chrome、Safari）自定义滚动条样式 */
.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.chat-messages::-webkit-scrollbar-track {
  background: transparent;
}

.chat-messages::-webkit-scrollbar-thumb {
  background-color: rgba(0, 105, 224, 0.3);
  border-radius: 3px;
}

.message {
  display: flex;
  margin-bottom: 20px;
}

.message .avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 10px;
  overflow: hidden;
}

.message .avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #ffffff;
}

.message .content {
  background-color: rgba(255, 255, 255, 1);
  padding: 12px 18px; /* 增加内边距 */
  border-radius: 10px;
  max-width: 80%;
  font-size: 16px; /* 增加字体大小 */
  line-height: 1.8; /* 增加行高 */
}

.message.user {
  flex-direction: row-reverse;
}

.message.user .avatar {
  margin-right: 0;
  margin-left: 10px;
}

.message.user .content {
  background-color: rgba(0, 105, 224, 0.12);
  color: black;
}

.input-area {
  padding: 20px 10% 0 10%;
  border-top: 0px solid #e0e0e0;
  background-color: transparent;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

input {
  width: 100%;
  padding: 12px 110px 12px 50px; /* 调整右侧padding以适应新的按钮组 */
  border: 1px solid rgba(204, 204, 204, 0.5);
  border-radius: 25px;
  font-size: 16px;
  background-color: rgba(255, 255, 255, 0.7);
  transition: border-color 0.3s;
  height: 55px;
}

input:focus {
  outline: none;
  border-color: #0069e0;
}

input::placeholder {
  color: #969696;
}

.button-group {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
}

.input-icon {
  color: #0069e0;
  font-size: 24px;
  cursor: pointer;
  position: absolute;
  left: 18px;
  top: 50%;
  transform: translateY(-50%);
}

.separator {
  width: 1px;
  height: 25px;
  background-color: rgba(204, 204, 204, 0.5);
  margin: 0 10px;
}

.send-button {
  width: 40px;
  height: 40px;
  background: linear-gradient(
    to right,
    #0069e0,
    #0052bc
  ); /* 保持一致的蓝色渐变 */
  border: none;
  color: white;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.send-button:disabled {
  background: rgba(0, 105, 224, 0.1);
  color: rgba(0, 82, 188, 0.3);
  cursor: default;
}

.send-button :deep(.el-icon) {
  font-size: 24px;
}

.send-button:not(:disabled):hover {
  opacity: 0.9;
}

/* 新增的免责声明样式 */
.disclaimer {
  font-size: 10px;
  color: #999;
  text-align: center;
  margin-top: 12px;
  margin-bottom: 12px;
}

.audio-wave {
  display: flex;
  align-items: center;
  height: 24px;
  width: 24px;
}

.audio-wave span {
  display: inline-block;
  width: 3px;
  height: 100%;
  margin-right: 1px;
  background: #0069e0;
  animation: audio-wave 0.8s infinite ease-in-out;
}

@keyframes audio-wave {
  0%,
  100% {
    transform: scaleY(0.3);
  }
  50% {
    transform: scaleY(1);
  }
}

.message .content audio {
  margin-top: 10px;
  width: 100%;
}

.backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6); /* 半透明灰色背景 */
  z-index: 99; /* 设置较低的 z-index */
  pointer-events: all; /* 使遮罩层可点击 */
}

.pop-window {
  position: fixed;
  top: 50%; /* 设置垂直居中 */
  left: 50%; /* 设置水平居中 */
  transform: translate(-50%, -50%); /* 通过偏移50%来确保完全居中 */
  z-index: 100;
}
</style>
