import asyncio
import httpx
import json
import os
from typing import Dict, Any, List
from utils.config import *


def write_to_file(content: Dict[str, Any]):
    """将内容追加到JSON文件中"""
    file_path = os.path.join(STATIC_DIR, "test.json")
    
    # 如果文件不存在，创建并写入空列表
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=4)
    
    # 读取现有数据
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        data = []
    
    # 追加新数据
    data.append(content)
    
    # 写入文件
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


async def query_LLM_reasoning(platform: str, model: str, messages: List[Dict[str, Any]]):
    async with httpx.AsyncClient(timeout=None) as client:
        retry_count = 0
        while retry_count < LLM_CONFIG["MAX_API_RETRY"]:
            print(f"正在尝试第 {retry_count+1} 次 API 请求")
            try:
                response = await client.post(
                    LLM_CONFIG["BASE_URL"][platform],
                    headers={
                        "Authorization": f"Bearer {LLM_CONFIG['APIKEY'][platform]}",
                    },
                    json={
                        "model": model,
                        "messages": messages,
                        "stream": True,
                        "stream_options": {"include_usage": True},
                    },
                    timeout=None,
                )
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if not line.strip() or line.strip() == "data: [DONE]":
                        continue
                        
                    if line.startswith("data:"):
                        content = line[len("data:"):].strip()
                        try:
                            chunk_data = json.loads(content)
                            if not isinstance(chunk_data, dict):
                                continue

                            # 处理choices数据
                            choices = chunk_data.get("choices", [])
                            if choices and isinstance(choices, list):
                                delta = choices[0].get("delta", {})
                                
                                # 处理reasoning_content
                                if delta.get("reasoning_content"):
                                    data = {
                                        "type": "reasoning_content",
                                        "message": delta["reasoning_content"]
                                    }
                                    write_to_file(data)
                                    yield data
                                
                                # 处理content
                                if delta.get("content"):
                                    data = {
                                        "type": "content",
                                        "message": delta["content"]
                                    }
                                    write_to_file(data)
                                    yield data

                        except json.JSONDecodeError as e:
                            print(f"JSON解析失败: {e}\n原始数据: {content}")
                            continue

                return  # 成功完成

            except httpx.HTTPStatusError as e:
                print(f"HTTP错误: {e}")
                retry_count += 1
                await asyncio.sleep(LLM_CONFIG["REQ_TIME_GAP"])
            except Exception as e:
                print(f"其他错误: {e}")
                retry_count += 1
                await asyncio.sleep(LLM_CONFIG["REQ_TIME_GAP"])

        yield {"error": "【网络错误，请稍后再试】"}


async def query_LLM_reasoning_test(platform: str, model: str, messages: List[Dict[str, Any]]):
    """从JSON文件读取数据"""
    file_path = os.path.join(STATIC_DIR, "test.json")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for item in data:
                yield item
    except FileNotFoundError:
        print(f"文件未找到: {file_path}")
        yield {"error": "数据文件不存在"}
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        yield {"error": "数据文件格式错误"}