"""
动漫推荐助手 - 主程序
"""
import asyncio
import sys
from typing import Dict, List, Any

from core.request_builder import APIRequestBuilder
from core.bangumi_client import BangumiClient
from utils.config_loader import config
from utils.helper import helper

class AnimeRecommendationAssistant:
    """动漫推荐助手"""
    
    def __init__(self):
        self.request_builder = APIRequestBuilder()
        self.bangumi_client = BangumiClient()
    
    async def recommend(self, user_input: str) -> Dict[str, Any]:
        """生成推荐"""
        print(f"\n{'='*60}")
        print(f"📝 用户输入: {user_input}")
        print(f"{'='*60}")
        
        # 1. 使用DeepSeek构建搜索查询字符串
        print("\n🔍 正在分析用户意图...")
        query_string = await self.request_builder.build_search_params(user_input)  # 方法名不变，但返回字符串
    
        if not query_string or not isinstance(query_string, str):
            return {
                "success": False,
                "message": "无法解析您的请求，请尝试重新描述。",
                "recommendations": []
            }
    
        print(f"✅ 生成的搜索参数: {query_string}")
    
        # 2. 使用Bangumi API搜索 - 直接传入字符串
        print("\n🔍 正在搜索动漫...")
        search_result = await self.bangumi_client.search_subjects(query_string)  # 传入字符串
        
        if "error" in search_result:
            return {
                "success": False,
                "message": f"搜索失败: {search_result['error']}",
                "recommendations": []
            }
        
        anime_list = search_result.get("data", [])
        print(f"✅ 找到 {len(anime_list)} 个相关动漫")
        
        if not anime_list:
            return {
                "success": False,
                "message": "未找到匹配的动漫，请尝试其他描述。",
                "recommendations": []
            }
        
        # 3. 格式化结果
        print("\n📊 正在整理结果...")
        max_results = config.get("app.max_recommendations", 10)
        recommendations = []
        
        for i, anime in enumerate(anime_list[:max_results]):
            # 确保所有字段都有默认值
            anime_id = anime.get("id", 0)
            
            # 处理标题：优先使用中文名，没有则用原名
            name_cn = anime.get("name_cn", "").strip()
            name = anime.get("name", "").strip()
            title = name_cn if name_cn else (name if name else "未知标题")
            
            # 处理评分信息
            rating = anime.get("rating", {})
            score = rating.get("score", 0.0)
            votes = rating.get("total", 0)
            
            # 处理标签
            tags = []
            anime_tags = anime.get("tags", [])
            for tag in anime_tags[:5]:  # 最多取5个标签
                if isinstance(tag, dict) and "name" in tag:
                    tags.append(tag["name"])
            
            recommendations.append({
                "id": anime_id,
                "title": title,
                "original_title": name if name and name != title else "",
                "score": score,
                "votes": votes,
                "summary": anime.get("summary", ""),
                "url": f"https://bgm.tv/subject/{anime_id}" if anime_id else "",
                "image": anime.get("images", {}).get("large", ""),
                "tags": tags
            })
        
        return {
            "success": True,
            "total_found": len(anime_list),
            "recommendations": recommendations,
            "message": f"根据您的要求为您推荐以下动漫："
        }
    
    def display_results(self, result: Dict[str, Any]):
        """显示结果"""
        print(f"\n{'='*60}")
        
        if not result["success"]:
            print(f"❌ {result['message']}")
            return
        
        print(f"✅ {result['message']}")
        print(f"   共找到 {result['total_found']} 个结果，显示前 {len(result['recommendations'])} 个")
        
        # 显示搜索参数（可选）
        query_params = result.get("query_params", {})
        if query_params:
            param_str = " | ".join([f"{k}: {v}" for k, v in query_params.items()])
            print(f"   搜索参数: {param_str}")
        
        print(f"{'='*60}")
        
        for i, anime in enumerate(result["recommendations"], 1):
            print(f"\n{helper.format_anime_display(anime, i)}")
        
        print(f"\n{'='*60}")
        print("💡 提示: 输入更具体的描述可以获得更精准的推荐！")
        print(f"{'='*60}")

async def main():
    """命令行界面"""
    # 检查API密钥
    api_key = config.get("deepseek.api_key")
    if not api_key:
        print("错误: 请设置DEEPSEEK_API_KEY环境变量")
        print("例如: export DEEPSEEK_API_KEY=your_api_key_here")
        print("或者在当前目录创建 .env 文件并添加 DEEPSEEK_API_KEY=your_key")
        sys.exit(1)
    
    assistant = AnimeRecommendationAssistant()
    
    print(f"\n{'🎌'*15} 动漫推荐助手 {'🎌'*15}")
    print("基于DeepSeek + Bangumi API的智能动漫推荐系统")
    print(f"{'='*60}")
    print("📖 使用说明:")
    print("  - 用自然语言描述你想看的动漫")
    print("  - 系统会自动分析并生成Bangumi API查询字符串")
    print("  - 输入 'quit', 'exit' 或 'q' 退出")
    print(f"{'='*60}")
    print("💡 示例输入:")
    print("  - 我想看科幻战斗类的热门动漫")
    print("  - 推荐一些轻松搞笑的校园日常番")
    print("  - 有没有类似《进击的巨人》的动漫？")
    print(f"{'='*60}")
    
    while True:
        try:
            user_input = input("\n👉 请输入您的动漫需求: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q', '退出']:
                print(f"\n{'='*60}")
                print("👋 感谢使用动漫推荐助手，再见！")
                print(f"{'='*60}")
                break
            
            if not user_input:
                print("⚠️  请输入有效的描述")
                continue
            
            # 生成推荐
            result = await assistant.recommend(user_input)
            
            # 显示结果
            assistant.display_results(result)
            
        except KeyboardInterrupt:
            print(f"\n\n{'='*60}")
            print("👋 已退出程序")
            print(f"{'='*60}")
            break
        except Exception as e:
            print(f"\n❌ 发生未预期错误: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    # 确保缓存目录存在
    import os
    os.makedirs(".cache", exist_ok=True)
    
    # 运行主程序
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")