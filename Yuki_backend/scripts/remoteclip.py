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

from clip_benchmark.metrics.zeroshot_retrieval import recall_at_k, batchify, dataloader_with_indices
from clip_benchmark.datasets.builder import get_dataset_collate_fn
import torch.nn.functional as F

from scripts.config import *

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

    yield topk_indices.tolist()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset_name', type=str)
    parser.add_argument('--retrieve_type', type=str)
    parser.add_argument('--input', type=str)
    args = parser.parse_args()
    return args

def main(dataset_name: str, retrieve_type: str, input: str):
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
        for i in prev_chunk[0]:
            yield {"type": "result_txt", "data": text_dataset[i] + "\n"}
    elif retrieve_type == "txt2img":
        for i in prev_chunk[0]:
            pil_img = ToPILImage(image_dataset[i].cpu())
            buf = io.BytesIO()
            pil_img.save(buf, format='JPEG')
            buf.seek(0)
            image_bytes = buf.read()
            img_base64 = base64.b64encode(image_bytes).decode('utf-8')
            yield {"type": "result_img", "data": f"data:image/jpeg;base64,{img_base64}"}
    else:
        yield {"type": "error", "data": "Invalid retrieve_type"}


    
if __name__ == "__main__":
    args = parse_args()
    main(args.dataset_name, args.retrieve_type, args.input)