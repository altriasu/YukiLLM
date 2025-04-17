<template>
  <div class="confTask">
    <div class="confHead">
      <div class="logo"></div>
      <div @click="closePopWindow()" class="comeback"></div>
    </div>
    <div class="confBody">
        <div>
            <span>数据集名称</span>
            <input v-model="inputName" type="text" class="create-input" id="inputName"></input>
        </div>
        <div>
            <span>数据集描述</span>
            <input v-model="inputDesc" type="text" class="create-input"></input>
        </div>
        <div>
            <span class="up-load-dec up-load-dec-left">上传图片文件夹</span><span class="up-load-dec up-load-dec-right">上传文本</span>
        </div>
        <div class="up-load-body">
            <el-icon @click="triggerFileInput('folder')" class="up-load-img up-load-plus">
                <input type="file" ref="folderInput" style="display: none" webkitdirectory directory 
                @change="handleFolderUpload" />
                <FolderOpened v-show="!isFolderChecked" />
                <FolderChecked v-show="isFolderChecked" />
            </el-icon>
            <el-icon @click="triggerFileInput('file')" class="up-load-txt up-load-plus">
                <input type="file" ref="fileInput" style="display: none" accept=".txt" 
                @change="handleFileUpload" />
                <DocumentAdd v-show="!isFileChecked"/>
                <DocumentChecked v-show="isFileChecked"/>
            </el-icon>
        </div>
    </div>
    <div class="error-message-body">
        <span class="error-message">{{ errorMessage }}</span>
    </div>
    <div class="confFoot">
      <button @click="uploadDataset()" class="confirm-btn">确认</button>
      <button @click="closePopWindow()" class="cancel-btn">取消</button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onBeforeUnmount } from 'vue';
import { ElMessage } from "element-plus";
import { API, BASE_URL } from '@/api/config';
const emit = defineEmits();

function closePopWindow() {
  emit('emitClosePopWindow', false); 
}

const folderInput = ref(null);
const fileInput = ref(null);
const inputName = ref("");
const inputDesc = ref("");
let errorMessage = ref("");
let lastInputName = "";

function triggerFileInput(type) {
  if (type === "folder") {
    folderInput.value.click(); 
  } 
  else if (type === "file") {
    fileInput.value.click(); 
  }
}


let dataset = reactive({
  name: "",
  description: "",
  imgsFolder: [],
  textFile: null
})

const imageExtensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg', 'tif'];
let isFolderChecked = ref(false);

function handleFolderUpload(event) {
    const files = event.target.files;
    if (!files.length) {
        errorMessage.value = "文件夹为空，请选择包含图片的文件夹";
        dataset.imgsFolder = [];
        return;
    }

    let isValid = true;
    // 获取文件夹中的所有文件
    for (const file of files) {
        // console.log("文件：", file.webkitRelativePath, file.name);
        const fileExtension = file.name.split('.').pop().toLowerCase();
        if (imageExtensions.includes(fileExtension)) {
            dataset.imgsFolder.push(file);
        } else {
            isValid = false;
            errorMessage.value = "文件夹中包含非图片文件，请选择只包含图片的文件夹";
            break;
        }
    }

    if (isValid) {
        errorMessage.value = "";
        isFolderChecked.value = true;
    }
    else {
        dataset.imgsFolder = [];
        isFolderChecked.value = false;
    }
}

let isFileChecked = ref(false);
function handleFileUpload(event) {
  const file = event.target.files[0];
  if (!file) {
    errorMessage.value = "文件为空，请选择一个文本文件";
    dataset.textFile = null;
    return;
  }
  dataset.textFile = file;
  isFileChecked.value = true;
}

function uploadDataset() {
  dataset.name = inputName.value.trim();
  dataset.description = inputDesc.value.trim();

  if (!dataset.name) {
    errorMessage.value = "数据集名称不能为空";
    return;
  }
  if (!dataset.description) {
    errorMessage.value = "数据集描述不能为空";
    return;
  }
  if (!dataset.imgsFolder.length) {
    errorMessage.value = "请上传包含图片的文件夹";
    return;
  }
  if (!dataset.textFile) {
    errorMessage.value = "请上传文本文件";
    return;
  }

  const formData = new FormData();
  formData.append('name', dataset.name);
  formData.append('description', dataset.description);
  
  dataset.imgsFolder.forEach((file) => {
    formData.append('imgsFolder', file);
  });

  formData.append('textFile', dataset.textFile);

  fetch(BASE_URL + API.DATASETS, {
    method: 'POST',
    body: formData
  })
  .then(res => {
      ElMessage({
        message: "数据集上传中，请稍等...",
        type: "info",
        showClose: true,
      })
      if (res.ok) {
        return res.json();
      }
      else{
        errorMessage.value = "上传失败，请稍后重试";
      }
    })
  .then(data => {
    if (data.code === 200) {
      ElMessage.success("数据集上传成功！");
      closePopWindow();
      emit("emitRefreshDatasets", true);
    } else {
      errorMessage.value = data.error || "上传失败，请稍后重试";
    }
  })
  .catch(error => {
    errorMessage.value = "上传过程中出现错误，请稍后重试";
  });
}



function handleClickOutside(event) {
  const selectListLeftElements = document.querySelectorAll("#inputName");
  let clickedInside = false;

  selectListLeftElements.forEach((element) => {
    if (element.contains(event.target)) {
      clickedInside = true;
    }
  });

  if (!clickedInside && lastInputName !== inputName.value) {
    lastInputName = inputName.value;
    fetch(BASE_URL + API.DATASETS, {
      method: "GET"
    })
    .then(res => {
      if (res.ok){
        return res.json();
      }
    })
    .then(data => {
      let isError = false;
      data.some((d) => {
        if (d.name === inputName.value) {
          isError = true;
        }
      });
      if (isError) {
        errorMessage.value = "数据集名称已存在";
      } else {
        errorMessage.value = "";
      }
    })
    .catch(error => {
      errorMessage.value = "未联网，请检查网络连接";
    });
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
.confBody div{
    display: flex;
    align-items: center;
    justify-content:  space-between;
    margin: 40px 0px;
    padding: 10px 15px;
}

.confBody div span{
    color: white;
    font-size: 18px;
    font-weight: bold;
}

.up-load-body{
    width: auto;
    height: 200px;
    margin: 40px 0px;
    padding: 10px 15px;
}

.create-input{
    width: 50%;
    height: 30px;
    background-color: #fff0ff;
    padding-left: 10px;
    display: flex;
    align-items: center;
    border-radius: 5px;
    box-shadow: inset 0px 2px 5px rgba(0, 0, 0, 0.3);
}

.up-load-dec-left{
    transform: translateX(11px);
}

.up-load-dec-right{
    transform: translateX(-43px);
}

.up-load-plus{
    width: 150px;
    height: 200px;
    /* background-color: #fff0ff; */
    border-radius: 3px;
    /* box-shadow: inset 0px 2px 5px rgba(0, 0, 0, 0.1); */

    font-size: 160px;
    font-weight: bold;
    text-indent: 42px;
    color: #66b2ff;
    cursor: pointer;
    transform: translateY(-45px);
}

.up-load-plus:hover{
    transform: translateY(-45px) scale(1.01);
    box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2);
    transition: all 0.5s;
}

.error-message-body{
    position: absolute;
    display: flex;
    align-items: center;
    justify-content: center;
    top: 550px;
    left: 50%;
    transform: translateX(-50%);
    width: 265px;
    height: 30px;
    border-radius: 5px;
    padding: 10px auto;
}
.error-message{
    color: red;
    font-size: 15px;
    font-family: '宋体';
    font-weight: bold;
    text-align: center;
    animation: fontscale 3s infinite;
}

@keyframes fontscale {
    0% {
        transform: scale(1);
    }
    50% {
        transform: scale(1.2);
    }
    100% {
        transform: scale(1);
    }
}
</style>