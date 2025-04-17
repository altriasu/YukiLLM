from torch.utils.data import Dataset, DataLoader
from torchvision.transforms import ToPILImage
from PIL import Image
import argparse
import os
import io
import time
import base64
import torch
import numpy as np
import open_clip
import json
import aiofiles

from clip_benchmark.metrics.zeroshot_retrieval import recall_at_k, batchify, dataloader_with_indices
from clip_benchmark.datasets.builder import get_dataset_collate_fn
import torch.nn.functional as F

from utils.config import *
from utils.startLLM import retrieve_LLM, generate_prompt

def get_model():
    CLIP_model, preprocess_train, preprocess_val = open_clip.create_model_and_transforms(
        model_name=REMOTE_CLIP['model_name'],
        pretrained='openai',
        device=REMOTE_CLIP['device'],
        cache_dir=REMOTE_CLIP['cache_dir']
    )
    tokenize = open_clip.tokenize
    checkpoint = torch.load(REMOTE_CLIP['remoteclip_path'], map_location="cuda")
    msg = CLIP_model.load_state_dict(checkpoint)
    return CLIP_model, preprocess_train, preprocess_val, preprocess_val, tokenize

class ImageDataset(Dataset):
    def __init__(self, img_dir, transform):
        self.img_dir = img_dir
        self.images = sorted([f for f in os.listdir(img_dir) if f.lower().endswith(('.jpg', '.png', '.jpeg'))])
        self.transform = transform

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        img_path = os.path.join(self.img_dir, self.images[idx])
        image = Image.open(img_path).convert('RGB')
        return self.transform(image)
    
    def get_original_image(self, idx):
        img_path = os.path.join(self.img_dir, self.images[idx])
        image = Image.open(img_path).convert('RGB')
        return image
    
class TextDataset(Dataset):
    def __init__(self, caption_path):
        with open(caption_path, 'r', encoding='utf-8') as f:
            self.captions = [line.strip() for line in f.readlines() if line.strip()]

    def __len__(self):
        return len(self.captions)

    def __getitem__(self, idx):
        return self.captions[idx]
    
def compute_embeddings(dataloader, encode_fn, device):
    all_embeddings = []
    total = len(dataloader)
    parts = 4
    part_size = total // parts
    indices = []

    for i in range(parts):
        start = i * part_size
        end = (i + 1) * part_size if i < parts - 1 else total
        indices.append(end)

    j = 0
    for i, batch in enumerate(dataloader):
        batch = batch.to(device) if isinstance(batch, torch.Tensor) else batch
        with torch.no_grad():
            features = encode_fn(batch)
            features = F.normalize(features, dim=-1)
        all_embeddings.append(features.cpu())
        if i + 1 == indices[j]:
            j += 1
            yield {"type":"progress", "data":f"{j / parts * 100:.2f}% \n"}
        
    yield torch.cat(all_embeddings, dim=0)

def retrieval(image_dataset, text_dataset, model, preprocess, tokenize):
    image_loader = DataLoader(image_dataset, batch_size=REMOTE_CLIP['batch_size'],
                             shuffle=False) 
    text_loader = DataLoader(text_dataset, batch_size=REMOTE_CLIP['batch_size'],
                             shuffle=False, collate_fn=lambda x: tokenize(x).to(REMOTE_CLIP['device']))

    prev_chunk = None
    for chunk in compute_embeddings(image_loader, model.encode_image, REMOTE_CLIP['device']):
        if prev_chunk is not None:
            yield prev_chunk
        prev_chunk = chunk
    image_emb = prev_chunk

    prev_chunk = None
    for chunk in compute_embeddings(text_loader, model.encode_text, REMOTE_CLIP['device']):
        if prev_chunk is not None:
            yield prev_chunk
        prev_chunk = chunk
    text_emb = prev_chunk

    scores = text_emb @ image_emb.t()
    if scores.shape[1] == 1:
        scores = scores.t()

    topk = REMOTE_CLIP['topk'] if REMOTE_CLIP['topk'] < scores.shape[1] else scores.shape[1]
    topk_scores, topk_indices = scores.topk(k= topk , dim=1)

    yield (topk_indices.tolist()[0], topk_scores.tolist()[0])

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset_name', type=str)
    parser.add_argument('--retrieve_type', type=str)
    parser.add_argument('--input', type=str)
    args = parser.parse_args()
    return args

def adjust_scores_numpy(original_scores, judgments, alpha=0.1, max_score=1.0):
    scores = np.array(original_scores, dtype=np.float32)
    judgments = np.array(judgments, dtype=np.bool_)
    
    # 计算调整系数矩阵
    adjustment = np.where(
        judgments,
        1 + (1 - scores) * alpha,  # 对的调整公式
        1                          # 错的保持不变
    )
    
    # 应用调整
    adjusted = scores * adjustment
    
    # 应用分数上限
    return np.minimum(adjusted, max_score)

async def main(dataset_name: str, retrieve_type: str, input: str):
    model, _, _, preprocess_aug, tokenize = get_model()
    images_dir = os.path.join(DATASET_DIR, dataset_name, "images")
    text_dir = os.path.join(DATASET_DIR, dataset_name, "caption.txt")

    if retrieve_type == "img2txt":
        images_dir = input
    else:
        text_dir = input

    image_dataset = ImageDataset(images_dir, preprocess_aug)
    text_dataset = TextDataset(text_dir)

    prev_chunk = None
    for chunk in retrieval(image_dataset, text_dataset, model, preprocess_aug, tokenize):
        if prev_chunk is not None:
            yield prev_chunk
        prev_chunk = chunk
    
    if retrieve_type == "img2txt":
        yield {"type": "hint", "data": "### Top-k retrieved captions:\n"}
        descriptions = []
        top_index, scores = prev_chunk
        for i, index in enumerate(top_index):
            descriptions.append(text_dataset[index])
            yield {"type": "result_txt", "data": "- " + text_dataset[index] + f"   `Score: {scores[i]:.4f}`" + "\n"}
        
        yield {"type": "hint", "data": "<hr>"}
        yield {"type": "hint", "data": "<h4> 大语言模型判断中... </h4><br>"}
        prompt = generate_prompt(retrieve_type, descriptions, input)
        try:
            prev_chunk = None
            async for chunk in retrieve_LLM("ALIYUN", "qvq-max", prompt):
                if prev_chunk is not None:
                    yield prev_chunk
                prev_chunk = chunk
            
            llm_judegements = np.array(prev_chunk)
            if len(llm_judegements)!= len(scores):
                yield {"type": "reasoning_content", "message": "大模型判断数量和topk数量不一致, 已将未判断内容不变，如需高质量判断，请重试。"}
                llm_judegements = np.concatenate((llm_judegements, np.zeros(len(scores) - len(llm_judegements))))
            adjusted_scores = adjust_scores_numpy(scores, llm_judegements)
            sorted_indices = np.argsort(adjusted_scores)[::-1]
            index_array = np.array(top_index)
            index_array = index_array[sorted_indices]

            for i in sorted_indices[:10]:
                yield {"type": "content", "message": "- " + text_dataset[index_array[i]] + f"   `Score: {adjusted_scores[i]:.4f}`" + "\n"}

                
        except Exception as e:
            yield {"type": "error", "data": f"LLM processing error: {str(e)}"}
            
    elif retrieve_type == "txt2img":
        yield {"type": "hint", "data": "### Top-k retrieved images:\n"}
        images = []
        top_index, scores = prev_chunk
        for i, index in enumerate(top_index):
            try:
                pil_img = image_dataset.get_original_image(index)
                buf = io.BytesIO()
                pil_img.save(buf, format='JPEG')
                buf.seek(0)
                image_bytes = buf.read()
                img_base64 = base64.b64encode(image_bytes).decode('utf-8')
                images.append(img_base64)
                yield {
                    "type": "result_img",
                    "data": {
                        "image": f"data:image/jpeg;base64,{img_base64}",
                        "score": f"{scores[i]:.4f}"
                    }
                }
            except Exception as e:
                yield {"type": "error", "data": f"Image processing error: {str(e)}"}
        yield {"type": "hint", "data": "<hr>"}
        yield {"type": "hint", "data": "<h4> 大语言模型判断中... </h4><br>"}
        prompt = generate_prompt(retrieve_type, images, input)

        try:
            prev_chunk = None
            async for chunk in retrieve_LLM("ALIYUN", "qvq-max", prompt):
                if prev_chunk is not None:
                    yield prev_chunk
                prev_chunk = chunk
            
            llm_judegements = np.array(prev_chunk)
            if len(llm_judegements)!= len(scores):
                yield {"type": "reasoning_content", "message": "大模型判断数量和topk数量不一致, 已将未判断内容不变，如需高质量判断，请重试。"}
                llm_judegements = np.concatenate((llm_judegements, np.zeros(len(scores) - len(llm_judegements))))
            adjusted_scores = adjust_scores_numpy(scores, llm_judegements)
            sorted_indices = np.argsort(adjusted_scores)[::-1]
            index_array = np.array(top_index)
            index_array = index_array[sorted_indices]

            for i in sorted_indices[:10]:
                try:
                    pil_img = image_dataset.get_original_image(index_array[i])
                    buf = io.BytesIO()
                    pil_img.save(buf, format='JPEG')
                    buf.seek(0)
                    image_bytes = buf.read()
                    img_base64 = base64.b64encode(image_bytes).decode('utf-8')
                    yield {
                        "type": "img_content",
                        "message": {
                            "image": f"data:image/jpeg;base64,{img_base64}",
                            "score": f"{adjusted_scores[i]:.4f}"
                        }
                    }
                except Exception as e:
                    yield {"type": "error", "data": f"Image processing error: {str(e)}"}      
        except Exception as e:
            yield {"type": "error", "data": f"LLM processing error: {str(e)}"}
    else:
        yield {"type": "error", "data": "Invalid retrieve_type"}

    
if __name__ == "__main__":
    # args = parse_args()
    # main(args.dataset_name, args.retrieve_type, args.input)
    generate_prompt("img2txt")