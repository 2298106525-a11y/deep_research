"""
多Agent深度研究智能体 - Agent模块

实现各个专业Agent:
- PlannerAgent: 研究规划Agent
- SearchAgent: 信息搜索Agent
- AnalystAgent: 分析Agent
- CriticAgent: 评审Agent
- WriterAgent: 撰写Agent
"""

import json
from typing import Optional

from openai import OpenAI

from config import config
from models import (
    ResearchPlan, SubTask, SearchResults, SearchResult,
    AnalysisResult, KeyInsight, ReviewResult, ImprovementSuggestion,
    ResearchState
)
from tools import search_tool, json_parser
from promt import (
    PLANNER_PROMPT, SEARCH_PROMPT, ANALYST_PROMPT,
    CRITER_PROMPT, WRITER_PROMPT, TRANSLATOR_PROMPT
)


class BaseAgent:
    """Agent基类"""

    def __init__(self, name: str, system_prompt: str, model: str = None):
        self.name = name
        self.system_prompt = system_prompt
        self.model = model or config.LLM_MODEL
        self.client = OpenAI(
            api_key=config.LLM_API_KEY,
            base_url=config.LLM_BASE_URL,
        )

    def chat(self, user_message: str, temperature: float = 0.7) -> str:
        """
        调用LLM进行对话

        Args:
            user_message: 用户消息
            temperature: 温度参数

        Returns:
            LLM响应文本
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=temperature,
                max_tokens=4096,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ [{self.name}] LLM调用失败: {e}")
            return ""

    def chat_with_context(self, messages: list, temperature: float = 0.7) -> str:
        """
        使用上下文消息列表调用LLM

        Args:
            messages: 消息列表
            temperature: 温度参数

        Returns:
            LLM响应文本
        """
        try:
            full_messages = [{"role": "system", "content": self.system_prompt}] + messages
            response = self.client.chat.completions.create(
                model=self.model,
                messages=full_messages,
                temperature=temperature,
                max_tokens=4096,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ [{self.name}] LLM调用失败: {e}")
            return ""


class PlannerAgent(BaseAgent):
    """研究规划Agent - 将研究问题分解为子任务"""

    def __init__(self):
        super().__init__(name="Planner", system_prompt=PLANNER_PROMPT)

    def plan(self, topic: str, context: str = "") -> ResearchPlan:
        """
        生成研究计划

        Args:
            topic: 研究主题
            context: 额外上下文（如优化反馈）

        Returns:
            ResearchPlan对象
        """
        print(f"📋 [{self.name}] 正在制定研究计划...")

        user_msg = f"请为以下研究主题制定详细的研究计划:\n\n**研究主题:** {topic}"
        if context:
            user_msg += f"\n\n**参考信息/优化要求:**\n{context}"

        response = self.chat(user_msg, temperature=0.6)

        # 解析JSON
        data = json_parser.extract_json(response)
        if data:
            plan = ResearchPlan.from_dict(data)
            print(f"✅ [{self.name}] 研究计划制定完成，共{len(plan.subtasks)}个子任务")
            return plan

        # 解析失败，创建默认计划
        print(f"⚠️ [{self.name}] JSON解析失败，使用默认计划")
        return ResearchPlan(
            research_topic=topic,
            research_objective=f"深入研究{topic}的各个方面",
            subtasks=[
                SubTask(id=1, title=f"{topic}概述", description=f"搜索{topic}的基本信息和定义", search_queries=[topic, f"{topic} 定义"]),
                SubTask(id=2, title=f"{topic}最新发展", description=f"搜索{topic}的最新进展和趋势", search_queries=[f"{topic} 最新进展", f"{topic} 趋势"]),
                SubTask(id=3, title=f"{topic}应用案例", description=f"搜索{topic}的实际应用案例", search_queries=[f"{topic} 应用", f"{topic} 案例"]),
            ],
            key_questions=[f"{topic}是什么?", f"{topic}的发展趋势如何?", f"{topic}有哪些应用?"]
        )


class SearchAgent(BaseAgent):
    """信息搜索Agent - 执行搜索收集信息"""

    def __init__(self):
        super().__init__(name="Searcher", system_prompt=SEARCH_PROMPT)

    def search(self, query: str, subtask_description: str = "") -> SearchResults:
        """
        执行搜索任务

        Args:
            query: 搜索查询
            subtask_description: 子任务描述（提供上下文）

        Returns:
            SearchResults对象
        """
        print(f"🔍 [{self.name}] 正在搜索: {query}")

        # 1. 执行实际搜索
        raw_results = search_tool.search(query, max_results=config.MAX_SEARCH_RESULTS)

        # 2. 用LLM分析和整理搜索结果
        results_text = json.dumps(raw_results, ensure_ascii=False, indent=2)
        context_msg = f"搜索查询: {query}"
        if subtask_description:
            context_msg += f"\n研究背景: {subtask_description}"

        analysis_prompt = f"""{context_msg}

以下是搜索结果:
{results_text}

请分析这些搜索结果，提取关键发现，并以JSON格式输出:
```json
{{
  "search_query": "{query}",
  "results": [
    {{
      "title": "标题",
      "url": "URL",
      "snippet": "关键内容",
      "relevance_score": 0.9,
      "source_type": "academic/news/official/blog"
    }}
  ],
  "key_findings": ["关键发现1", "关键发现2"],
  "information_gaps": ["还需补充的信息"]
}}
```"""

        response = self.chat(analysis_prompt, temperature=0.3)

        # 3. 解析LLM输出
        data = json_parser.extract_json(response)
        if data:
            results = SearchResults(
                search_query=data.get("search_query", query),
                results=[
                    SearchResult(
                        title=r.get("title", ""),
                        url=r.get("url", ""),
                        snippet=r.get("snippet", ""),
                        relevance_score=r.get("relevance_score", 0.5),
                        source_type=r.get("source_type", "unknown"),
                    )
                    for r in data.get("results", [])
                ],
                key_findings=data.get("key_findings", []),
                information_gaps=data.get("information_gaps", []),
            )
        else:
            # 解析失败，直接使用原始结果
            results = SearchResults(
                search_query=query,
                results=[
                    SearchResult(title=r["title"], url=r["url"], snippet=r["snippet"])
                    for r in raw_results
                ],
                key_findings=[r["snippet"][:100] for r in raw_results[:3]],
            )

        print(f"✅ [{self.name}] 搜索完成，找到{len(results.results)}条结果，{len(results.key_findings)}个关键发现")
        return results


class AnalystAgent(BaseAgent):
    """分析Agent - 综合分析搜索结果"""

    def __init__(self):
        super().__init__(name="Analyst", system_prompt=ANALYST_PROMPT)

    def analyze(self, state: ResearchState) -> AnalysisResult:
        """
        分析所有搜索结果

        Args:
            state: 研究状态

        Returns:
            AnalysisResult对象
        """
        print(f"📊 [{self.name}] 正在分析研究数据...")

        # 汇总所有搜索结果
        all_findings = []
        all_gaps = []
        search_contexts = []

        for i, sr in enumerate(state.search_results):
            search_contexts.append(f"\n### 子任务 {i+1}: {sr.search_query}")
            for finding in sr.key_findings:
                search_contexts.append(f"- {finding}")
            all_findings.extend(sr.key_findings)
            all_gaps.extend(sr.information_gaps)

        combined_context = "\n".join(search_contexts)

        analysis_prompt = f"""**研究主题:** {state.topic}

**研究计划目标:** {state.plan.research_objective if state.plan else '深入研究'}

**收集到的信息:**
{combined_context}

**信息缺口:**
{json.dumps(list(set(all_gaps)), ensure_ascii=False)}

请对以上信息进行深度分析，识别关键洞察、模式和趋势，并以JSON格式输出分析结果。"""

        response = self.chat(analysis_prompt, temperature=0.5)

        # 解析结果
        data = json_parser.extract_json(response)
        if data:
            analysis = AnalysisResult(
                analysis_summary=data.get("analysis_summary", ""),
                key_insights=[
                    KeyInsight(
                        insight=ki.get("insight", ""),
                        evidence=ki.get("evidence", []),
                        confidence=ki.get("confidence", 0.5),
                    )
                    for ki in data.get("key_insights", [])
                ],
                patterns_identified=data.get("patterns_identified", []),
                contradictions=data.get("contradictions", []),
                information_gaps=data.get("information_gaps", []),
                preliminary_conclusions=data.get("preliminary_conclusions", []),
            )
        else:
            analysis = AnalysisResult(
                analysis_summary=response[:500] if response else "分析生成失败",
                preliminary_conclusions=all_findings[:5],
            )

        print(f"✅ [{self.name}] 分析完成，发现{len(analysis.key_insights)}个关键洞察")
        return analysis


class CriticAgent(BaseAgent):
    """评审Agent - 评估研究质量"""

    def __init__(self):
        super().__init__(name="Critic", system_prompt=CRITER_PROMPT)

    def review(self, state: ResearchState) -> ReviewResult:
        """
        评审研究质量

        Args:
            state: 当前研究状态

        Returns:
            ReviewResult对象
        """
        print(f"🔎 [{self.name}] 正在评审研究质量...")

        # 构建待评审内容摘要
        analysis_summary = ""
        if state.analysis:
            analysis_summary = f"""**分析摘要:** {state.analysis.analysis_summary}
**关键洞察数量:** {len(state.analysis.key_insights)}
**识别的模式:** {', '.join(state.analysis.patterns_identified)}
**初步结论:** {', '.join(state.analysis.preliminary_conclusions)}"""

        search_summary = f"共执行了{len(state.search_results)}次搜索"
        if state.search_results:
            total_results = sum(len(sr.results) for sr in state.search_results)
            total_findings = sum(len(sr.key_findings) for sr in state.search_results)
            search_summary += f"，获取{total_results}条结果，提取{total_findings}个关键发现"

        plan_summary = ""
        if state.plan:
            plan_summary = f"研究计划包含{len(state.plan.subtasks)}个子任务，目标：{state.plan.research_objective}"

        review_prompt = f"""请评审以下深度研究的质量:

**研究主题:** {state.topic}
**当前迭代:** {state.iteration}/{state.max_iterations}
**研究计划:** {plan_summary}
**搜索情况:** {search_summary}
**分析结果:**
{analysis_summary}

请按照评审标准进行评分和评审，并以JSON格式输出评审结果。"""

        response = self.chat(review_prompt, temperature=0.3)

        # 解析结果
        data = json_parser.extract_json(response)
        if data:
            review = ReviewResult(
                overall_score=data.get("overall_score", 0),
                dimension_scores=data.get("dimension_scores", {}),
                strengths=data.get("strengths", []),
                weaknesses=data.get("weaknesses", []),
                improvement_suggestions=[
                    ImprovementSuggestion(
                        area=s.get("area", ""),
                        suggestion=s.get("suggestion", ""),
                        priority=s.get("priority", "medium"),
                    )
                    for s in data.get("improvement_suggestions", [])
                ],
                verdict=data.get("verdict", "revise"),
                revision_focus=data.get("revision_focus", []),
            )
        else:
            review = ReviewResult(
                overall_score=60,
                verdict="pass",
                strengths=["已完成基础研究"],
                weaknesses=["无法解析评审结果"],
            )

        print(f"✅ [{self.name}] 评审完成，综合评分: {review.overall_score}/100，结论: {review.verdict}")
        return review


class WriterAgent(BaseAgent):
    """撰写Agent - 编写研究报告"""

    def __init__(self):
        super().__init__(name="Writer", system_prompt=WRITER_PROMPT)

    def write(self, state: ResearchState, review_feedback: str = "") -> str:
        """
        撰写研究报告

        Args:
            state: 研究状态
            review_feedback: 评审反馈（用于优化）

        Returns:
            Markdown格式的研究报告
        """
        print(f"✍️ [{self.name}] 正在撰写研究报告...")

        # 构建撰写上下文
        analysis_context = ""
        if state.analysis:
            insights_text = "\n".join([
                f"  - {ki.insight} (置信度: {ki.confidence})"
                for ki in state.analysis.key_insights
            ])
            analysis_context = f"""**分析摘要:** {state.analysis.analysis_summary}
**关键洞察:**
{insights_text}
**识别的模式:** {', '.join(state.analysis.patterns_identified)}
**初步结论:** {', '.join(state.analysis.preliminary_conclusions)}"""

        search_context = ""
        for i, sr in enumerate(state.search_results):
            search_context += f"\n### 搜索主题: {sr.search_query}\n"
            search_context += "关键发现:\n"
            for f in sr.key_findings:
                search_context += f"- {f}\n"

        key_questions = ""
        if state.plan:
            key_questions = "\n".join([f"- {q}" for q in state.plan.key_questions])

        write_prompt = f"""请根据以下研究数据，撰写一份高质量的研究报告:

**研究主题:** {state.topic}

**核心研究问题:**
{key_questions}

**搜索发现:**
{search_context}

**分析结果:**
{analysis_context}

**评审反馈:** {review_feedback if review_feedback else "无，请直接撰写完整报告"}

**要求:**
1. 报告结构完整，包含执行摘要、背景、方法、发现、分析、结论
2. 语言专业、逻辑清晰
3. 引用具体数据和发现支持结论
4. 使用Markdown格式输出"""

        response = self.chat(write_prompt, temperature=0.6)

        # 提取Markdown报告
        report = json_parser.extract_markdown_report(response)

        if not report:
            report = f"# {state.topic} 研究报告\n\n> 报告生成失败，请检查研究数据。\n\n{response}"

        print(f"✅ [{self.name}] 报告撰写完成，共{len(report)}字符")
        return report


class TranslatorAgent(BaseAgent):
    """翻译Agent - 将研究报告翻译成中文"""

    def __init__(self):
        super().__init__(name="Translator", system_prompt=TRANSLATOR_PROMPT)

    def translate(self, report: str, topic: str = "") -> str:
        """
        将英文报告翻译成中文

        Args:
            report: 英文研究报告（Markdown格式）
            topic: 研究主题（用于上下文）

        Returns:
            中文研究报告（Markdown格式）
        """
        print(f"🌐 [{self.name}] 正在翻译研究报告...")

        # 如果报告已经是中文或者很短，直接返回
        if not report or len(report) < 100:
            print(f"⚠️ [{self.name}] 报告内容为空或过短，跳过翻译")
            return report

        # 构建翻译请求
        translation_prompt = f"""请将以下关于"{topic}"的研究报告翻译成中文。

{report}

请确保：
1. 保持Markdown格式完整
2. 专业术语翻译准确
3. 语言流畅自然
4. 不要遗漏任何内容"""

        try:
            response = self.chat(translation_prompt, temperature=0.3)

            if response and len(response) > 100:
                print(f"✅ [{self.name}] 翻译完成，共{len(response)}字符")
                return response
            else:
                print(f"⚠️ [{self.name}] 翻译结果为空或过短，返回原文")
                return report

        except Exception as e:
            print(f"❌ [{self.name}] 翻译失败: {e}，返回原文")
            return report