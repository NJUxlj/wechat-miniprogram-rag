import json
import requests
from typing import Dict, Any
from ..core.config import settings

class DouBaoService:    
    def __init__(self):
        self.api_url = "https://maas-api.ml-platform-cn-beijing.volces.com/v1/chat"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.DOUBAO_AK}" # 使用 API Key 作为 Bearer Token
            }
    
    async def chat(self, messages: list, temperature: float = 0.7) -> Dict[str, Any]:
        """
        调用豆包API进行对话
        
        Args:
            messages: 对话历史
            temperature: 温度参数，控制随机性
            
        Returns:
            Dict: API响应
        """
        try:
            payload  = {
                "model": "doubao-v1",  # 使用豆包v1模型
                "messages": messages,
                "temperature": temperature,
                "top_p": 0.8,
                "stream": False
            }
            response = requests.post(  
                self.api_url,  
                headers=self.headers,  
                json=payload  
            )  

            if response.status_code!=200:
                raise Exception(f"API调用失败:{response.text}")
            
            return response.json()

            
        except Exception as e:
            raise Exception(f"豆包API调用失败: {str(e)}")

