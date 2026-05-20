# 🔬 多Agent深度研究智能体 (Deep Research Agent)

一个基于多Agent协作的深度研究系统，能够自动分解研究问题、搜索信息、分析数据、评审质量、生成研究报告并翻译成中文。

## ✨ 主要特性

- 🤖 **多Agent协作**: 6个专业Agent各司其职（规划/搜索/分析/评审/撰写/翻译）
- 🔄 **迭代优化**: 评审不通过时自动补充搜索和重新分析（最多3轮）
- 📊 **质量控制**: 5个维度评分（完整性/准确性/深度/客观性/结构性）
- 🌐 **中英双语**: 自动生成中英文两个版本的研究报告
- ⚙️ **高度可配置**: 迭代次数、质量阈值、搜索结果数量均可调整
- 📝 **结构化输出**: 自动生成专业的Markdown格式研究报告

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                   DeepResearchCoordinator                    │
│                       (协调器)                                │
├─────────┬─────────┬─────────┬─────────┬─────────┬───────────┤
│ Planner │Searcher │ Analyst │ Critic  │ Writer  │Translator │
│ (规划)  │ (搜索)  │ (分析)  │ (评审)  │ (撰写)  │ (翻译)    │
└─────────┴────┬────┴─────────┴─────────┴─────────┴───────────┘
               │
          ┌────┴────┐
          │  Tools  │
          │ Search  │
          │ Scraper │
          │ JSON    │
          └─────────┘
```

## 🔄 研究流程

```
[用户输入主题]
     │
     ▼
┌─────────────┐
│  Planner    │  阶段1: 将研究问题分解为子任务，制定搜索策略
└─────┬───────┘
      │
      ▼
┌─────────────┐
│  Searcher   │  阶段2: 按子任务执行网络搜索，整理搜索结果
└─────┬───────┘
      │
      ▼
┌─────────────┐
│  Analyst    │  阶段3: 综合分析，识别模式和趋势，形成洞察
└─────┬───────┘
      │
      ▼
┌─────────────┐
│  Critic     │  阶段4: 多维度质量评审（完整性/准确性/深度/客观性/结构性）
└─────┬───────┘
      │
 ┌────┴────┐
 │ 通过？  │──否──→ 补充搜索+重新分析 (最多3轮迭代)
 └────┬────┘
      │是
      ▼
┌─────────────┐
│  Writer     │  阶段5: 撰写结构化研究报告（英文）
└─────┬───────┘
      │
      ▼
┌─────────────┐
│ Translator  │  阶段6: 将报告翻译成中文
└─────┬───────┘
      │
      ▼
[输出中英文研究报告 (Markdown)]
```

## 📁 文件结构

```
deepresearch_agent/
├── promt.py          # 各Agent的提示词定义
├── config.py         # 配置管理（LLM、搜索API、参数）
├── models.py         # 数据模型（研究计划、搜索结果、分析结果等）
├── tools.py          # 工具模块（搜索、网页抓取、JSON解析）
├── agents.py         # Agent实现（Planner/Searcher/Analyst/Critic/Writer/Translator）
├── coordinator.py    # 协调器 - 管理整个研究流程
├── run.py            # 主入口
├── output/           # 研究报告输出目录（自动生成）
├── .env              # 环境变量配置文件（需自行创建）
├── .env.example      # 环境变量配置示例
├── requirements.txt  # Python依赖包列表
└── README.md         # 本文档
```

## 🛠️ 安装步骤

### 1. 克隆项目

```bash
git clone <repository-url>
cd deepreasearch_agent
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

或者手动安装：

```bash
pip install openai tavily-python python-dotenv requests beautifulsoup4
```

## ⚙️ 配置

### 1. 创建环境变量文件

复制 `.env.example` 为 `.env`：

```bash
cp .env.example .env
```

### 2. 配置 API Keys

编辑 `.env` 文件，填入你的 API Key：

```env
# LLM配置（必需）
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL=qwen-plus

# 搜索工具配置（必需）
TAVILY_API_KEY=your_tavily_api_key

# 研究流程配置（可选）
MAX_ITERATIONS=3
MIN_QUALITY_SCORE=70
MAX_SEARCH_RESULTS=10
```

**获取 Tavily API Key:**
- 访问 https://tavily.com 注册账号
- 免费额度每月1000次搜索

**支持的 LLM 提供商:**
- OpenAI (GPT-3.5/4)
- 阿里云通义千问 (Qwen)
- 其他兼容 OpenAI API 的服务

## 🚀 使用方式

### 命令行运行

```bash
# 直接传入研究主题
python run.py "人工智能在医疗领域的最新应用"

# 使用命名参数
python run.py --topic "量子计算的发展趋势"

# 自定义迭代次数和质量阈值
python run.py "大语言模型的安全性研究" -n 5 -s 80

# 交互式模式（不传参数）
python run.py
```

### Python代码调用

```python
from coordinator import DeepResearchCoordinator

# 创建协调器
coordinator = DeepResearchCoordinator()

# 执行研究
report = coordinator.run("你的研究主题")
print(report)
```

## 🤖 各Agent职责

| Agent | 职责 | 核心能力 |
|-------|------|----------|
| **Planner** | 研究规划 | 分解问题、制定子任务、确定搜索策略 |
| **Searcher** | 信息搜索 | 执行网络搜索、提取关键信息、评估信息质量 |
| **Analyst** | 深度分析 | 识别模式趋势、多角度分析、形成洞察 |
| **Critic** | 质量评审 | 多维度评分、识别不足、提出改进建议 |
| **Writer** | 报告撰写 | 结构化输出、引用证据、专业表达（英文） |
| **Translator** | 翻译 | 将英文报告翻译成流畅的中文，保留格式和专业术语 |

## 🔑 核心特性

- **多Agent协作**: 6个专业Agent各司其职，协同完成研究
- **迭代优化**: 评审不通过时自动补充搜索和重新分析
- **质量控制**: 5个维度（完整性/准确性/深度/客观性/结构性）评分
- **中英双语**: 自动生成中英文两个版本的研究报告
- **可配置**: 迭代次数、质量阈值、搜索结果数量均可调整
- **报告输出**: 自动生成结构化的Markdown研究报告（EN + ZH）

## 📊 输出示例

研究报告将保存到 `output/` 目录，每个研究会生成两个文件：

- `research_主题_时间_EN.md` - 英文原版报告
- `research_主题_时间_ZH.md` - 中文翻译版报告

报告格式如下：

```markdown
---
# 深度研究报告 / Deep Research Report

> **研究主题 / Topic:** xxx
> **生成时间 / Generated:** 2025-01-01 12:00:00
> **研究迭代 / Iterations:** 2轮
> **最终评分 / Final Score:** 82/100

---

## 执行摘要 / Executive Summary
...

## 研究背景 / Background
...

## 主要发现 / Key Findings
...

## 分析与讨论 / Analysis & Discussion
...

## 结论与建议 / Conclusions & Recommendations
...

## 参考来源 / References
...
```

## 🔧 技术栈

- **Python 3.8+**: 主要编程语言
- **OpenAI API**: LLM 调用接口
- **Tavily API**: 专业搜索引擎
- **python-dotenv**: 环境变量管理
- **Requests & BeautifulSoup**: 网页抓取
- **JSON**: 数据交换格式

## 📝 许可证

本项目采用 MIT 许可证。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

如有问题或建议，请提交 GitHub Issue。

---

⭐ 如果这个项目对你有帮助，请给个 Star！