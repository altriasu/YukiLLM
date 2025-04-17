import asyncio
import httpx
import json
from utils.config import * 

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
                        "Content-Type": "application/json",
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