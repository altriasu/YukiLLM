import os
import sys

current_path = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

REMOTE_CLIP = {
    "model_name": "ViT-L-14",
    "remoteclip_path": os.path.join(current_path, "clip_checkpoints/models--chendelong--RemoteCLIP/snapshots/bf1d8a3ccf2ddbf7c875705e46373bfe542bce38/RemoteCLIP-ViT-L-14.pt"),
    "cache_dir": os.path.join(current_path, "cache/weights/open_clip/"),
    "topk": 15,
    "batch_size": 64,
    "num_workers": 8,
    "device": "cuda"
}

from settings import STATIC_DIR
DATASET_DIR = os.path.join(current_path, "../static/datasets/")