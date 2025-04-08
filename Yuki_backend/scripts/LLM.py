import os
import openai
from openai import OpenAI
from PIL import Image
import asyncio
import httpx
import base64
import json
from typing import List, Dict

from scripts.config import * 

async def query_LLM_streaming(platform: str, model: str, messages: str):
    async with httpx.AsyncClient(timeout=None) as client:
        retry_count: int = 0
        while retry_count < LLM_CONFIG["MAX_API_RETRY"]:
            try:
                # 发起带 stream 的 POST 请求
                response = await client.post(
                    LLM_CONFIG["BASE_URL"][platform],
                    headers={
                        "Authorization": f"Bearer {LLM_CONFIG['APIKEY'][platform]}",
                    },
                    json={
                        "model": model,
                        "messages": messages,
                        "stream": True,
                        "stream_options": {
                            "include_usage": True
                        },
                    },
                    timeout=None,
                )

                response.raise_for_status()

                async for line in response.aiter_lines():
                    if line.strip() == "":
                        continue
                    if line.startswith("data:"):
                        content = line[len("data:"):].strip()
                        if content == "[DONE]":
                            break
                        try:
                            chunk_data = json.loads(content)

                            # 安全访问 choices 列表
                            if (
                                isinstance(chunk_data, dict)
                                and "choices" in chunk_data
                                and isinstance(chunk_data["choices"], list)
                                and len(chunk_data["choices"]) > 0
                            ):
                                delta_dict = chunk_data["choices"][0].get("delta", {})
                                delta = delta_dict.get("content", "")
                                if delta:
                                    print(delta)
                                    yield delta
                            else:
                                # 输出结构异常信息
                                print("⚠️ 非标准流数据结构:", chunk_data)

                        except Exception as e:
                            print("⚠️ JSON解析失败:", content)
                            yield f"流数据解析失败: {e}"

                return  # 成功后返回
            except httpx.HTTPStatusError as e:
                retry_count += 1
                await asyncio.sleep(LLM_CONFIG["REQ_TIME_GAP"])
            except Exception as e:
                retry_count += 1
                await asyncio.sleep(LLM_CONFIG["REQ_TIME_GAP"])

        yield "【网络错误，请稍后再试】"


async def start_LLM(platform: str, model: str, messages: List[Dict], image_path: str):
    if image_path:
        sys_prompt = {
            "role" : "system",
            "content": "你是一个多模态智能体，擅长从图像与文本中提取关键信息并进行推理。\n" +
                    "用户可以上传一张图片，并附带相关描述或问题。\n" +
                    "请结合图像与文本内容进行分析，做出合理推断，并解释你的推理依据。"
        }
        messages[0] = sys_prompt
        image_data = base64.b64encode(open(image_path, "rb").read()).decode("utf-8")
        img_prompt = {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpg;base64,{image_data}"}
            }
        messages.append(img_prompt)
    else:
        sys_prompt = {
            "role" : "system",
            "content": "你是一个语言理解与推理专家，擅长判断文本中的因果关系、对话逻辑、情感变化和事实一致性。\n" +
                    "请根据用户提供的文本，完成合理的推理任务。你的回答要清晰、简洁、逻辑严谨。"
        }
        messages[0] = sys_prompt
    async for chunk in query_LLM_streaming(platform, model, messages):
        yield chunk
