<template>
  <div class="canvas">
    <div class="info-head">
      <div class="info-head-title">数据集管理</div>
      <div class="info-head-present">
        默认提供RSITMD、RSICD数据集，可以上传其他遥感Retrieve数据集，但是要求文本一条占一行
      </div>
    </div>
    <div class="info-body">
      <div v-for="dataset in datasets" :key="dataset.name" :title="dataset.description" class="dataset-card">
        <span class="dataset-name">{{ dataset.name }}</span>
        <el-icon @click="deleteDataset(dataset.name)" class="delete-dataset"><Delete/></el-icon>
        <div class="bubbles">
          <div v-for="n in getRandomBubbleCount()" :key="n" class="bubble" :style="getBubbleStyle()"></div>
        </div>
      </div>
      <div @click="openPopWindow()" class="dataset-card" title="添加数据集">
        <span class="plus-icon">+</span>
        <div class="bubbles">
          <div v-for="n in getRandomBubbleCount()" :key="n" class="bubble" :style="getBubbleStyle()"></div>
        </div>
      </div>
    </div>
  </div>
  <div v-if="showUploadDataset"  class="backdrop"></div>
  <div v-if="showUploadDataset" class="pop-window">
      <UploadDataset @emitClosePopWindow="closePopWindow" @emitRefreshDatasets="reflushDatasets" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import UploadDataset from './UploadDataset.vue';
import { ElMessage } from "element-plus";
import { API, BASE_URL } from '@/api/config';
import $ from 'jquery';

// 数据集示例
let datasets = ref([]);

const reflushDatasets = () => { 
  datasets.value = [];
  $.ajax({
    url: BASE_URL + API.DATASETS,
    type: 'GET',
    dataType: 'json',
    success: function (data) {
      data.forEach((d) => {
        datasets.value.push({
          name: d.name,
          description: d.description,
        });
      })
    },
  })};

onMounted(() => {
  reflushDatasets();
})

let showUploadDataset = ref(false);

function openPopWindow() {
  showUploadDataset.value = true;
}

function closePopWindow(value) {
  showUploadDataset.value = value;
}

function deleteDataset(datasetName) {
  fetch(BASE_URL + API.DATASETS, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ name: datasetName })
  })
  .then(res => {
    if (res.ok){
      return res.json();
    }
    else{
      throw new Error("网络异常")
    }
  })
  .then(data => {
    if (data.code === 200) {
      ElMessage.success("数据集删除成功！");
      reflushDatasets();
    } else if (data.code === 400) {
      ElMessage.error(data.error || "数据集不存在");
    } else if (data.code === 500) {
      ElMessage.error(data.error || "服务器错误，请稍后重试"); 
    } else {
      ElMessage.error(data.error || "删除失败，请稍后重试");
    }
  })
}

// 随机气泡数量
function getRandomBubbleCount() {
  return Math.floor(Math.random() * 5) + 10;
}

// 生成随机位置和动画的样式
function getBubbleStyle() {
  const left = Math.random() * 100 + '%'; // 气泡水平随机位置
  const delay = Math.random() * 8 + 's'; // 随机化延迟
  const size = 5 + Math.random() * 8 + 'px'; //随机大小

  return {
    '--size': size,
    '--left': left,
    '--delay': delay
  };
}
</script>

<style scoped>
* {
  margin: 0px;
  padding: 0px;
}

.canvas {
  background: #edf1fa;
  width: 100%;
  height: 100vh;
  position: relative;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
}

.info-head {
  width: 97%;
  height: 100px;
  background: linear-gradient(45deg, #4f8aee 0%, white 20%);
  margin: 0px auto;
  margin-top: 40px;
  border-radius: 10px;
  box-sizing: border-box;
  display: flex;
}

.info-head-title {
  font-size: 33px;
  color: #010850;
  text-align: left;
  line-height: 100px;
  padding-left: 80px;
}

.info-head-present {
  font-size: 11px;
  color: #888aab;
  text-align: left;
  line-height: 1.5;
  width: 300px; /* 设置固定宽度，超出自动换行 */
  word-wrap: break-word; /* 允许长单词换行 */
  padding-left: 20px;
  height: 100px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.info-body {
  width: 97%;
  height: 86%;
  background-color: #fff;
  margin: 0px auto;
  margin-top: 20px;
  border-radius: 10px;
  box-sizing: border-box;
  display: flex;
  flex-wrap: wrap;
}

.dataset-card {
  width: 170px;
  height: 200px;
  background: linear-gradient(
    to bottom,
    #1cb5e0 0%,
    #0069e0 20%,
    #0052bc 40%,
    #003894 60%,
    #001e6c 80%,
    #000046 100%
  );
  margin: 20px;
  border-radius: 10px;
  position: relative;
  box-sizing: border-box;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
}

.dataset-name {
  font-size: 20px;
  color: #66b2ff;
  overflow: hidden;
}

.delete-dataset{
  color: red;
  position: absolute;
  font-size: 30px;
  top: 50%;
  left: 50%;
  z-index: 100;
  opacity: 0;
  transform: translateX(-50%) translateY(-50%);
}

.dataset-card:hover {
  box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.3);
}

.dataset-card:hover .dataset-name {
  opacity: 0;
}

.dataset-card:hover .delete-dataset{
  opacity: 1;
  transition: all 0.3s;
}


/* 气泡动画 */
.bubbles {
  position: absolute;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.bubble {
  position: absolute;
  width: var(--size); /* 气泡大小 */
  height: var(--size); /* 气泡大小 */
  background: rgba(255, 255, 255, 0.5);
  box-shadow: 3px rgba(0, 0, 0, 1);
  border-radius: 50%;
  opacity: 0.6;
  animation: bubbleUp 12s infinite ease-in;
  animation-delay: var(--delay);
  left: var(--left);
  bottom: -15px;
}

@keyframes bubbleUp {
  0% {
    transform: translateY(0) translateX(0);
    opacity: 0;
  }
  20% {
    opacity: 0.5;
  }
  40% {
    transform: translateY(-60px) translateX(5px);
  }
  60% {
    opacity: 0.7;
  }
  80% {
    transform: translateY(-120px) translateX(-5px);
  }
  100% {
    transform: translateY(-200px) translateX(3px);
    opacity: 0;
  }
}

@keyframes sway {
  0%,
  100% {
    transform: translateX(-1px);
  }
  50% {
    transform: translateX(1px);
  }
}

.plus-icon {
  font-size: 40px;
  font-weight: bold;
  color: #66b2ff;
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
