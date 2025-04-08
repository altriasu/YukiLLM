<template>
  <div class="confTask">
    <div class="confHead">
      <div class="logo"></div>
      <div @click="closePopWindow()" class="comeback"></div>
    </div>
    <div class="confBody">
      <div class="select-body">
        <span class="select-name">数据集选择</span>
        <span class="select-list">
          <div
            class="select-list-left"
            :class="{ 'select-list-left-dropdown': dropdownIndex === 1 }"
            @click="clickDropdown(1)"
          ></div>
          <div class="select-list-right">
            {{ showOptions.dataset }}
          </div>
          <ul v-show="dropdownIndex === 1" class="dropdown-list">
            <li
              v-for="option in item.options"
              :key="option"
              @click="selectOption(dropdownIndex, option)"
            >
              {{ option }}
            </li>
          </ul>
        </span>
      </div>
      <div class="select-body">
        <span class="select-name">嵌入模型</span>
        <span class="select-list">
          <div
            class="select-list-left"
            :class="{ 'select-list-left-dropdown': dropdownIndex === 2 }"
            @click="clickDropdown(2)"   
          ></div>
          <div class="select-list-right">
            {{ showOptions.embdingModel }}
          </div>
          <ul v-show="dropdownIndex === 2" class="dropdown-list">
            <li
              v-for="option in item.options"
              :key="option"
              @click="selectOption(dropdownIndex, option)"
            >
              {{ option }}
            </li>
          </ul>
        </span>
      </div>
      <div class="select-body">
        <span class="select-name">大模型平台</span>
        <span class="select-list">
          <div
            class="select-list-left"
            :class="{ 'select-list-left-dropdown': dropdownIndex === 3 }"
            @click="clickDropdown(3)"
          ></div>
          <div class="select-list-right">
            {{ showOptions.platform }}
          </div>
          <ul v-show="dropdownIndex === 3" class="dropdown-list">
            <li
              v-for="option in item.options"
              :key="option"
              @click="selectOption(dropdownIndex, option)"
            >
              {{ option }}
            </li>
          </ul>
        </span>
      </div>
      <div class="select-body">
        <span class="select-name">大模型名称</span>
        <span class="select-list">
          <div
            class="select-list-left"
            :class="{ 'select-list-left-dropdown': dropdownIndex === 4 }"
            @click="clickDropdown(4)"
          ></div>
          <div class="select-list-right">
            {{ showOptions.modelName }}
          </div>
          <ul v-show="dropdownIndex === 4" class="dropdown-list">
            <li
              v-for="option in item.options"
              :key="option"
              @click="selectOption(dropdownIndex, option)"
            >
              {{ option }}
            </li>
          </ul>
        </span>
      </div>
      <div class="select-body">
        <span class="select-name">检索任务选择</span>
        <span class="select-list">
          <div
            class="select-list-left"
            :class="{ 'select-list-left-dropdown': dropdownIndex === 5 }"
            @click="clickDropdown(5)"
          ></div>
          <div class="select-list-right">
            {{ showOptions.task }}
          </div>
          <ul v-show="dropdownIndex === 5" class="dropdown-list">
            <li
              v-for="option in item.options"
              :key="option"
              @click="selectOption(dropdownIndex, option)"
            >
              {{ option }}
            </li>
          </ul>
        </span>
      </div>
    </div>
    <div class="confFoot">
      <button @click="confirm()" class="confirm-btn">确认</button>
      <button @click="closePopWindow()" class="cancel-btn">取消</button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onBeforeUnmount } from "vue";
import { useApiConfigStore } from "@/stores/apiConfig";
import { ElMessage } from "element-plus";
import { BASE_URL, API } from "@/api/config";
import { v4 as uuidv4 } from 'uuid';

const apiConfigStore = useApiConfigStore();
const emit = defineEmits();

const dropdownIndex = ref(0);

let task_id = null;
const showOptions = reactive({
  id: task_id,
  dataset: "RSITMD",
  embdingModel: "remoteClip",
  platform: "ALIYUN",
  modelName: "qvq-max-latest",
  task: "img2txt"
});

const selectOptions = ref([
  { codename: "dataset", name: "数据集选择", options: [] },
  { codename: "embdingModel", name: "嵌入模型", options: [] },
  { codename: "platform", name: "大模型平台", options: [] },
  { codename: "modelName", name: "大模型名称", options: [] },
  { codename: "task", name: "检索任务选择", options: [] },
]);

function getOptions() {
  fetch(BASE_URL + API.CONFIG,{
    type: 'GET',
    headers: {
      'Content-Type': 'application/json'
    },
  })
  .then(res => {
    if (res.ok){
      return res.json();
    }
    else {
      ElMessage.error('请求失败，请检查网络连接');
      return;
    }
  })
  .then(data => {
    selectOptions.value[0].options = data.dataset;
    selectOptions.value[1].options = data.embding_model;
    selectOptions.value[2].options = data.platform;
    selectOptions.value[3].options = data.model[data.platform[0]]
    selectOptions.value[4].options = ["img2txt", "txt2img"]
  })
}

function selectOption(index, option) {
  showOptions[selectOptions.value[index - 1].codename] = option;
  dropdownIndex.value = 0;
}

function closePopWindow() {
  emit("emitClosePopWindow", false);
} 

function confirm() {
  task_id = uuidv4();
  showOptions.id = task_id;
  apiConfigStore.addConfig(showOptions);
  emit("emitConfirm", true, task_id);
}

let item = selectOptions.value[0];

function clickDropdown(id) {
  if (dropdownIndex.value === id) {
    dropdownIndex.value = 0; // 如果点击的是当前已展开的项，则收起
  } else {
    dropdownIndex.value = id; // 展开新项
  }
  item = selectOptions.value[id - 1];
}



function handleClickOutside(event) {
  const selectListLeftElements = document.querySelectorAll(".select-list-left");
  let clickedInside = false;

  selectListLeftElements.forEach((element) => {
    if (element.contains(event.target)) {
      clickedInside = true;
    }
  });

  const confBody = document.querySelector(".confBody");
  if (confBody && !confBody.contains(event.target)) {
    dropdownIndex.value = 0;
  }

  if (!clickedInside) {
    dropdownIndex.value = 0;
  }
}

onMounted(() => {
  document.addEventListener("click", handleClickOutside);
  getOptions();
});

onBeforeUnmount(() => {
  document.removeEventListener("click", handleClickOutside);
});
</script>

<style scoped>
@import "@/assets/css/CenterCard.css";

.select-body{
    width: auto;
    display: flex;
    align-items: center;
    justify-content:  space-between;
    height: 50px;
    margin: 40px 0px;
    padding: 10px 15px;
}

.select-name {
    color: white;
    font-size: 18px;
    font-weight: bold;
    white-space: nowrap;
}

.select-list {
    width: 50%;
    height: 30px;
    background-color: white;
    display: flex;
    align-items: center;
    border-radius: 5px;
    box-shadow: inset 0px 2px 5px rgba(0, 0, 0, 0.1);
    position: relative;
}

.select-list-left{
    background-image: url('@/assets/images/arrow2.png');
    background-size: contain;
    background-repeat: no-repeat;
    background-position: center;
    cursor: pointer;
    width: 20px;
    height: 60%;
}

.select-list-left-dropdown{
    background-image: url('@/assets/images/arrow2.png');
    background-size: contain;
    background-repeat: no-repeat;
    background-position: center;
    cursor: pointer;
    width: 20px;
    height: 60%;
    transform: rotate(90deg);
    transition: all 400ms;
}


.select-list-right{
    /* background-color: green; */
    color: #66b2ff;
    text-align: center;
    font-size: 1.1em;
    height: 100%;
    flex: 1;
    box-shadow: inset 0px 2px 5px rgba(0, 0, 0, 0.2);
}

.dropdown-list {
    position: absolute;
    top: 80%; /* 紧贴在 select-list 下方 */
    background: whitesmoke;
    box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2);
    list-style: none;
    margin-top: 5px;
    transform: translateX(8%);
    width: 243px;
    z-index: 10;
    opacity: 90%;
    backdrop-filter: blur(10px); 
}
  
.dropdown-list li {
    font-size: 0.9em;
    padding: 4px 15px;
    cursor: pointer;
}

.dropdown-list li:hover {
    background: #f0f0f0;
}
</style>
