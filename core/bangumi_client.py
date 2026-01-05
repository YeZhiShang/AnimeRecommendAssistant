"""
Bangumi API客户端
"""
import aiohttp
import asyncio
import json
from typing import Dict, List, Any, Optional
from utils.config_loader import config

class BangumiClient:
    """Bangumi API客户端"""
    
    def __init__(self):
        self.api_url = config.get("bangumi.api_url", "https://api.bgm.tv")
        self.user_agent = config.get("bangumi.user_agent")
        self.timeout = config.get("bangumi.request_timeout", 30)
    
    async def search_subjects(self, params):
        if isinstance(params, str):
            try:
                params = json.loads(params)
            except json.JSONDecodeError:
                return {"error": "搜索参数不是合法 JSON", "list": []}

        if not isinstance(params, dict):
            return {"error": "搜索参数类型错误", "list": []}
        if not params or "keyword" not in params:
            return {"error": "无效的搜索参数", "list": []}

        url = f"{self.api_url}/v0/search/subjects"

        headers = {
            "User-Agent": self.user_agent,
            "Content-Type": "application/json",
        }

        query = {
            "limit": 10,
            "offset": 0
        }

        print(f"请求Bangumi API: {url}")
        print(f"Query params: {query}")
        print(f"JSON body: {params}")

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    url,
                    headers=headers,
                    params=query,   # ✅ 只分页
                    json=params,    # ✅ JSON body
                    timeout=self.timeout
                ) as response:

                    text = await response.text()

                    if response.status == 200:
                        data = json.loads(text)
                        data.setdefault("list", [])
                        return data

                    return {"error": f"API错误 {response.status}", "list": []}

            except asyncio.TimeoutError:
                return {"error": "请求超时", "list": []}
            except Exception as e:
                return {"error": str(e), "list": []}

    
    async def get_subject_detail(self, subject_id: int) -> Optional[Dict]:
        """获取条目详情"""
        url = f"{self.api_url}/v0/subjects/{subject_id}"
        headers = {"User-Agent": self.user_agent}
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers, timeout=self.timeout) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
            except Exception:
                pass
        
        return None