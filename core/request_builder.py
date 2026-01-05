"""
DeepSeek API请求构造器 - 核心模块
将自然语言转换为Bangumi API搜索参数
"""
import json
import aiohttp
import asyncio
from typing import Dict, List, Any, Optional
from utils.config_loader import config
from utils.helper import helper

class APIRequestBuilder:
    """API请求构造器"""
    
    def __init__(self):
        self.api_key = config.get("deepseek.api_key")
        self.base_url = config.get("deepseek.base_url", "https://api.deepseek.com/v1")
        self.model = config.get("deepseek.model", "deepseek-chat")
        self.temperature = config.get("deepseek.temperature", 0.1)
        self.timeout = config.get("deepseek.timeout", 60)
        
        if not self.api_key:
            raise ValueError("请设置DEEPSEEK_API_KEY环境变量")
        
        # 构建系统提示词
        self.system_prompt = self._build_system_prompt()
    
    def _build_system_prompt(self) -> str:
        """构建系统提示词"""
        return f"""你是一个动画搜索API转换器。你的任务是将用户的自然语言描述转换为Bangumi API的搜索参数。

# Bangumi搜索API文档
- 接口: POST v0/search/subjects
- 主要参数:
  * keyword: 搜索关键词（字符串，对应标题搜索，如果用户输入中包含想找的动画的名字则有内容，否则为空）
  * sort: 排序方式（match（按照匹配程度）/heat（按照收藏人数）/rank（按照排名）/score（按照评分））（默认为match）
  * filter: 过滤条件（JSON对象，包含以下参数）
    * type: 条目类型（固定为2）
    * tag：根据用户输入提取至多5个tag，（tag列表：科幻、喜剧、同人、百合、校园、惊悚、后宫、机战、悬疑、恋爱、奇幻、推理、运动、耽美、音乐、战斗、冒险、萌系、穿越、玄幻、乙女、恐怖、历史、日常、剧情、武侠、美食、职场）
    * air_date: 根据用户输入提取动画播出的年份或季度，固定为一个范围（如“>=2020”、“<2009-10-01”）
    * rating: 评分区间（如“>=8”、“<5”）
    * rating_count: 用于按照评分人数筛选条目（如“>=200”、“<5000”）
    * rank: 排名区间（如“<=1000”、“>5000”）
    * nfsw: 是否包含R18内容（默认为false，除非用户输入改为true）

# 转换规则
1. 提取搜索关键词（即动画名字或部分名字，可以为空，但必须有该参数）
2. 提取tag，最多5个tag，严格按照上面给出的列表
3. 提取日期范围、评分区间和排名区间（如果用户输入）

# 输出格式
你必须返回一个严格的JSON对象，格式如下：
{{
  "keyword": "主要搜索关键词",
  "sort": "",
  filter: {{
      "type": [
        2
      ],
      "tag": [
        "从用户输入提取tag，用引号隔开"
      ],
      "air_date": [
        "从用户输入提取的日期范围，引号隔开，可以没有"
      ],
      "rating": [
        "从用户输入提取的评分区间，引号隔开，可以没有"
      ],
      rating_count": [
        "从用户输入提取的评分人数区间，引号隔开，可以没有"
      ],
      "rank": [
        "从用户输入提取的排名区间，引号隔开，可以没有"
      ]
      nsfw: false
  }}
}}

# 示例
用户输入："我想看科幻战斗类的热门动漫"
输出：
{{
  "keyword": "",
  "sort": "rank",
  filter: {{
      "type": [
        2
      ],
      "tag": [
        "科幻",
        "战斗"
      ],
      "rank": [
       ">=1000"
      ]
  }}
}}

用户输入："最近有什么好看的新番？"
输出：
{{
  "keyword": "",
  filter: {{
      "type": [
        2
      ],
      "air_date":[
        ">=2025-10-01"
      ],
      "rating": [
        ">=7"
      ]
  }}
}}

用户输入："我想找一部日常番，名字里带有“相合”"
输出：
{{
  "keyword": "相合",
  "sort": "match",
  filter: {{
      "type": [
        2
      ],
      "tag": [
        "日常"
      ]
  }}
}}

现在，请处理以下用户输入：
"""
    
    async def build_search_params(self, user_input: str) -> Dict[str, Any]:
        """将用户输入转换为API搜索参数"""
        # 构建消息
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_input}
        ]
        
        # 调用DeepSeek API
        params = await self._call_deepseek_api(messages)
        
        return params or {}
    
    async def _call_deepseek_api(self, messages: List[Dict]) -> Optional[Dict]:
        """调用DeepSeek API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": config.get("deepseek.max_tokens", 500),
            "response_format": {"type": "json_object"}
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=self.timeout
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        content = result["choices"][0]["message"]["content"]                    
                        return content
                    
                    else:
                        error_text = await response.text()
                        print(f"DeepSeek API错误: {response.status} - {error_text}")
                        return None
                        
            except asyncio.TimeoutError:
                print("DeepSeek API请求超时")
                return None
            except Exception as e:
                print(f"DeepSeek API请求异常: {e}")
                return None