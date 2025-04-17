from fastapi import APIRouter, Request, UploadFile, File, Form
from fastapi.requests import Request
from settings import STATIC_DIR
from PIL import Image
from typing import List
from io import BytesIO
from tqdm import tqdm
from shutil import rmtree
import os

datasets_api = APIRouter()

@datasets_api.get("")
async def datasets_details():
    datasets = []
    for dir in os.listdir(os.path.join(STATIC_DIR, "datasets")):
        imgsCount = len(os.listdir(os.path.join(STATIC_DIR, "datasets", dir, "images")))
        datasets.append({"name": dir, "description": f"{dir}数据集，有图片{imgsCount}张"})
    return datasets

@datasets_api.post("")
async def datasets_upload(
    name: str = Form(...),
    description: str = Form(...),
    imgsFolder: List[UploadFile] = File(...),
    textFile: UploadFile = File(...)
):
    print("上传图片中...")
    dataset_path = os.path.join(STATIC_DIR, "datasets", name)
    os.makedirs(dataset_path, exist_ok=True)
    images_path = os.path.join(dataset_path, "images")
    os.makedirs(images_path, exist_ok=True)

    for img in tqdm(imgsFolder):
        file_name = img.filename.split("/")[-1]
        if not file_name.endswith(".jpg"):
            file_save_name = file_name.split(".")[-2] + ".jpg"
            img_bytes = await img.read()
            img_stream = BytesIO(img_bytes)
            Image.open(img_stream).convert("RGB").save(os.path.join(images_path, file_save_name))
        else:
            file_path = os.path.join(images_path, file_name)
            with open(file_path, 'wb') as f:
                f.write(await img.read())

    file_name = textFile.filename.split("/")[-1]
    text_file_path = os.path.join(dataset_path, "caption.txt")
    with open(text_file_path, 'wb') as f:
        f.write(await textFile.read())

    return {"code": 200, "msg": "上传成功", "data": {}}

@datasets_api.delete("")
async def datasets_delete(request: Request):
    request = await request.json()
    dataset_path = os.path.join(STATIC_DIR, "datasets", request["name"])
    if os.path.exists(dataset_path):
        rmtree(dataset_path)
        return {"code": 200, "msg": "删除成功", "data": {}}
    else:
        return {"code": 400, "msg": "数据集不存在", "data": {}}
    
