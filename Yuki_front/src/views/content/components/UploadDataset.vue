<template>
      <div class="confTask">
    <div class="confHead">
      <div class="logo"></div>
      <div @click="closePopWindow()" class="comeback"></div>
    </div>
    <div class="confBody">
        <div>
            <span>数据集名称</span>
            <input type="text" class="create-input" />
        </div>
        <div>
            <span>数据集描述</span>
            <input type="text" class="create-input" />
        </div>
        <div>
            <span class="up-load-dec up-load-dec-left">上传图片文件夹</span><span class="up-load-dec up-load-dec-right">上传文本</span>
        </div>
        <div class="up-load-body">
            <el-icon @click="triggerFileInput('folder')" class="up-load-img up-load-plus">
                <input type="file" ref="folderInput" style="display: none" webkitdirectory directory 
                @change="handleFolderUpload" />
                <FolderOpened />
            </el-icon>
            <el-icon @click="triggerFileInput('file')" class="up-load-txt up-load-plus">
                <input type="file" ref="fileInput" style="display: none" accept=".txt" 
                @change="handleFileUpload" />
                <DocumentAdd />
            </el-icon>
        </div>
    </div>
    <div class="confFoot">
      <button class="confirm-btn">确认</button>
      <button @click="closePopWindow()" class="cancel-btn">取消</button>
    </div>
  </div>
</template>

<script setup>
import { ref, defineEmits } from 'vue';
import { ElMessage } from "element-plus";
const emit = defineEmits();

function closePopWindow() {
  emit('emitClosePopWindow', false); // 触发事件，将值传递给父组件
}

const folderInput = ref(null)
const fileInput = ref(null);

function triggerFileInput(type) {
  if (type === "folder") {
    folderInput.value.click(); // 触发上传文件夹
  } 
  else if (type === "file") {
    fileInput.value.click(); // 触发上传文件
  }
}

function handleFolderUpload(event) {
    const files = event.target.files;
    console.log("选择的文件夹内容：", files);

    // 获取文件夹中的所有文件
    for (const file of files) {
        console.log("文件：", file.webkitRelativePath, file.name);
    }
}

function handleFileUpload(event) {
  const file = event.target.files[0];
  console.log("选择的文件：", file);
}
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

</style>