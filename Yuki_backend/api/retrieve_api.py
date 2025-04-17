from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import StreamingResponse
import os
import json
from PIL import Image
from shutil import rmtree
import aiofiles

from utils.config import *
import utils.remoteclip as remoteclip

retrieve_api = APIRouter()

@retrieve_api.post("/remoteclip")
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
    file_dir = task_id_dir
    
    try:
        if retrieve_type == "img2txt":
            file_path = os.path.join(task_id_dir, file.filename)
            if not file.filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                try:
                    img = Image.open(file.file)
                    img.save(file_path)
                except Exception as e:
                    return {"code": 400, "message": f"Invalid image file: {str(e)}"}
            else:
                async with aiofiles.open(file_path, 'wb') as f:
                    await f.write(await file.read())
        else:
            file_path = os.path.join(task_id_dir, file.filename)
            task_id_dir = file_path
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(await file.read())

        async def stream_response():
            try:
                # test_path = os.path.join(STATIC_DIR, "test.txt")
                async for chunk in remoteclip.main(dataset_name, retrieve_type, task_id_dir):
                    # with open(test_path, "a") as f:
                    #     f.write(json.dumps(chunk) + "\n\n")
                    yield json.dumps(chunk, ensure_ascii=False) + "\n\n"
            except Exception as e:
                yield json.dumps({"type": "error", "data": str(e)}, ensure_ascii=False) + "\n\n"
            finally:
                # 清理临时文件
                try:
                    if os.path.exists(file_dir):
                        rmtree(file_dir)
                except:
                    pass

        return StreamingResponse(stream_response(), media_type="text/plain")
    
    except Exception as e:
        return {"code": 500, "message": f"Internal server error: {str(e)}"}