"""
辅助工具函数
"""
import string
import hashlib
from typing import Any, Dict, List, Optional

class Helper:
    """工具类"""
    
    @staticmethod
    def calculate_md5(text: str) -> str:
        """计算文本的MD5哈希值"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    @staticmethod
    def format_anime_display(anime: Dict, index: int) -> str:
        """格式化动漫显示信息"""
        lines = []
        
        # 标题
        title = anime.get("title")
        lines.append(f"{index}. {title}")
        
        # 原始标题（如果与中文标题不同）
        if anime.get("title") and anime.get("original_title") != title:
            lines.append(f"   原名: {anime['original_title']}")
        
        # 评分
        if anime.get("score"):
            lines.append(f"   评分: {anime['score']}/10 ({anime.get('votes', 0)}人评分)")
        
        # 简介
        if anime.get("summary"):
            summary = anime["summary"].replace("\r\n", "").strip()
            lines.append(f"   简介: {summary}")
        
        # 标签
        if anime.get("tags"):
            tags = anime.get("tags", [])
            lines.append(f"   标签: {', '.join(tags)}")
        
        # URL
        if anime.get("id"):
            lines.append(f"   链接: https://bgm.tv/subject/{anime['id']}")
        
        return "\n".join(lines)

helper = Helper()