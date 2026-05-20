"""
多Agent深度研究智能体 - 工具模块

提供搜索、网页抓取等工具函数
"""

import json
import re
from typing import List, Dict, Any, Optional
from config import config


class SearchTool:
    """网络搜索工具 - 基于Tavily API"""

    def __init__(self):
        self._client = None

    @property
    def client(self):
        if self._client is None:
            try:
                from tavily import TavilyClient
                self._client = TavilyClient(api_key=config.TAVILY_API_KEY)
            except ImportError:
                raise ImportError("请安装 tavily-python: pip install tavily-python")
        return self._client

    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        执行网络搜索

        Args:
            query: 搜索查询
            max_results: 最大结果数

        Returns:
            搜索结果列表
        """
        try:
            response = self.client.search(
                query=query,
                max_results=max_results,
                search_depth="advanced",
                include_answer=True,
            )
            results = []
            for item in response.get("results", []):
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "snippet": item.get("content", "")[:500],
                    "score": item.get("score", 0.0),
                })

            # 如果有Tavily的总结答案，也加入结果
            answer = response.get("answer")
            if answer:
                results.insert(0, {
                    "title": f"Tavily综合回答: {query}",
                    "url": "",
                    "snippet": answer,
                    "score": 1.0,
                })
            return results
        except Exception as e:
            print(f"⚠️ 搜索失败: {e}")
            return [{"title": "搜索失败", "url": "", "snippet": str(e), "score": 0.0}]


class WebScraper:
    """网页抓取工具"""

    @staticmethod
    def fetch_page(url: str, max_length: int = 3000) -> str:
        """
        抓取网页内容

        Args:
            url: 网页URL
            max_length: 最大返回字符数

        Returns:
            网页文本内容
        """
        try:
            import requests
            from bs4 import BeautifulSoup

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            resp = requests.get(url, headers=headers, timeout=15)
            resp.encoding = resp.apparent_encoding
            soup = BeautifulSoup(resp.text, "html.parser")

            # 移除脚本和样式
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()

            text = soup.get_text(separator="\n", strip=True)
            # 清理多余空行
            text = re.sub(r'\n{3,}', '\n\n', text)
            return text[:max_length]
        except Exception as e:
            return f"[抓取失败: {e}]"


class JSONParser:
    """JSON解析工具 - 从LLM输出中提取JSON"""

    @staticmethod
    def extract_json(text: str) -> Optional[Dict[str, Any]]:
        """
        从文本中提取JSON对象

        Args:
            text: 包含JSON的文本

        Returns:
            解析后的字典，失败返回None
        """
        # 尝试1: 查找 ```json ... ``` 代码块
        patterns = [
            r'```json\s*\n(.*?)\n\s*```',
            r'```\s*\n(.*?)\n\s*```',
            r'\{[\s\S]*\}',  # 最宽泛的匹配
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                json_str = match.group(1) if match.lastindex else match.group(0)
                json_str = json_str.strip()
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    # 尝试修复常见问题
                    try:
                        # 去掉尾部逗号
                        fixed = re.sub(r',\s*([\]}])', r'\1', json_str)
                        return json.loads(fixed)
                    except json.JSONDecodeError:
                        continue
        return None

    @staticmethod
    def extract_markdown_report(text: str) -> str:
        """
        从文本中提取Markdown报告

        Args:
            text: 包含报告的文本

        Returns:
            提取的Markdown内容
        """
        # 如果文本本身就是Markdown格式，直接返回
        if text.lstrip().startswith("#"):
            return text.strip()
        # 尝试从代码块中提取
        match = re.search(r'```(?:markdown)?\s*\n(.*?)\n\s*```', text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return text.strip()


# 全局工具实例
search_tool = SearchTool()
web_scraper = WebScraper()
json_parser = JSONParser()