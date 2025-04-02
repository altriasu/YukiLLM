from fastapi import APIRouter

chat_api = APIRouter()

@chat_api.get("/")
def chat():
    pass



