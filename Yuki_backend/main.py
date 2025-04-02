from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from settings import *
from datasetsApi.datasets_api import datasets_api
from chat.chat_api import chat_api


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.middleware("http")
async def myMiddleware(request: Request, call_next):
    print("收到请求")
    response = await call_next(request)
    print("发送回复")
    return response


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

app.include_router(datasets_api, prefix="/datasets", tags=["数据集管理接口"])
app.include_router(chat_api, prefix="/chat", tags=["聊天界面接口"])

if __name__ == "__main__":
    uvicorn.run("main:app", host=HOST, port=PORT, reload=True)
