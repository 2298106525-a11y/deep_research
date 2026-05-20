"""
多Agent深度研究智能体 - 主入口

使用方式:
    python run.py                          # 交互式输入研究主题
    python run.py "你的研究主题"             # 直接传入研究主题
    python run.py --topic "你的研究主题"     # 使用命名参数
"""

import sys
import argparse

# 确保当前目录在sys.path中（解决模块导入问题）
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from coordinator import DeepResearchCoordinator
from config import config


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="多Agent深度研究智能体 - 使用多个AI Agent协作完成深度研究"
    )
    parser.add_argument(
        "topic",
        nargs="?",
        default=None,
        help="研究主题 (也可交互式输入)"
    )
    parser.add_argument(
        "--topic", "-t",
        dest="topic_flag",
        default=None,
        help="研究主题 (命名参数方式)"
    )
    parser.add_argument(
        "--max-iterations", "-n",
        type=int,
        default=None,
        help=f"最大迭代次数 (默认: {config.MAX_ITERATIONS})"
    )
    parser.add_argument(
        "--min-score", "-s",
        type=int,
        default=None,
        help=f"质量分数阈值 (默认: {config.MIN_QUALITY_SCORE})"
    )
    return parser.parse_args()


def interactive_mode():
    """交互式模式"""
    print("\n" + "="*60)
    print("  🔬 多Agent深度研究智能体")
    print("="*60)
    print("  系统将自动执行以下流程:")
    print("    1. 📋 规划 - 分解研究问题为子任务")
    print("    2. 🔍 搜索 - 收集相关信息和数据")
    print("    3. 📊 分析 - 深度分析和综合信息")
    print("    4. 🔎 评审 - 评估研究质量和完整性")
    print("    5. ✍️  撰写 - 生成研究报告")
    print("="*60)
    print()

    while True:
        try:
            topic = input("请输入研究主题 (输入 'quit' 退出): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n👋 再见!")
            break

        if not topic:
            print("⚠️ 主题不能为空，请重新输入。")
            continue

        if topic.lower() in ('quit', 'exit', 'q'):
            print("\n👋 再见!")
            break

        try:
            coordinator = DeepResearchCoordinator()
            report = coordinator.run(topic)
            print("\n" + "="*60)
            print("📄 研究报告预览 (前500字符):")
            print("="*60)
            print(report[:500] + "..." if len(report) > 500 else report)
            print("="*60)
        except Exception as e:
            print(f"\n❌ 研究过程出错: {e}")
            import traceback
            traceback.print_exc()

        print()


def single_run(topic: str):
    """单次运行模式"""
    try:
        coordinator = DeepResearchCoordinator()
        report = coordinator.run(topic)
        return report
    except Exception as e:
        print(f"\n❌ 研究过程出错: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """主函数"""
    args = parse_args()

    # 更新配置
    if args.max_iterations:
        config.MAX_ITERATIONS = args.max_iterations
    if args.min_score:
        config.MIN_QUALITY_SCORE = args.min_score

    # 确定研究主题
    topic = args.topic_flag or args.topic

    if topic:
        # 单次运行模式
        single_run(topic)
    else:
        # 交互式模式
        interactive_mode()


if __name__ == "__main__":
    main()