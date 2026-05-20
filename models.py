"""
多Agent深度研究智能体 - 数据模型模块
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


class ResearchPhase(str, Enum):
    """研究阶段枚举"""
    INIT = "init"                      # 初始化
    PLANNING = "planning"              # 规划阶段
    SEARCHING = "searching"            # 搜索阶段
    ANALYZING = "analyzing"            # 分析阶段
    REVIEWING = "reviewing"            # 评审阶段
    WRITING = "writing"                # 撰写阶段
    REFINING = "refining"              # 优化阶段
    COMPLETED = "completed"            # 完成


class ReviewVerdict(str, Enum):
    """评审结论枚举"""
    PASS = "pass"                      # 通过
    REVISE = "revise"                  # 需修订
    REJECT = "reject"                  # 驳回


@dataclass
class SubTask:
    """研究子任务"""
    id: int
    title: str
    description: str
    search_queries: List[str] = field(default_factory=list)
    priority: str = "medium"
    dependencies: List[int] = field(default_factory=list)
    status: str = "pending"  # pending / in_progress / completed
    results: Optional[str] = None


@dataclass
class ResearchPlan:
    """研究计划"""
    research_topic: str
    research_objective: str
    subtasks: List[SubTask] = field(default_factory=list)
    estimated_depth: str = ""
    key_questions: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ResearchPlan":
        """从字典创建研究计划"""
        subtasks = []
        for st in data.get("subtasks", []):
            subtasks.append(SubTask(
                id=st.get("id", 0),
                title=st.get("title", ""),
                description=st.get("description", ""),
                search_queries=st.get("search_queries", []),
                priority=st.get("priority", "medium"),
                dependencies=st.get("dependencies", [])
            ))
        return cls(
            research_topic=data.get("research_topic", ""),
            research_objective=data.get("research_objective", ""),
            subtasks=subtasks,
            estimated_depth=data.get("estimated_depth", ""),
            key_questions=data.get("key_questions", [])
        )


@dataclass
class SearchResult:
    """单条搜索结果"""
    title: str
    url: str
    snippet: str
    relevance_score: float = 0.0
    source_type: str = "unknown"


@dataclass
class SearchResults:
    """搜索Agent的输出"""
    search_query: str
    results: List[SearchResult] = field(default_factory=list)
    key_findings: List[str] = field(default_factory=list)
    information_gaps: List[str] = field(default_factory=list)


@dataclass
class KeyInsight:
    """关键洞察"""
    insight: str
    evidence: List[str] = field(default_factory=list)
    confidence: float = 0.0


@dataclass
class AnalysisResult:
    """分析师Agent的输出"""
    analysis_summary: str = ""
    key_insights: List[KeyInsight] = field(default_factory=list)
    patterns_identified: List[str] = field(default_factory=list)
    contradictions: List[str] = field(default_factory=list)
    information_gaps: List[str] = field(default_factory=list)
    preliminary_conclusions: List[str] = field(default_factory=list)


@dataclass
class ImprovementSuggestion:
    """改进建议"""
    area: str
    suggestion: str
    priority: str = "medium"


@dataclass
class ReviewResult:
    """评审Agent的输出"""
    overall_score: int = 0
    dimension_scores: Dict[str, int] = field(default_factory=dict)
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    improvement_suggestions: List[ImprovementSuggestion] = field(default_factory=list)
    verdict: str = "revise"
    revision_focus: List[str] = field(default_factory=list)

    @property
    def is_pass(self) -> bool:
        return self.verdict == ReviewVerdict.PASS.value

    @property
    def needs_revision(self) -> bool:
        return self.verdict == ReviewVerdict.REVISE.value


@dataclass
class ResearchState:
    """研究状态 - 在各Agent之间传递的上下文"""
    topic: str
    plan: Optional[ResearchPlan] = None
    search_results: List[SearchResults] = field(default_factory=list)
    analysis: Optional[AnalysisResult] = None
    review: Optional[ReviewResult] = None
    report: str = ""
    current_phase: ResearchPhase = ResearchPhase.INIT
    iteration: int = 0
    max_iterations: int = 3
    messages: List[str] = field(default_factory=list)

    def add_message(self, msg: str):
        """添加日志消息"""
        self.messages.append(f"[{self.current_phase.value}] {msg}")