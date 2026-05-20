"""
多Agent深度研究智能体 - 配置管理模块
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path, override=False)


class ResearchConfig:
    """研究智能体配置"""

    # LLM配置
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "qwen")
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", os.getenv("OPENAI_API_KEY", ""))
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "qwen3.6-flash")

    # 搜索工具配置 (Tavily Search)
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")

    # 研究流程配置
    MAX_ITERATIONS: int = int(os.getenv("MAX_ITERATIONS", "3"))
    MAX_SEARCH_RESULTS: int = int(os.getenv("MAX_SEARCH_RESULTS", "10"))
    MIN_QUALITY_SCORE: int = int(os.getenv("MIN_QUALITY_SCORE", "70"))

    # 输出配置
    OUTPUT_DIR: str = os.getenv("OUTPUT_DIR", str(Path(__file__).parent / "output"))

    @classmethod
    def validate(cls) -> bool:
        """验证必要配置是否已设置"""
        errors = []
        if not cls.LLM_API_KEY:
            errors.append("LLM_API_KEY 或 OPENAI_API_KEY 未配置")
        if not cls.TAVILY_API_KEY:
            errors.append("TAVILY_API_KEY 未配置 (用于网络搜索)")

        if errors:
            print("⚠️ 配置警告:")
            for err in errors:
                print(f"  - {err}")
            return False
        return True


config = ResearchConfig()