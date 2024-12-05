from openai import OpenAI
import json
from typing import Optional
from ...config import settings

class StepAIClient:
    """阶跃星辰AI客户端"""
    
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.STEPAI_API_KEY,
            base_url="https://api.stepfun.com/v1"
        )
        
    async def analyze_image(self, image_base64: str, prompt: str) -> Optional[str]:
        """调用阶跃星辰AI进行图片分析"""
        try:
            # 构建请求数据
            completion = self.client.chat.completions.create(
                model="step-1v-8k",  # 使用正确的模型名称
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的建筑工地安全检查员，负责识别施工现场的各类安全隐患。"
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ]
            )
            
            # 打印调试信息
            print(f"Response: {completion}")
            
            # 处理响应结果
            if hasattr(completion, 'choices') and len(completion.choices) > 0:
                content = completion.choices[0].message.content
                if isinstance(content, dict):
                    return json.dumps(content)
                return content
            else:
                raise Exception("Invalid response format")
                    
        except Exception as e:
            print(f"Analysis error: {str(e)}")
            raise Exception(f"AI分析失败: {str(e)}")