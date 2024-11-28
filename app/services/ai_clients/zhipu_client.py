import aiohttp
import json
import time
import hashlib
import base64
import hmac
from typing import Optional
from ...config import settings

class ZhipuAIClient:
    def __init__(self):
        self.api_key = settings.ZHIPU_API_KEY
        self.base_url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        
    def _generate_token(self) -> str:
        """生成JWT token"""
        try:
            api_key_parts = self.api_key.split('.')
            if len(api_key_parts) != 2:
                raise ValueError("Invalid API key format")
                
            key_id, secret = api_key_parts
            
            # 准备JWT header
            header = {
                "alg": "HS256",
                "sign_type": "SIGN"
            }
            header_str = base64.urlsafe_b64encode(
                json.dumps(header, separators=(',', ':')).encode()
            ).decode().rstrip('=')
            
            # 准备JWT payload
            payload = {
                "api_key": key_id,
                "exp": int(time.time()) + 3600,
                "timestamp": int(time.time())
            }
            payload_str = base64.urlsafe_b64encode(
                json.dumps(payload, separators=(',', ':')).encode()
            ).decode().rstrip('=')
            
            # 生成签名
            signature_raw = f"{header_str}.{payload_str}"
            signature = base64.urlsafe_b64encode(
                hmac.new(
                    secret.encode(),
                    signature_raw.encode(),
                    hashlib.sha256
                ).digest()
            ).decode().rstrip('=')
            
            return f"{signature_raw}.{signature}"
            
        except Exception as e:
            print(f"Token generation error: {str(e)}")  # 添加错误日志
            raise Exception(f"Token generation failed: {str(e)}")
    
    async def analyze_image(self, image_base64: str, prompt: str) -> Optional[str]:
        """调用智谱AI进行图片分析"""
        try:
            # 构建请求头
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self._generate_token()}"
            }
            
            # 构建请求体 - 注意content的顺序，图片需要在前
            data = {
                "model": "glm-4v",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ],
                "temperature": 0.8,  # 默认值
                "top_p": 0.6,       # 默认值
                "max_tokens": 1024,  # 最大支持1024
                "stream": False      # 同步调用
            }
            
            # 打印调试信息
            print("Sending request to GLM-4V with parameters:")
            print(f"Request URL: {self.base_url}")
            print(f"Content length: {len(prompt)}")
            print(f"Image data length: {len(image_base64)}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.base_url,
                    headers=headers,
                    json=data,
                    timeout=60  # 增加超时时间
                ) as response:
                    result = await response.json()
                    print(f"Response status: {response.status}")
                    print(f"Response body: {result}")
                    
                    if response.status != 200:
                        raise Exception(f"API request failed: {result}")
                    
                    return result['choices'][0]['message']['content']
                    
        except Exception as e:
            print(f"Error details: {str(e)}")
            raise Exception(f"AI分析失败: {str(e)}") 