import os
import openai
from openai import OpenAI
from PIL import Image
import asyncio
import httpx
import base64
import json
from typing import List, Dict, AsyncGenerator, Union
from utils.config import * 
import re
from utils.LLMs.llmReasoning import query_LLM_reasoning, query_LLM_reasoning_test


async def start_LLM(platform: str, model: str, messages: List[Dict], image_path: str) -> AsyncGenerator[str, None]:
    if image_path:
        platform = "ALIYUN"
        model = "qvq-max"
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
        
        messages[-1]["content"] = [{
                    "type": "text",
                    "text": messages[-1]["content"]
                }]
        messages[-1]["content"].append(img_prompt)

        async for chunk in query_LLM_reasoning(platform, model, messages):
            yield chunk
    else:
        platform = "ALIYUN"
        model = "deepseek-r1-distill-llama-70b"
        # sys_prompt = {
        #     "role" : "system",
        #     "content": "你是一个语言理解与推理专家，擅长判断文本中的因果关系、对话逻辑、情感变化和事实一致性。\n" +
        #             "请根据用户提供的文本，完成合理的推理任务。你的回答要清晰、简洁、逻辑严谨。"
        # }
        del messages[0]
        async for chunk in query_LLM_reasoning(platform, model, messages):
            yield chunk



def extract_data(data: str) -> str:
    match = re.search(r"\[BEG\](.*?)\[END\]", data, re.DOTALL)
    if match:
        return match.group(1).strip()  # 去掉首尾空格
    return ""

async def retrieve_LLM(platform: str, model: str, messages: List[Dict]) -> AsyncGenerator[Dict, None]:
    content = ""
    async for chunk in query_LLM_reasoning(platform, model, messages):
        try:
            if isinstance(chunk, dict):
                if chunk.get("message") is None or chunk.get("message") == "":
                    continue
                elif chunk.get("type") == "content":
                    piece = chunk.get("message")
                    content += piece
                    continue
                else:
                    yield chunk
        except Exception as e:
            print(e)
    
    res = list(map(int, extract_data(content).split(" ")))
    print(res)
    yield res



            
def generate_template_input(retrieve_type: str, decs: Union[str, List[str]]) -> str:
    if retrieve_type == "img2txt":
        return  f"""
            You are given an image and several texts. Your task is to determine whether each text completely and accurately describes the image. If a text does, output 1; otherwise, output 0. The results for all texts should be on one line, separated by spaces.\n
            Important Note: You must be cautious when assigning a 1, as the final outcome heavily depends on the accuracy of texts marked as 1. Any incorrect assignment of 1 will significantly degrade the performance of the results. However, missing a valid 1 will not negatively impact the overall result. Therefore, prioritize precision over recall when determining 1. \n
            Text Descriptions: {decs}\n
            Output Rules:\n
            The first line of your response must contain the evaluation results wrapped in [BEG] and [END]. Example: [BEG] 1 0 0 1 0 [END].\n
            """.strip()
    elif retrieve_type == "txt2img":
        return  f"""
            You are given a text and several images. Your task is to determine whether each image completely and accurately describes the text. If an image does, output 1; otherwise, output 0. The results for all images should be on one line, separated by spaces.\n
            Important Note: You must be cautious when assigning a 1, as the final outcome heavily depends on the accuracy of images marked as 1. Any incorrect assignment of 1 will significantly degrade the performance of the results. However, missing a valid 1 will not negatively impact the overall result. Therefore, prioritize precision over recall when determining 1. \n
            Text Description: {decs}\n
            The first line of your response must contain the evaluation results wrapped in [BEG] and [END]. Example: [BEG] 1 0 0 1 0 [END].\n
            """.strip()


def generate_prompt(retrieve_type: str, content_array: List[str], input: str) -> List[Dict]:
    template_dir = os.path.join(STATIC_DIR, "prompt_template")
    if retrieve_type == "img2txt":
        template_prompt = [
            {
                "role": "system",
                "content": "你是一个能将图片和多个文本进行对比的专家, 用户会发送一张图片和和多个这个图片的描述, 请你仔细对比图片和每个描述, 简洁准确的回答用户的要求。"
            },
            {
                "role": "user",
                "content" : []
            },
            {
                "role": "assistant",
                "content" : ""
            },
            {
                "role": "user",
                "content": []
            }
        ]
        with open(os.path.join(template_dir, "template1.json"), 'r', encoding='utf-8') as f:
            data = json.load(f)

            template_output = "[BEG] "
            descriptions = []
            for i in data:
                descriptions.append(i.get("desc"))
                if i.get("matched"):
                    template_output += "1 "
                else:
                    template_output += "0 "
            template_input = generate_template_input(retrieve_type,descriptions)
            template_output += "[END]"

        template_prompt[1]["content"].append({
            "type": "text",
            "text": template_input
        })
        base64img = base64.b64encode(open(os.path.join(template_dir, "template1.jpg"), 'rb').read()).decode('utf-8')
        template_prompt[1]["content"].append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpg;base64,{base64img}"}
        })
        template_prompt[2]["content"] = template_output

        template_input = generate_template_input(retrieve_type, content_array)
        img_name = os.listdir(input)
        img_path = os.path.join(input, img_name[0])
        base64img = base64.b64encode(open(img_path, 'rb').read()).decode('utf-8')
        template_prompt[3]["content"].append({
            "type": "text",
            "text": template_input
        })
        template_prompt[3]["content"].append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpg;base64,{base64img}"}
        })
    
    elif retrieve_type == "txt2img":
        template_prompt = [
            {
                "role": "system",
                "content": "你是一个能将文本和多个图像进行对比的专家, 用户会发送一段文字和和多个图片, 请你仔细对比文本和每个图片, 简洁准确的回答用户的要求。"
            },
            {
                "role": "user",
                "content" : []
            },
            {
                "role": "assistant",
                "content" : ""
            },
            {
                "role": "user",
                "content": []
            }
        ]
        with open(os.path.join(template_dir, "template2.txt"), 'r', encoding='utf-8') as f:
            data = f.read()
            template_input = generate_template_input(retrieve_type, data)
            template_prompt[1]["content"].append({
                "type": "text",
                "text": template_input
            })
            
        img_names = os.listdir(os.path.join(template_dir, "template2"))
        template_output = "[BEG] "
        for img_name in img_names:
            if "true" in img_name.lower():
                template_output += "1 "
            else:
                template_output += "0 "
        
            img_path = os.path.join(template_dir, "template2", img_name)
            base64img = base64.b64encode(open(img_path, 'rb').read()).decode('utf-8')
            template_prompt[1]["content"].append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpg;base64,{base64img}"}
            })
        template_output += "[END]"
        template_prompt[2]["content"] = template_output

        with open(input, 'r', encoding='utf-8') as f:
            data = f.read()
            template_input = generate_template_input(retrieve_type, data)
            template_prompt[3]["content"].append({
                "type": "text",
                "text": template_input
            })

        for based_img in content_array:
            template_prompt[3]["content"].append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpg;base64,{based_img}"}
            })
    
    return template_prompt



