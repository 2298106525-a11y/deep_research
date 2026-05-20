"""
多Agent深度研究智能体 - 协调器模块

协调器是整个系统的核心，负责:
1. 管理研究流程的状态转换
2. 协调各Agent之间的协作
3. 处理迭代优化逻辑
4. 输出研究报告
"""

import os
from datetime import datetime
from pathlib import Path

from config import config
from models import ResearchState, ResearchPhase
from agents import PlannerAgent, SearchAgent, AnalystAgent, CriticAgent, WriterAgent


class DeepResearchCoordinator:
    """
    深度研究协调器

    协调多个专业Agent完成深度研究任务，流程如下:

    [用户输入主题]
         │
         ▼
    ┌─────────────┐
    │  Planner    │  阶段1: 制定研究计划
    └─────┬───────┘
          │
          ▼
    ┌─────────────┐
    │  Searcher   │  阶段2: 多轮搜索收集信息
    └─────┬───────┘
          │
          ▼
    ┌─────────────┐
    │  Analyst    │  阶段3: 综合分析
    └─────┬───────┘
          │
          ▼
    ┌─────────────┐
    │  Critic     │  阶段4: 质量评审
    └─────┬───────┘
          │
     ┌────┴────┐
     │ 通过？  │──否──→ 回到阶段2/3/4 (最多N轮)
     └────┬────┘
          │是
          ▼
    ┌─────────────┐
    │  Writer     │  阶段5: 撰写报告
    └─────┬───────┘
          │
          ▼
    [输出研究报告]
    """

    def __init__(self):
        """初始化协调器和所有Agent"""
        print("🔄 正在初始化深度研究智能体系统...")

        self.planner = PlannerAgent()
        self.searcher = SearchAgent()
        self.analyst = AnalystAgent()
        self.critic = CriticAgent()
        self.writer = WriterAgent()

        # 创建输出目录
        self.output_dir = Path(config.OUTPUT_DIR)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        print("✅ 深度研究智能体系统初始化完成")
        print(f"   - Planner Agent: 研究规划")
        print(f"   - Search Agent: 信息搜索")
        print(f"   - Analyst Agent: 深度分析")
        print(f"   - Critic Agent: 质量评审")
        print(f"   - Writer Agent: 报告撰写")
        print(f"   - Translator Agent: 中文翻译")

    def run(self, topic: str) -> str:
        """
        执行完整的研究流程

        Args:
            topic: 研究主题

        Returns:
            Markdown格式的研究报告
        """
        state = ResearchState(
            topic=topic,
            max_iterations=config.MAX_ITERATIONS,
        )

        print(f"\n{'='*70}")
        print(f"🚀 开始深度研究: {topic}")
        print(f"   最大迭代次数: {state.max_iterations}")
        print(f"   质量阈值: {config.MIN_QUALITY_SCORE}分")
        print(f"{'='*70}\n")

        # ======== 阶段1: 规划 ========
        state.current_phase = ResearchPhase.PLANNING
        state.add_message("开始研究规划")
        self._print_phase("📋 阶段1: 制定研究计划")

        state.plan = self.planner.plan(topic)

        if state.plan.subtasks:
            print(f"\n  研究计划概要:")
            print(f"  主题: {state.plan.research_topic}")
            print(f"  目标: {state.plan.research_objective}")
            print(f"  子任务数: {len(state.plan.subtasks)}")
            for st in state.plan.subtasks:
                print(f"    [{st.priority.upper()}] {st.title}: {st.description}")
            print(f"  核心问题: {', '.join(state.plan.key_questions)}")

        # ======== 迭代研究流程 ========
        while state.iteration < state.max_iterations:
            state.iteration += 1
            print(f"\n{'─'*70}")
            print(f"🔄 研究迭代 {state.iteration}/{state.max_iterations}")
            print(f"{'─'*70}\n")

            # ======== 阶段2: 搜索 ========
            state.current_phase = ResearchPhase.SEARCHING
            state.add_message(f"第{state.iteration}轮搜索")
            self._print_phase("🔍 阶段2: 搜索收集信息")

            state.search_results = []  # 清空旧结果
            for subtask in state.plan.subtasks:
                subtask.status = "in_progress"
                for query in subtask.search_queries:
                    result = self.searcher.search(query, subtask.description)
                    state.search_results.append(result)
                subtask.status = "completed"
                print()

            # ======== 阶段3: 分析 ========
            state.current_phase = ResearchPhase.ANALYZING
            state.add_message(f"第{state.iteration}轮分析")
            self._print_phase("📊 阶段3: 深度分析")

            state.analysis = self.analyst.analyze(state)

            if state.analysis.key_insights:
                print(f"\n  分析摘要:")
                print(f"  {state.analysis.analysis_summary[:200]}...")
                print(f"  关键洞察 ({len(state.analysis.key_insights)}):")
                for ki in state.analysis.key_insights[:3]:
                    print(f"    • {ki.insight} (置信度: {ki.confidence})")
                if state.analysis.preliminary_conclusions:
                    print(f"  初步结论:")
                    for c in state.analysis.preliminary_conclusions[:3]:
                        print(f"    → {c}")

            # ======== 阶段4: 评审 ========
            state.current_phase = ResearchPhase.REVIEWING
            state.add_message(f"第{state.iteration}轮评审")
            self._print_phase("🔎 阶段4: 质量评审")

            state.review = self.critic.review(state)

            print(f"\n  评审结果:")
            print(f"  综合评分: {state.review.overall_score}/100")
            for dim, score in state.review.dimension_scores.items():
                print(f"    {dim}: {score}")
            print(f"  结论: {state.review.verdict.upper()}")
            if state.review.strengths:
                print(f"  优点: {', '.join(state.review.strengths[:3])}")
            if state.review.weaknesses:
                print(f"  不足: {', '.join(state.review.weaknesses[:3])}")

            # 判断是否通过
            if state.review.is_pass and state.review.overall_score >= config.MIN_QUALITY_SCORE:
                print(f"\n✅ 评审通过! (评分: {state.review.overall_score})")
                break

            # 需要优化
            if state.iteration < state.max_iterations:
                print(f"\n⚠️ 评审未通过，准备优化... (评分: {state.review.overall_score}, 阈值: {config.MIN_QUALITY_SCORE})")
                state.current_phase = ResearchPhase.REFINING

                # 根据评审反馈优化
                feedback = self._build_review_feedback(state)
                improvement_focus = ", ".join(state.review.revision_focus[:3]) if state.review.revision_focus else "整体改进"

                # 如果搜索评分低，重新搜索并扩展
                search_score = state.review.dimension_scores.get("completeness", 100)
                if search_score < config.MIN_QUALITY_SCORE:
                    print(f"  → 补充搜索 (完整性评分不足: {search_score})")
                    additional_queries = []
                    for suggestion in state.review.improvement_suggestions:
                        if suggestion.priority == "high":
                            additional_queries.append(suggestion.area)
                    for query in additional_queries[:2]:
                        result = self.searcher.search(query, f"补充搜索: {improvement_focus}")
                        state.search_results.append(result)

                    # 重新分析
                    state.analysis = self.analyst.analyze(state)
            else:
                print(f"\n⚠️ 已达到最大迭代次数，进入撰写阶段...")

        # ======== 阶段5: 撰写报告 ========
        state.current_phase = ResearchPhase.WRITING
        state.add_message("撰写最终报告")
        self._print_phase("✍️ 阶段5: 撰写研究报告")

        review_feedback = self._build_review_feedback(state) if state.review else ""
        state.report = self.writer.write(state, review_feedback)

        # 保存报告
        # state.current_phase = ResearchPhase.COMPLETED
        # output_path = self._save_report(state)
        #
        # print(f"\n{'='*70}")
        # print(f"🎉 深度研究完成!")
        # print(f"   研究主题: {state.topic}")
        # print(f"   研究迭代: {state.iteration}轮")
        # print(f"   最终评分: {state.review.overall_score}/100" if state.review else "   评分: N/A")
        # print(f"   报告长度: {len(state.report)}字符")
        # print(f"   报告已保存: {output_path}")
        # print(f"{'='*70}\n")
        #
        # return state.report

        # ======== 阶段6: 翻译成中文 ========
        state.current_phase = ResearchPhase.COMPLETED
        state.add_message("翻译成中文")
        self._print_phase("🌐 阶段6: 翻译成中文")

        state.report_zh = self.translator.translate(state.report, state.topic)

        # 保存报告
        output_paths = self._save_report(state)

        print(f"\n{'=' * 70}")
        print(f"🎉 深度研究完成!")
        print(f"   研究主题: {state.topic}")
        print(f"   研究迭代: {state.iteration}轮")
        print(f"   最终评分: {state.review.overall_score}/100" if state.review else "   评分: N/A")
        print(f"   英文报告长度: {len(state.report)}字符")
        print(f"   中文报告长度: {len(state.report_zh)}字符")
        print(f"   报告已保存:")
        for lang, path in output_paths.items():
            print(f"     [{lang}] {path}")
        print(f"{'=' * 70}\n")

        return state.report_zh

    def _build_review_feedback(self, state: ResearchState) -> str:
        """构建评审反馈文本"""
        if not state.review:
            return ""

        feedback_parts = [f"评审评分: {state.review.overall_score}/100"]
        if state.review.weaknesses:
            feedback_parts.append(f"不足之处: {'; '.join(state.review.weaknesses)}")
        if state.review.improvement_suggestions:
            suggestions = [f"{s.area}: {s.suggestion}" for s in state.review.improvement_suggestions]
            feedback_parts.append(f"改进建议: {'; '.join(suggestions)}")
        if state.review.revision_focus:
            feedback_parts.append(f"重点修订方向: {', '.join(state.review.revision_focus)}")
        return "\n".join(feedback_parts)

    def _save_report(self, state: ResearchState) -> str:
        """保存研究报告到文件"""
        # 生成文件名
        safe_topic = "".join(c for c in state.topic if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_topic = safe_topic.replace(' ', '_')[:50]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"research_{safe_topic}_{timestamp}.md"
        filepath = self.output_dir / filename

        # 写入报告内容
        report_header = f"""---
# 深度研究报告

> **研究主题:** {state.topic}
> **生成时间:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
> **研究迭代:** {state.iteration}轮
> **最终评分:** {state.review.overall_score}/100 (如适用)

---

"""
        full_report = report_header + state.report

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(full_report)

        return str(filepath)

    @staticmethod
    def _print_phase(phase_name: str):
        """打印研究阶段标题"""
        print(f"\n{'─'*50}")
        print(f"  {phase_name}")
        print(f"{'─'*50}")