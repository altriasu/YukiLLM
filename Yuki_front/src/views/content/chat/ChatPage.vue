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
      <div v-show="isScrolledToBottom" @click="scrollToBottom()" class="scroll-to-bottom">
        <el-icon><Bottom /></el-icon>
      </div>
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
                <img  src="@/assets/images/yuki.png" alt="AI Avatar" />
              </div>
              <div v-else>
                <img src="@/assets/images/AEGIS.png" alt="Me" />
              </div>
            </div>
            <div class="content">
              <div v-if="message.role !== 'user' && index !== 0" class="reasoning-container">
                <div class="reasoning-head">
                  <el-icon><MagicStick /></el-icon>
                  <span v-if="!currentReasoning.reasoning_messages[index].isCompleted">(っ•̀ω•́)っ✎⁾⁾思考中...</span> <span v-else>( ´▽` )ﾉ思考完成</span>
                  <el-icon @click="isOpenReasoningContent(index, false)" v-if="currentReasoning.reasoning_messages[index].isOpend" style="font-size: 70%; margin-left: 20px; cursor: pointer;"><ArrowUpBold /></el-icon>
                  <el-icon @click="isOpenReasoningContent(index, true)" v-else style="font-size: 70%; margin-left: 20px; cursor: pointer;"><ArrowDownBold /></el-icon>
                </div>
              </div>
              <div class="markdown-diy"><div v-if="currentReasoning.reasoning_messages[index].isOpend" v-html="renderMarkdown(currentReasoning.reasoning_messages[index].content)" class="reasoning-text"></div></div>
              <div class="markdown-diy"><div v-html="renderMarkdown(message.content)" class="message-text"></div></div>
              <div class="image-container">
                <img v-for="(img, i) in currentReasoning.reasoning_messages[index].imgs" :key="i" :src="img" class="streamed-img"/>
              </div>
            </div>
          </div>
        </div>

        <!-- 输入框 -->
        <div class="input-area">
          <div class="input-wrapper">
            <div v-if="isUploadedFile">
              <el-icon class="input-icon"><CircleCheckFilled /></el-icon>
            </div>
            <div v-else class="input-icon-group">
              <el-icon @click="triggerFileInput('file')" v-if="isTxt2ImgRetrieve" class="input-icon">
                <input type="file" ref="fileInput" style="display: none" @change="handleFileUpload" accept=".txt" />
                <DocumentAdd />
              </el-icon>
              <el-icon @click="triggerFileInput('file')" v-else class="input-icon">
                <input type="file" ref="fileInput" style="display: none" @change="handleFileUpload" accept="image/*" />
                <Picture/>
              </el-icon>
            </div>
            <input
              id = "input-message"
              v-model="userInput"
              @keyup.enter="sendMessage"
              placeholder="输入消息，按回车发送..."
              type="text"
            />
            <div class="button-group">
              <div class="separator"></div>
              <el-popover
                placement="top"
                :width="200"
                trigger="hover"
                :disabled="!!isInputDisabled"
              >
                <template #reference>
                  <el-button
                    class="send-button"
                    circle
                    @click="sendMessage"
                    :disabled="!isInputDisabled"
                  >
                    <el-icon><Top /></el-icon>
                    <!-- <el-icon v-show="!nextSentMessage"><Cpu /></el-icon> -->
                  </el-button>
                </template>
                <span>请上传图片/文字回复</span>
                <!-- <span v-show="!nextSentMessage">停止回答</span> -->
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
          `您好！我是结城理，你可以向我提出一些问题。`,
      },
    ],
  },
]);

const reasoningList = ref([{
  task_id: "default",
  reasoning_messages: [
    {
      isOpend: false,
      isCompleted: false,
      content: "",
      imgs: []
    }
  ]
}]);

const isOpenReasoningContent = (index, isOpend) => {
  currentReasoning.value.reasoning_messages[index].isOpend = isOpend;
}

// <---------------------------------- 弹窗 -------------------------------------------->
const currentConversationIndex = ref(0);
const userInput = ref("");
const chatMessagesRef = ref(null);

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

const isInputDisabled = computed(() => {
  if (taskConfig.value.task !== "chat" && uploadFile.value !== null){
    return true;
  } else if (taskConfig.value.task !== "chat" && userInput.value.trim() === "检索图像的对应文本") {
    return false;
  } else if (taskConfig.value.task !== "chat" && userInput.value.trim() === "检索文本对应图像") {
    return false;
  } else if (userInput.value.trim() !== "") {
    return true;
  } 
});


// <---------------------------------- 新建任务 ------------------------------------------->
const createNewConversation = (flag, taskId, taskType) => {
  closePopWindow();
  
  let title = "";
  if (taskType === "img2txt") {
    title = "检索图像的对应文本"
  } else if (taskType === "txt2img") {
    title = "检索文本对应图像"
  } else {
    title = "直接使用大模型"
  }

  historyList.value.unshift({
    title: title,
    task_id: taskId,
    // 实际上这里要和后端交互的话，messages 最好用 map 格式，key 是对应的 id，这样方便后端根据 id 来操作消息
    messages: [
      {
        role: "assistant",
        content: 
          "你好！我是结城理，你可以向我问一些问题。",
      },
    ],
  });
  reasoningList.value.unshift({
    task_id: taskId,
    reasoning_messages: [
      {
        isOpend: false,
        isCompleted: false,
        content: "",
        imgs: []
      },
    ]
  });

  currentConversationIndex.value = 0;
  chatCount.value = chatCount.value + 1;
  changeTask();
}

const changeTask = () => {
  if (taskConfig.value.task === "img2txt"){
    document.querySelector("#input-message").style = "user-select: none;"
    userInput.value = "检索图像的对应文本"
    document.querySelector("#input-message").disabled = true;
  } else if (taskConfig.value.task === "txt2img"){
    document.querySelector("#input-message").style = "user-select: none;"
    userInput.value = "检索文本对应图像"
    document.querySelector("#input-message").disabled = true;
  } else {
    document.querySelector("#input-message").style = "user-select: unset;"
    userInput.value = ""
    document.querySelector("#input-message").disabled = false;
  }
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

const currentReasoning = computed(
  () => reasoningList.value[currentConversationIndex.value]
);

const taskConfig = computed(() => {
  const taskId = currentConversation.value.task_id;
  return apiConfigStore.getConfigById(taskId).value;
});

const isTxt2ImgRetrieve = computed(() => {
  if (taskConfig.value.task === "txt2img") {
    return true;
  } else {
    return false;
  }
})

const selectConversation = (index) => {
  currentConversationIndex.value = index;
  changeTask();
  nextTick(() => {
    scrollToBottom();
  });
};


// <---------------------------------- 发送信息 ------------------------------------------->
const fileInput = ref(null);
const uploadFile = ref(null);
const isUploadedFile = ref(false);

const triggerFileInput = () => {
  fileInput.value.click()
}

const handleFileUpload = (event) => {
  uploadFile.value = event.target.files[0];
  isUploadedFile.value = true;
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function typeWriter(text, message, type = "char", delay = 10) {
  if (type === "char"){
    for (let char of text) {
      await sleep(delay);
      message.content += char;
    }
  } else if (type === "line" ){
    await sleep(delay);
    message.content += text
  }
}

const useEmbeding = async () => {
  const formdata = new FormData();
  formdata.append("dataset_name", taskConfig.value.dataset);
  formdata.append("task_id", taskConfig.value.id);
  formdata.append("retrieve_type", taskConfig.value.task);
  formdata.append("file", uploadFile.value)

  const loadingMessage = ref({
    role: "assistant",
    content: "",
  });

  const reasoningMessage = ref({
    isOpend: true,
    isCompleted: false,
    content: "",
    imgs: []
  })

  nextTick(() => {
      scrollToBottom();
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
              reasoningMessage.value.content = "";
              await typeWriter(`#### 向量模型检索中...${msg.data}`, reasoningMessage.value);
            } else if (msg.type === "hint") {
              await typeWriter(msg.data, reasoningMessage.value);
            } else if (msg.type === "result_img") {
              const imgHtml = `<div style="display: inline-block; margin: 5px;" class="result-item">
                                <img src="${msg.data.image}" style="width: 100px; height: 100px;" class="result-image"/>
                                <div class="score">Score: ${msg.data.score}</div>
                              </div>`;
              reasoningMessage.value.content += imgHtml;
              await sleep(100);
            } else if (msg.type === "result_txt") {
              await typeWriter(msg.data, reasoningMessage.value);
            } else if (msg.type === "reasoning_content" && msg.message !== null){
              await typeWriter(msg.message, reasoningMessage.value, "line");
            } else if (msg.type === "content" && msg.message !== null) {
              await typeWriter(msg.message, loadingMessage.value, "line");
              reasoningMessage.value.isCompleted = true;
            } else if (msg.type === "img_content" && msg.message !== null) {
              const imgHtml = `<div style="display: inline-block; margin: 5px;" class="result-item">
                                <img src="${msg.message.image}" style="width: 100px; height: 100px;" class="result-image"/>
                                <div class="score">Score: ${msg.message.score}</div>
                              </div>`;
              loadingMessage.value.content += imgHtml;
              await sleep(100);
              reasoningMessage.value.isCompleted = true;
            } else if (msg.type === "error") {
              /* reasoningMessage.value.content = "检索失败，请稍后重试"; */
              console.log(msg);
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

  currentReasoning.value.reasoning_messages.push(reasoningMessage.value);
  currentConversation.value.messages.push(loadingMessage.value);
  nextTick(() => {
    scrollToBottom();
  });
}

const useLLM = async () => {
  const loadingMessage = ref({
    role: "assistant",
    content: "",
  });

  const reasoningMessage = ref({
    isOpend: true,
    isCompleted: false,
    content: "",
    imgs: []
  })

  const formdata = new FormData();
  formdata.append("platform", taskConfig.value.platform);
  formdata.append("model", taskConfig.value.modelName);
  formdata.append("taskId", taskConfig.value.id);
  formdata.append("messages", JSON.stringify(historyList.value[currentConversationIndex.value].messages));
  if (uploadFile.value) {
    formdata.append("img", uploadFile.value);
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
            const msg = JSON.parse(part);
            // console.log(msg);
            if (msg.type === "reasoning_content" && msg.message !== null){
              await typeWriter(msg.message, reasoningMessage.value, "line");
            } else if (msg.type === "content" && msg.message !== null) {
              await typeWriter(msg.message, loadingMessage.value, "line");
              reasoningMessage.value.isCompleted = true;
            } 
            // loadingMessage.value.content += msg;
          } catch (e) {
            console.log(e);
          }
        }

        read();
      });
    }
    read();
  })
  currentReasoning.value.reasoning_messages.push(reasoningMessage.value);
  currentConversation.value.messages.push(loadingMessage.value);
  nextTick(() => {
    scrollToBottom();
  });
}

const sendMessage = async () => {
  if (userInput.value.trim()) {
    const userMessage = {
        role: "user",
        content: userInput.value,
    }
    // 添加用户消息
    currentConversation.value.messages.push(userMessage);

    const reasoningMessage = ref({
      isOpend: true,
      isCompleted: false,
      content: "",
      imgs: []
    });

    if (isUploadedFile.value && taskConfig.value.task !== "txt2img") {
      reasoningMessage.value.imgs.push(URL.createObjectURL(uploadFile.value));
    }

    if (isUploadedFile.value && taskConfig.value.task === "txt2img") {
      reasoningMessage.value.imgs = []
      if (uploadFile.value.type === "text/plain" || uploadFile.value.name.endsWith('.txt')) {
        const reader = new FileReader();
        
        reader.onload = (e) => {
          // 获取文本内容
          const textContent = e.target.result;
          reasoningMessage.value.content = textContent;
        };
        
        reader.onerror = (e) => {
          console.error('文件读取错误:', e.target.error);
          ElMessage.error('文件读取失败');
        };
        reader.readAsText(uploadFile.value);
      }
    }

    currentReasoning.value.reasoning_messages.push(reasoningMessage.value);

    userInput.value = "";
    nextTick(() => {
      scrollToBottom();
    });

    const taskId = historyList.value[currentConversationIndex.value].task_id;
    if (taskConfig.value.task === "chat") {
      await useLLM();
    } else {
      await useEmbeding();
    }

    uploadFile.value = null;
    isUploadedFile.value = false;

    changeTask();
  }
};

const isScrolledToBottom = ref(false)

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
  if (chatMessagesRef.value) {
    chatMessagesRef.value.addEventListener('scroll', () => {
      const el = chatMessagesRef.value;
      isScrolledToBottom.value = el.scrollTop + el.clientHeight <= el.scrollHeight - 1;
    });
  }
});

onBeforeUnmount(() => {
  document.removeEventListener("click", handleClickOutside);
  currentConversation.value.messages.forEach(msg => {
    msg.images?.forEach(url => URL.revokeObjectURL(url));
  });
});
</script>

<style scoped>
/* markdown latex 样式 */
@import 'katex/dist/katex.min.css';
@import url('@/assets/css/markdown.css');

* {
  overflow: hidden;
}


.katex-display {
  overflow-x: auto;
  max-width: 100%;
  box-sizing: border-box;
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
  width: 50px;
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
  position: relative;
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
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 10px;
  overflow: hidden;
}

.message .avatar img {
  width: 100%;
  height: 100%;
  border-radius: 10px;
  object-fit: cover;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  
}

.message .content {
  background-color: rgba(255, 255, 255, 1);
  padding: 12px 18px; /* 增加内边距 */
  border-radius: 10px;
  margin-top: 40px;
  max-width: 80%;
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

.message-text {
  word-break: break-word;
  overflow-wrap: anywhere;
  max-width: 100%;
  overflow-x: auto;
}

.reasoning-head {
  background-color: #f2f2f2;
  display: inline-block;
  padding: 5px;
  border-radius: 8px;
}

.reasoning-head span {
  font-size: 14px;
  font-weight: bold;
  color: #333;
  text-align: left;
  margin-left: 5px;
}

.reasoning-text {
  background-color: #f2f2f2;
  color: #016ce0;
  border-radius: 8px;
  padding: 0 10px;

  word-break: break-word;
  overflow-wrap: anywhere;
  max-width: 100%;
  overflow-x: auto;
}

.reasoning-text :deep(p){
  font-size: 0.8em;
}

.scroll-to-bottom{
  background-color: rgba(255, 255, 255, 0.8);
  color: rgba(0, 105, 224, 0.3);
  position: absolute;
  bottom: 130px;
  font-size: 18px;
  text-align: center;
  line-height: 2.5;
  z-index: 10;
  left: 50%;
  transform: translateX(-50%);
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 1px solid rgba(0, 105, 224, 0.3);
  cursor: pointer;
  transition: background-color 0.3s;
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
