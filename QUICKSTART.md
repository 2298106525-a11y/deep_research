# 🚀 快速开始指南

## 5分钟快速上手

### 1️⃣ 克隆项目

```bash
git clone <repository-url>
cd deepreasearch_agent
```

### 2️⃣ 安装依赖

```bash
pip install -r requirements.txt
```

### 3️⃣ 配置环境变量

复制配置文件并填入你的 API Keys：

```bash
cp .env.example .env
```

编辑 `.env` 文件，至少需要配置：

```env
LLM_API_KEY=your_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

**获取 API Keys:**
- **LLM API Key**: 
  - OpenAI: https://platform.openai.com/api-keys
  - 阿里云通义千问: https://dashscope.console.aliyun.com/apiKey
- **Tavily API Key**: https://tavily.com (免费额度 1000次/月)

### 4️⃣ 运行研究

#### 方式一：交互式模式

```bash
python run.py
```

然后输入你想研究的主题，例如：
```
请输入研究主题: 人工智能在医疗领域的最新应用
```

#### 方式二：命令行直接传入主题

```bash
python run.py "量子计算的发展趋势"
```

#### 方式三：自定义参数

```bash
python run.py "大语言模型的安全性研究" -n 5 -s 80
```

参数说明：
- `-n 5`: 最大迭代次数为 5（默认 3）
- `-s 80`: 质量分数阈值为 80（默认 70）

### 5️⃣ 查看结果

研究报告会自动保存到 `output/` 目录：

- `research_主题_时间_EN.md` - 英文原版报告
- `research_主题_时间_ZH.md` - 中文翻译版报告

---

## 💡 使用技巧

### 选择合适的研究主题

✅ **好的主题**：
- "人工智能在医疗诊断中的应用"
- "可再生能源技术的发展趋势"
- "区块链技术在供应链管理中的实践"

❌ **避免的主题**：
- 过于宽泛："科技"
- 过于简单："今天天气"
- 需要实时数据："今天的股票价格"

### 调整研究深度

- **快速研究**（适合简单问题）：
  ```bash
  python run.py "主题" -n 2 -s 60
  ```

- **深度研究**（适合复杂问题）：
  ```bash
  python run.py "主题" -n 5 -s 85
  ```

### 监控研究进度

系统会在控制台实时显示每个阶段的进度：

```
📋 阶段1: 制定研究计划
🔍 阶段2: 搜索收集信息
📊 阶段3: 深度分析
🔎 阶段4: 质量评审
✍️ 阶段5: 撰写研究报告
🌐 阶段6: 翻译成中文
```

---

## ❓ 常见问题

### Q: 提示 "API Key 未配置"？

A: 确保你已经：
1. 创建了 `.env` 文件
2. 正确填写了 `LLM_API_KEY` 和 `TAVILY_API_KEY`
3. 没有多余的空格或引号

### Q: 如何提高报告质量？

A: 
- 增加迭代次数：`-n 5`
- 提高质量阈值：`-s 85`
- 使用更强大的 LLM 模型（如 GPT-4）

### Q: 可以只用中文吗？

A: 当前版本会先生成英文报告再翻译成中文。如果只需要中文，可以修改 `coordinator.py` 跳过翻译步骤。

### Q: 如何更换 LLM 提供商？

A: 修改 `.env` 文件：

```env
# 使用 OpenAI
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4

# 使用阿里云
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL=qwen-plus
```

---

## 📚 更多资源

- [完整文档](README.md)
- [配置文件说明](.env.example)
- [提交 Issue](https://github.com/your-repo/issues)

---

祝你研究愉快！🎉
