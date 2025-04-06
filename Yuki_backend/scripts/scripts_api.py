from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import StreamingResponse
import os
import json
from PIL import Image
from shutil import rmtree

from scripts.config import *
import scripts.remoteclip as remoteclip

scripts_api = APIRouter()

@scripts_api.post("/remoteclip")
async def remote_clip(
    dataset_name: str = Form(...),
    task_id: str = Form(...),
    retrieve_type: str = Form(...),
    file: UploadFile = File(...)
):
    if dataset_name not in os.listdir(DATASET_DIR):
        return {"code": 404, "message": "Dataset not found"}
    
    os.makedirs(os.path.join(STATIC_DIR, "tmp", task_id), exist_ok=True)
    task_id_dir = os.path.join(STATIC_DIR, "tmp", task_id)

    if retrieve_type == "img2txt":
        if not file.filename.endswith(".jpg"):
            Image.open(file.file).save(os.path.join(task_id_dir, file.filename))
        else:
            with open(os.path.join(task_id_dir, file.filename), "wb") as f:
                f.write(file.file.read()) 
    else:
        with open(os.path.join(task_id_dir, file.filename), "w") as f:
            f.write(file.file.read())
    def stream_response():
        try:
            for chunk in remoteclip.main(dataset_name, retrieve_type, task_id_dir):
                yield json.dumps(chunk) + "\n\n"
        except Exception as e:
            yield json.dumps({"type": "error", "data": str(e)}) + "\n\n"

    return StreamingResponse(stream_response(), media_type="text/plain")



