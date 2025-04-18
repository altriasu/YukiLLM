from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from settings import *
from api.datasets_api import datasets_api
from api.retrieve_api import retrieve_api
from api.chat_api import chat_api


app = FastAPI(max_upload_size = 1024 * 1024 * 1024 * 10) # 100MB

app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.middleware("http")
async def myMiddleware(request: Request, call_next):
    # print("收到请求")
    response = await call_next(request)
    # print("发送回复")
    return response


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

app.include_router(datasets_api, prefix="/datasets", tags=["数据集管理接口"])
app.include_router(retrieve_api, prefix="/retrieve", tags=["检索接口"])
app.include_router(chat_api, prefix="/chat", tags=["聊天接口"])

if __name__ == "__main__":
    uvicorn.run("main:app", host=HOST, port=PORT, reload=True)
