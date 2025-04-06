<template>
  <div class="login-page">
    <div v-show="!showOpVideo" class="wave-container">
      <div class="wave-box" ref="waveRefs">
        <div class="wave-box-title">
          <div>YUKILLM</div>
          <div>This is a platform </div>
          <div>for remote sensing image retrieval using large models</div>
          <div>Welcome to our platform</div>
        </div>
        <svg class="waves" viewBox="0 12 150 28" preserveAspectRatio="none" shape-rendering="auto">
          <defs>
            <path id="gentle-wave" d="M-160 44c30 0 58-18 88-18s58 18 88 18 58-18 88-18 58 18 88 18v44h-352z"></path>
          </defs>
          <g class="parallax">
            <use xlink:href="#gentle-wave" x="20" y="2" fill="rgba(0, 122, 204, 0.7)" />
            <use xlink:href="#gentle-wave" x="40" y="3" fill="rgba(0, 122, 204, 0.5)" />
            <use xlink:href="#gentle-wave" x="80" y="4" fill="rgba(0, 122, 204, 0.3)" />
            <use xlink:href="#gentle-wave" x="100" y="5" fill="rgba(0, 122, 204, 0.9)" />
          </g>
        </svg>
        <div class="wave-bottom"></div>
      </div>
    </div>
    <video v-show="showOpVideo" ref="videoRef" class="op-video" autoplay muted @ended="onOpVideoEnded">
      <source src="@/assets/video/op.mp4" type="video/mp4" />
      您的浏览器不支持 HTML5 视频。
    </video>
    <!-- 初始不渲染背景视频，直到OP视频播放结束 -->
    <video v-show="showBgVideo" ref="videoRef2" class="background-video" autoplay muted loop>
      <source src="@/assets/video/bg.mp4" type="video/mp4" />
      您的浏览器不支持 HTML5 视频。
    </video>
    <button v-if="showButton" @click="goToMainPage()" ref="magicButtonRef" class="magic-button">
      <div class="logo">YUKI</div>
      <div class="text">click to start your experience</div>
    </button>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue';

const waveRefs = ref(null);

const videoRef = ref(null);
const videoRef2 = ref(null);
const showOpVideo = ref(false);
const showBgVideo = ref(false);
const showButton = ref(false);
const magicButtonRef = ref(null);


function generateFadeDownKeyframes() {
  let keyframes = '@keyframes fadeDown {\n';

  for (let i = 0; i <= 33; i += 3) {
    const h = 100 - i;
    keyframes += `  ${i}% { height: ${h}%; }\n`;
  }

  for (let i = 33; i <= 50; i += 2) {
    const h = 100 - i;
    keyframes += `  ${i}% { height: ${h}%; }\n`;
  }

  for (let i = 51; i <= 100; i ++) {
    const h = 100 - i;
    keyframes += `  ${i}% { height: ${h}%; }\n`;
  }

  keyframes += '}\n';

  // 创建 <style> 标签并插入
  const styleTag = document.createElement('style');
  styleTag.type = 'text/css';
  styleTag.innerHTML = keyframes;
  document.head.appendChild(styleTag);
}


onMounted(() => {
  generateFadeDownKeyframes();

  const opVideo = videoRef.value;
  const bgVideo = videoRef2.value;

  if (opVideo && bgVideo) {
    // 提前加载 OP 视频，进行缓冲
    opVideo.load();
    opVideo.play().then(() => {
      opVideo.pause(); // 播放一次然后暂停，确保预加载完成
      opVideo.currentTime = 0.7; 
    })
    // 播放 wave 动画
    waveRefs.value?.classList.add('down');
    
    waveRefs.value?.addEventListener('animationend', () => {
      nextTick(() => {
        showOpVideo.value = true;
        // 直接继续播放已缓冲的 op
        opVideo.play()
        setTimeout(() => {
          showButton.value = true;
          nextTick(() => {
            magicButtonRef.value?.classList.add('show');
          });
        }, 1100);
      });
    });

    bgVideo.load();
  }
});

const goToMainPage = () => {
  window.location.href = '/main';
};


const onOpVideoEnded = () => {
  showBgVideo.value = true;
  videoRef2.value?.play(); 
  videoRef.value?.remove();
};
</script>

<style scoped>
*{
  margin: 0;
  padding: 0;
}
.login-page {
  position: relative;
  height: 100vh;
  overflow: hidden;
}

.wave-container {
  position: relative;
  background-color: #181a1b;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
}

.wave-box {
  position: absolute;
  bottom: 0;
  width: 100%;
  height: 100%;
  opacity: 0.9;
}

@font-face {
  font-family: 'Playfair';
  src: url('@/assets/fonts/PlayfairDisplaySC/PlayfairDisplaySC-Regular.ttf') format('truetype');
}

.wave-box-title {
  position: fixed;
  top: 40%;
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
  font-size: 20px;
  text-align: center;
}

.wave-box div:nth-child(1){
  font-size: 1.9em;
  font-family: 'Playfair', sans-serif;
  color: #1d384a;
}

.wave-box div:nth-child(2){
  font-size: 0.4em;
  font-family: 'times new roman', sans-serif;
  color: #98b7ca;
}

.wave-box div:nth-child(3){
  font-size: 0.4em;
  font-family: 'times new roman', sans-serif;
  color: #98b7ca;
}

.wave-box div:nth-child(4){
  font-size: 0.4em;
  font-family: 'times new roman', sans-serif;
  color: #98b7ca;
}


.wave-box.down {
  animation: fadeDown 2s ease-in-out forwards;
}

.waves {
  width: 100%;
  height: 15vh;
  transform: translateY(-15vh);
  margin-bottom: -8px;
}

.wave-bottom {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: #007acc;
}


.parallax use {
  animation: move-forever 1s cubic-bezier(0.55, 0.5, 0.45, 0.5) infinite;
}

.parallax use:nth-child(1){
  animation-delay: -2s;
  animation-duration: 4s;
}

.parallax use:nth-child(2){
  animation-delay: -3s;
  animation-duration: 6s;
}

.parallax use:nth-child(3){
  animation-delay: -5s;
  animation-duration: 8s;
}

.parallax use:nth-child(4){
  animation-delay: -7s;
  animation-duration: 12s;
}

@keyframes move-forever {
  0% {
    transform: translate3d(-90px, 0, 0);
  }
  100% {
    transform: translate3d(85px, 0, 0);
  }
}

.op-video {
  position: absolute;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  object-fit: cover;
}

.background-video {
  position: absolute;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  object-fit: cover;
}

.magic-button {
  all: unset;
  position: absolute;
  top: 50%;
  left: 63%;
  transform: translateY(-50%);
  width: 300px;
  height: 150px;
  background-color: rgba(0, 0, 0, 0);
  border-radius: 10px;
  font-size: 28px;
  font-family: 'times new roman', sans-serif;
  color: white;
  cursor: pointer;
  opacity: 0; 
}

.magic-button.show{
  animation: fadeIn 0.5s ease-in-out forwards;
}

@keyframes fadeIn {
  0% {
    opacity: 0;
  }
  20% {
    opacity: 0.2;
  }
  50% {
    opacity: 0.5;
  }
  70% {
    opacity: 0.7;
  }
  100% {
    opacity: 1;
  }
}

.logo {
  text-align: center;
  font-size: 80px;
  transform: translate(-5px, 20%);
  font-weight: bold;
}

.text { 
  text-align: center;
  font-size: 0.5em;
  font-family: 'microsoft yahei', sans-serif;
  font-weight: bold;
  color: white;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8);
}
</style>
