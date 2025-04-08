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

CHAT_CONFIG = {
    "platform" : ["ALIYUN", "OPENAI"],
    "embdingModel" : ["remoteClip"]
}


LLM_CONFIG = {
    "model" : {
        "ALIYUN" : ["qvq-max-latest", "qwen-vl-max-0125"], 
        "OPENAI" : ["chatgpt-4o"]
    },
    "APIKEY": {
        "ALIYUN" : os.getenv("DASHSCOPE_API_KEY"),
        "OPENAI" : os.getenv("OPENAI_API_KEY")
    },
    "BASE_URL": {
        "ALIYUN" : "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
        "OPENAI" : "https://api.openai.com/v1/chat/completions"
    },
    "MAX_API_RETRY" : 3,
    "REQ_TIME_GAP" : 10,
}

from settings import STATIC_DIR
DATASET_DIR = os.path.join(current_path, "../static/datasets/")