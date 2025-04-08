from fastapi import APIRouter, Form, UploadFile, File
from fastapi.responses import StreamingResponse
import os
from scripts.config import *
from scripts.LLM import start_LLM
import json
from typing import Optional
import re

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

# 处理 LaTeX 公式的转义
def escape_latex_symbols(text: str) -> str:
    # 使用正则表达式匹配所有反斜杠后面的字符
    text = re.sub(r'\\', r'\\\\', text)
    return text

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
        os.makedirs(os.path.join(STATIC_DIR, "tmp", taskId), exist_ok=True)
        img_path = os.path.join(STATIC_DIR, "tmp", taskId, img.filename)
        with open(img_path, "wb") as buffer:
            buffer.write(img.file.read())

    messages = json.loads(messages)

    async def stream_response():
        try:
            async for chunk in start_LLM(platform, model, messages, img_path):
                yield json.dumps(chunk) + "\n\n"
        except Exception as e:
            yield json.dumps({"type": "error", "data": str(e)}) + "\n\n"
    return StreamingResponse(stream_response(), media_type="text/text/plain")
