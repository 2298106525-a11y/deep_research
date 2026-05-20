# 📁 项目结构说明

本文档详细说明项目的文件结构和各模块的职责。

## 核心文件

### 1. 入口文件

#### `run.py` - 主程序入口
- **职责**: 提供命令行接口，处理用户输入
- **功能**:
  - 解析命令行参数（主题、迭代次数、质量阈值）
  - 支持交互式模式和单次运行模式
  - 初始化协调器并启动研究流程
- **使用示例**:
  ```bash
  python run.py "研究主题"
  python run.py --topic "主题" -n 5 -s 80
  ```

### 2. 核心模块

#### `coordinator.py` - 协调器
- **职责**: 管理整个研究流程的状态转换和Agent协作
- **核心类**: `DeepResearchCoordinator`
- **工作流程**:
  1. 初始化所有Agent
  2. 执行6个阶段的研究流程
  3. 处理迭代优化逻辑
  4. 保存研究报告（中英文版本）
- **关键方法**:
  - `run(topic)`: 执行完整研究流程
  - `_build_review_feedback()`: 构建评审反馈
  - `_save_report()`: 保存报告到文件

#### `agents.py` - Agent实现
- **职责**: 实现6个专业Agent
- **核心类**:
  - `BaseAgent`: Agent基类，提供LLM调用接口
  - `PlannerAgent`: 研究规划Agent
  - `SearchAgent`: 信息搜索Agent
  - `AnalystAgent`: 深度分析Agent
  - `CriticAgent`: 质量评审Agent
  - `WriterAgent`: 报告撰写Agent
  - `TranslatorAgent`: 翻译Agent（新增）
- **每个Agent的功能**:
  - 继承自BaseAgent
  - 有专属的系统提示词
  - 实现特定的研究方法
  - 返回结构化的结果对象

#### `models.py` - 数据模型
- **职责**: 定义研究中使用的数据结构
- **核心模型**:
  - `ResearchPhase`: 研究阶段枚举
  - `ReviewVerdict`: 评审结论枚举
  - `SubTask`: 研究子任务
  - `ResearchPlan`: 研究计划
  - `SearchResult`: 单条搜索结果
  - `SearchResults`: 搜索结果集合
  - `KeyInsight`: 关键洞察
  - `AnalysisResult`: 分析结果
  - `ImprovementSuggestion`: 改进建议
  - `ReviewResult`: 评审结果
  - `ResearchState`: 研究状态（在各Agent间传递）

#### `promt.py` - 提示词管理
- **职责**: 定义所有Agent的系统提示词
- **提示词列表**:
  - `PLANNER_PROMPT`: 规划Agent提示词
  - `SEARCH_PROMPT`: 搜索Agent提示词
  - `ANALYST_PROMPT`: 分析Agent提示词
  - `CRITER_PROMPT`: 评审Agent提示词
  - `WRITER_PROMPT`: 撰写Agent提示词
  - `TRANSLATOR_PROMPT`: 翻译Agent提示词（新增）
- **设计原则**:
  - 明确Agent职责
  - 规定输出格式（通常是JSON）
  - 提供具体的操作指南

#### `tools.py` - 工具模块
- **职责**: 提供底层工具函数
- **主要工具**:
  - `search_tool`: Tavily搜索引擎封装
  - `json_parser`: JSON提取和解析工具
  - 网页抓取功能（如需要）

#### `config.py` - 配置管理
- **职责**: 管理所有配置项
- **配置类别**:
  - LLM配置（API Key、URL、模型）
  - 搜索工具配置（Tavily API Key）
  - 研究流程配置（迭代次数、质量阈值等）
  - 输出配置（输出目录）
- **加载方式**: 从环境变量或.env文件加载

### 3. 配置文件

#### `.env.example` - 环境变量示例
- **用途**: 提供配置模板
- **包含**:
  - 必需配置（API Keys）
  - 可选配置（流程参数）
  - 详细的注释说明
- **使用方法**: 复制为`.env`并填入实际值

#### `.gitignore` - Git忽略规则
- **忽略内容**:
  - Python缓存文件
  - 虚拟环境
  - .env文件（保护API Keys）
  - output目录（研究报告）
  - IDE配置文件

#### `requirements.txt` - Python依赖
- **依赖包**:
  - openai: LLM API客户端
  - tavily-python: 搜索引擎
  - python-dotenv: 环境变量管理
  - requests: HTTP请求
  - beautifulsoup4: HTML解析
  - tqdm: 进度条

### 4. 文档文件

#### `README.md` - 项目主文档
- **内容**:
  - 项目介绍和特性
  - 系统架构图
  - 研究流程图
  - 安装和配置指南
  - 使用示例
  - Agent职责说明
  - 技术栈

#### `QUICKSTART.md` - 快速开始指南
- **内容**:
  - 5分钟快速上手教程
  - 详细的使用步骤
  - 常见问题解答
  - 使用技巧

#### `PROJECT_STRUCTURE.md` - 本文档
- **内容**: 项目结构和模块说明

### 5. 输出目录

#### `output/` - 研究报告存储
- **自动生成**: 首次运行时创建
- **文件格式**: Markdown
- **命名规则**: `research_主题_时间_EN.md` 和 `research_主题_时间_ZH.md`
- **注意**: 已在.gitignore中忽略

---

## 数据流图

```
用户输入主题
    ↓
run.py (解析参数)
    ↓
coordinator.py (创建ResearchState)
    ↓
┌─────────────────────────────────┐
│ 阶段1: PlannerAgent             │
│ - 读取: topic                   │
│ - 输出: ResearchPlan            │
└──────────────┬──────────────────┘
               ↓
┌─────────────────────────────────┐
│ 阶段2: SearchAgent (循环)       │
│ - 读取: SubTask.search_queries  │
│ - 输出: List[SearchResults]     │
└──────────────┬──────────────────┘
               ↓
┌─────────────────────────────────┐
│ 阶段3: AnalystAgent             │
│ - 读取: ResearchState           │
│ - 输出: AnalysisResult          │
└──────────────┬──────────────────┘
               ↓
┌─────────────────────────────────┐
│ 阶段4: CriticAgent              │
│ - 读取: ResearchState           │
│ - 输出: ReviewResult            │
└──────────────┬──────────────────┘
               ↓
        ┌──────┴──────┐
        │ 评分 >= 阈值？│
        └──┬─────┬────┘
      否   │     │ 是
    ┌──────┘     └──────┐
    ↓                    ↓
重新搜索/分析      ┌─────────────────────┐
(最多3轮)          │ 阶段5: WriterAgent   │
                   │ - 读取: ResearchState│
                   │ - 输出: report (EN)  │
                   └──────────┬──────────┘
                              ↓
                   ┌─────────────────────┐
                   │阶段6: TranslatorAgent│
                   │ - 读取: report (EN)  │
                   │ - 输出: report (ZH)  │
                   └──────────┬──────────┘
                              ↓
                      保存到 output/
```

---

## 模块依赖关系

```
run.py
  ├── coordinator.py
  │     ├── agents.py
  │     │     ├── BaseAgent
  │     │     │     └── config.py
  │     │     ├── PlannerAgent
  │     │     ├── SearchAgent
  │     │     ├── AnalystAgent
  │     │     ├── CriticAgent
  │     │     ├── WriterAgent
  │     │     └── TranslatorAgent (新增)
  │     │           └── promt.py
  │     ├── models.py
  │     └── tools.py
  └── config.py
```

---

## 扩展开发指南

### 添加新的Agent

1. 在 `promt.py` 中添加提示词
2. 在 `agents.py` 中创建Agent类（继承BaseAgent）
3. 在 `models.py` 中添加相关数据模型（如需要）
4. 在 `coordinator.py` 中集成新Agent

### 修改研究流程

编辑 `coordinator.py` 的 `run()` 方法，调整阶段顺序或添加新阶段。

### 自定义输出格式

修改 `coordinator.py` 的 `_save_report()` 方法，支持其他格式（如PDF、HTML）。

### 更换搜索引擎

修改 `tools.py` 中的 `search_tool` 实现，替换为其他搜索API。

---

## 性能优化建议

1. **减少Token消耗**:
   - 降低 `MAX_SEARCH_RESULTS`
   - 精简提示词
   - 使用更小的模型

2. **提高研究速度**:
   - 减少 `MAX_ITERATIONS`
   - 降低 `MIN_QUALITY_SCORE`
   - 并行化搜索（需修改代码）

3. **提高报告质量**:
   - 增加 `MAX_ITERATIONS`
   - 提高 `MIN_QUALITY_SCORE`
   - 使用更强大的LLM模型

---

## 调试技巧

1. **查看中间结果**:
   - 在每个阶段后打印state对象
   - 检查Agent的输出是否符合预期

2. **测试单个Agent**:
   ```python
   from agents import PlannerAgent
   planner = PlannerAgent()
   plan = planner.plan("测试主题")
   print(plan)
   ```

3. **检查配置**:
   ```python
   from config import config
   print(config.validate())
   ```

4. **查看详细错误**:
   - 捕获异常并打印traceback
   - 检查API Key是否正确
   - 验证网络连接

---

希望这份文档能帮助你更好地理解和使用本项目！
