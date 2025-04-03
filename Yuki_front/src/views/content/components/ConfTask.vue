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
            id="sll1"
            @click="clickDropdown(1)"
          ></div>
          <div class="select-list-right">
            {{ ApiConfigStore.config.dataset }}
          </div>
          <ul v-show="dropdownIndex === 1" class="dropdown-list">
            <li
              v-for="option in item.options"
              :key="option"
              @click="selectOption(index, option)"
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
            id="sll2"
            @click="clickDropdown(2)"
          ></div>
          <div class="select-list-right">
            {{ ApiConfigStore.config.embdingModel }}
          </div>
          <ul v-show="dropdownIndex === 2" class="dropdown-list">
            <li
              v-for="option in item.options"
              :key="option"
              @click="selectOption(index, option)"
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
            id="sll3"
            @click="clickDropdown(3)"
          ></div>
          <div class="select-list-right">
            {{ ApiConfigStore.config.platform }}
          </div>
          <ul v-show="dropdownIndex === 3" class="dropdown-list">
            <li
              v-for="option in item.options"
              :key="option"
              @click="selectOption(index, option)"
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
            id="sll4"
            @click="clickDropdown(4)"
          ></div>
          <div class="select-list-right">
            {{ ApiConfigStore.config.modelName }}
          </div>
          <ul v-show="dropdownIndex === 4" class="dropdown-list">
            <li
              v-for="option in item.options"
              :key="option"
              @click="selectOption(index, option)"
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
            id="sll5"
            @click="clickDropdown(5)"
          ></div>
          <div class="select-list-right">
            {{ ApiConfigStore.config.task }}
          </div>
          <ul v-show="dropdownIndex === 5" class="dropdown-list">
            <li
              v-for="option in item.options"
              :key="option"
              @click="selectOption(index, option)"
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
import { ref, onMounted, onBeforeUnmount, defineEmits } from "vue";
import { useApiConfigStore } from "@/stores/apiConfig";

const ApiConfigStore = useApiConfigStore();
const emit = defineEmits();

function closePopWindow() {
  emit("emitClosePopWindow", false);
}

function confirm() {
  emit("emitConfirm", true)
}

const dropdownIndex = ref(0);
const selectOptions = ref([
  { name: "数据集选择", options: ["数据集A", "数据集B", "数据集C"] },
  { name: "嵌入模型", options: ["模型X", "模型Y", "模型Z"] },
  { name: "大模型平台", options: ["平台1", "平台2", "平台3"] },
  { name: "大模型名称", options: ["GPT-4", "Gemini", "Claude"] },
  { name: "检索任务选择", options: ["任务1", "任务2", "任务3"] },
]);

let item = selectOptions.value[0];
let Expand = false;
let ExpandId = 0;
function clickDropdown(id) {
  dropdownIndex.value = id;
  const selectListLeft = document.querySelector(`#sll${id}`);
  if (selectListLeft && !Expand) {
    selectListLeft.style.transform = "rotate(90deg)";
    selectListLeft.style.transition = "all 400ms";
    Expand = true;
    ExpandId = id;
  } else if (selectListLeft && Expand) {
    selectListLeft.style.transform = "";
    dropdownIndex.value = 0;
    Expand = false;
    ExpandId = 0;
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

  if (!clickedInside) {
    dropdownIndex.value = 0;
    const selectListLeft = document.querySelector(`#sll${ExpandId}`);
    if (selectListLeft) {
      selectListLeft.style.transform = "";
      Expand = false;
      ExpandId = 0;
    }
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
    background: whitesmoke;
    box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2);
    list-style: none;
    padding: 5px 0;
    margin-top: 5px;
    width: 259px;
    z-index: 10;
    transform: translateX(3px) translateY(62px);
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
