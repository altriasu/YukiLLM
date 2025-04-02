from fastapi import APIRouter, File, UploadFile
from settings import STATIC_DIR
from pydantic import BaseModel
from typing import List
import os

from typing import Union

datasets_api = APIRouter()

class Dataset(BaseModel):
    name: str
    description: Union[str, None] = None
    images: List[UploadFile]
    caption: str

@datasets_api.get("/")
async def datasets_details():
    datasets = []
    for dir in os.listdir(os.path.join(STATIC_DIR, "datasets")):
        imgsCount = len(os.listdir(os.path.join(STATIC_DIR, "datasets", dir, "images")))
        datasets.append({"name": dir, "description": f"{dir}数据集，有图片{imgsCount}张"})
    return datasets

@datasets_api.put("/")
async def datasets_upload(dataset: Dataset):
    datasets_all_names = []
    for dir in os.listdir(os.path.join(STATIC_DIR, "datasets")):
        datasets_all_names.append(dir)
    if dataset.name in datasets_all_names:
        return {"code": 400, "msg": "数据集名称重复，请重新命名", "data": {}}
    
    return {"code": 200, "msg": "上传成功", "data": {}}

@datasets_api.delete("/")
async def datasets_delete():
    pass



