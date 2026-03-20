#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QSM Agent Harness - 自我进化框架
基于MiniMax M2.7思路构建

三模块：
1. 短时记忆 - 记录每次迭代状态
2. 自反馈 - 分析结果提供优化方向
3. 自优化 - 基于历史记忆改进

迭代循环：
分析失败 → 规划改动 → 执行 → 评测 → 对比 → 保留/回退
"""

import json
import time
from datetime import datetime
from pathlib import Path


class ShortTermMemory:
    """短时记忆模块"""
    
    def __init__(self, memory_dir: str = "/tmp/qsm_memory"):
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.current_session = None
        
    def create_session(self, task_name: str) -> str:
        """创建新的迭代会话"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_id = f"{task_name}_{timestamp}"
        self.current_session = session_id
        
        memory = {
            "session_id": session_id,
            "task_name": task_name,
            "created_at": datetime.now().isoformat(),
            "iterations": [],
            "current_state": "initialized"
        }
        
        self._save_memory(memory)
        return session_id
    
    def record_iteration(self, iteration_data: dict):
        """记录一次迭代"""
        memory = self._load_memory()
        
        iteration = {
            "timestamp": datetime.now().isoformat(),
            "iteration_num": len(memory["iterations"]) + 1,
            **iteration_data
        }
        
        memory["iterations"].append(iteration)
        memory["current_state"] = iteration_data.get("state", "running")
        
        self._save_memory(memory)
        return iteration
    
    def get_all_iterations(self) -> list:
        """获取所有历史迭代"""
        memory = self._load_memory()
        return memory.get("iterations", [])
    
    def _save_memory(self, memory: dict):
        """保存记忆文件"""
        if self.current_session:
            file_path = self.memory_dir / f"{self.current_session}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(memory, f, ensure_ascii=False, indent=2)
    
    def _load_memory(self) -> dict:
        """加载记忆文件"""
        if self.current_session:
            file_path = self.memory_dir / f"{self.current_session}.json"
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        return {"iterations": []}


class SelfFeedback:
    """自反馈模块"""
    
    def analyze_result(self, result: dict, history: list) -> dict:
        """分析结果并生成反馈"""
        feedback = {
            "success": result.get("success", False),
            "score": result.get("score", 0),
            "issues": [],
            "optimization_hints": []
        }
        
        # 分析失败原因
        if not result.get("success"):
            feedback["issues"].append({
                "type": "execution_error",
                "description": result.get("error", "Unknown error"),
                "suggestion": "检查输入参数和执行环境"
            })
        
        # 分析分数变化
        if history:
            prev_score = history[-1].get("score", 0)
            score_diff = result.get("score", 0) - prev_score
            
            if score_diff > 0:
                feedback["optimization_hints"].append({
                    "type": "positive",
                    "message": f"分数提升 {score_diff:.2f}，当前改动有效"
                })
            elif score_diff < 0:
                feedback["optimization_hints"].append({
                    "type": "negative",
                    "message": f"分数下降 {-score_diff:.2f}，建议回退"
                })
        
        # 生成下一步建议
        feedback["next_steps"] = self._generate_next_steps(feedback, result)
        
        return feedback
    
    def _generate_next_steps(self, feedback: dict, result: dict) -> list:
        """生成下一步行动建议"""
        steps = []
        
        if feedback["success"]:
            steps.append("保持当前改动，尝试进一步优化")
            steps.append("记录成功参数组合，用于后续实验")
        else:
            steps.append("分析失败原因，调整参数")
            steps.append("回退到上一个稳定版本")
            steps.append("尝试替代方案")
        
        return steps


class SelfOptimization:
    """自优化模块"""
    
    def __init__(self):
        self.optimization_history = []
    
    def optimize(self, current_state: dict, feedback: dict, history: list) -> dict:
        """基于反馈和历史进行优化"""
        optimization = {
            "action": "continue",
            "changes": [],
            "reason": ""
        }
        
        # 决策逻辑
        if feedback["success"]:
            # 成功：继续优化或保持
            if self._should_continue_optimizing(history):
                optimization["action"] = "optimize"
                optimization["changes"] = self._propose_improvements(current_state, history)
                optimization["reason"] = "继续改进以获得更好性能"
            else:
                optimization["action"] = "keep"
                optimization["reason"] = "已达到较好状态，保持当前配置"
        else:
            # 失败：回退或调整
            optimization["action"] = "rollback"
            optimization["reason"] = "执行失败，回退到上一版本"
        
        self.optimization_history.append(optimization)
        return optimization
    
    def _should_continue_optimizing(self, history: list) -> bool:
        """判断是否应该继续优化"""
        if len(history) < 3:
            return True
        
        # 检查最近几次改进是否还有提升空间
        recent_scores = [h.get("score", 0) for h in history[-3:]]
        return max(recent_scores) - min(recent_scores) > 0.01
    
    def _propose_improvements(self, current: dict, history: list) -> list:
        """提出改进建议"""
        return [
            "微调参数范围",
            "尝试不同的量子门序列",
            "优化测量顺序"
        ]


class AgentHarness:
    """Agent Harness - 完整的自我进化框架"""
    
    def __init__(self):
        self.memory = ShortTermMemory()
        self.feedback = SelfFeedback()
        self.optimizer = SelfOptimization()
        self.iteration_count = 0
        self.max_iterations = 100
    
    def run_evolution_loop(self, task_name: str, initial_state: dict, 
                          execute_fn, evaluate_fn, max_iterations: int = 100):
        """
        运行自我进化循环
        
        参数:
            task_name: 任务名称
            initial_state: 初始状态
            execute_fn: 执行函数
            evaluate_fn: 评测函数
            max_iterations: 最大迭代次数
        """
        # 创建会话
        session_id = self.memory.create_session(task_name)
        current_state = initial_state.copy()
        
        print(f"🚀 开始自我进化循环: {session_id}")
        print(f"最大迭代次数: {max_iterations}")
        
        for i in range(max_iterations):
            self.iteration_count = i + 1
            print(f"\n=== 迭代 {self.iteration_count} ===")
            
            # 1. 执行
            print("执行中...")
            result = execute_fn(current_state)
            
            # 2. 评测
            print("评测中...")
            eval_result = evaluate_fn(result)
            
            # 3. 记录迭代
            iteration_data = {
                "state": current_state,
                "result": result,
                "evaluation": eval_result,
                "success": eval_result.get("success", False),
                "score": eval_result.get("score", 0)
            }
            self.memory.record_iteration(iteration_data)
            
            # 4. 自反馈
            print("分析反馈...")
            feedback = self.feedback.analyze_result(
                eval_result, 
                self.memory.get_all_iterations()
            )
            
            # 5. 自优化
            print("优化决策...")
            optimization = self.optimizer.optimize(
                current_state,
                feedback,
                self.memory.get_all_iterations()
            )
            
            # 6. 应用优化决策
            if optimization["action"] == "rollback":
                print("⬅️ 回退到上一版本")
                if self.iteration_count > 1:
                    # 回退到上一个成功版本
                    history = self.memory.get_all_iterations()
                    if history:
                        current_state = history[-1]["state"]
            elif optimization["action"] == "optimize":
                print("➡️ 应用优化改进")
                # 应用改进建议
                for change in optimization.get("changes", []):
                    print(f"  改进: {change}")
            elif optimization["action"] == "keep":
                print("✅ 保持当前状态")
                break
            
            # 打印进度
            print(f"分数: {eval_result.get('score', 0):.4f}")
            print(f"状态: {feedback.get('success', False) and '成功' or '失败'}")
            
            # 检查是否达到目标
            if eval_result.get("score", 0) >= 0.95:
                print("\n🎉 达到目标！")
                break
        
        print(f"\n=== 自我进化完成 ===")
        print(f"总迭代次数: {self.iteration_count}")
        
        # 返回最终状态
        history = self.memory.get_all_iterations()
        if history:
            best_iteration = max(history, key=lambda x: x.get("score", 0))
            return {
                "success": True,
                "best_score": best_iteration.get("score", 0),
                "iterations": self.iteration_count,
                "best_state": best_iteration.get("state")
            }
        
        return {"success": False}


# 测试示例
if __name__ == "__main__":
    # 创建Agent Harness
    harness = AgentHarness()
    
    # 定义执行函数
    def test_execute(state):
        """测试执行函数"""
        return {"output": f"执行结果_{state.get('param', 0)}"}
    
    # 定义评测函数
    def test_evaluate(result):
        """测试评测函数"""
        import random
        score = random.random()  # 模拟分数
        return {
            "success": score > 0.3,
            "score": score,
            "metrics": {"accuracy": score}
        }
    
    # 运行进化循环
    initial_state = {"param": 1}
    result = harness.run_evolution_loop(
        task_name="test_evolution",
        initial_state=initial_state,
        execute_fn=test_execute,
        evaluate_fn=test_evaluate,
        max_iterations=10
    )
    
    print(f"\n最终结果: {result}")
