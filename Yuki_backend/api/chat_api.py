from fastapi import APIRouter, Form, UploadFile, File
from fastapi.responses import StreamingResponse
import os
import json
from typing import Optional
from shutil import rmtree
import re

from utils.config import *
from utils.startLLM import start_LLM

chat_api = APIRouter()

@chat_api.get("/config")
async def get_config():
    response = {}
    response['dataset'] = []
    for dir in os.listdir(os.path.join(STATIC_DIR, "datasets")):
        response['dataset'].append(dir)
    response["embding_model"] = CHAT_CONFIG["embdingModel"]
    response["platform"] = CHAT_CONFIG["platform"]
    response["model"] = LLM_CONFIG["model"]

    return response

# # 处理 LaTeX 公式的转义
# def escape_latex_symbols(text: str) -> str:
#     # 使用正则表达式匹配所有反斜杠后面的字符
#     text = re.sub(r'\\', r'\\\\', text)
#     return text

@chat_api.post("")
async def startChat(
    platform: str = Form(...), 
    model: str = Form(...),
    taskId: str = Form(...),
    messages: str = Form(...),
    img: Optional[UploadFile] = File(None)
):
    if platform not in CHAT_CONFIG["platform"]:
        return {"error": "Invalid platform"}
    if model not in LLM_CONFIG["model"][platform]:
        return {"error": "Invalid model"}
    
    img_path = None  
    if img:
        tmp_dir_path = os.makedirs(os.path.join(STATIC_DIR, "tmp", taskId), exist_ok=True)
        img_path = os.path.join(STATIC_DIR, "tmp", taskId, img.filename)
        with open(img_path, "wb") as buffer:
            buffer.write(img.file.read())

    messages = json.loads(messages)

    async def stream_response():
        test_path = os.path.join(STATIC_DIR, "test.txt")
        try:
            print("Start LLM")
            async for chunk in start_LLM(platform, model, messages, img_path):
                with open(test_path, "a") as f:
                    f.write(json.dumps(chunk) + "\n\n")
                yield json.dumps(chunk) + "\n\n"
        except Exception as e:
            yield json.dumps({"type": "error", "data": str(e)}) + "\n\n"
        finally:
                # 清理临时文件
                try:
                    if os.path.exists(tmp_dir_path):
                        rmtree(tmp_dir_path)
                except:
                    pass
    return StreamingResponse(stream_response(), media_type="text/text/plain")

@chat_api.post("/test")
def test(
    platform: str = Form(...), 
    model: str = Form(...),
    taskId: str = Form(...),
    messages: str = Form(...),
    img: Optional[UploadFile] = File(None)
    ):
    def stream_response():
        with open(os.path.join(STATIC_DIR, "test.txt"), "r") as f:
            for line in f.readlines():
                yield line
    return StreamingResponse(stream_response(), media_type="text/text/plain")