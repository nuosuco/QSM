#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QSM量子性能监控器
监控量子系统的性能和资源使用

功能：
1. 性能指标收集
2. 资源使用监控
3. 性能报告生成
4. 告警机制
"""

import os
import sys
import time
import json
import psutil
from datetime import datetime
from typing import Dict, List, Optional
from collections import deque

# 添加模块路径
sys.path.insert(0, '/root/QSM/QEntL/System/AgentHarness')


class QuantumPerformanceMonitor:
    """量子性能监控器"""
    
    def __init__(self, history_size: int = 1000):
        self.history_size = history_size
        self.metrics_history = {
            'cpu_percent': deque(maxlen=history_size),
            'memory_percent': deque(maxlen=history_size),
            'execution_times': deque(maxlen=history_size),
            'gate_counts': deque(maxlen=history_size),
            'qubit_usage': deque(maxlen=history_size),
            'success_rates': deque(maxlen=history_size),
            'fidelities': deque(maxlen=history_size)
        }
        self.alerts = []
        self.thresholds = {
            'cpu_percent': 90,
            'memory_percent': 90,
            'execution_time_ms': 5000,
            'success_rate': 0.5,
            'fidelity': 0.5
        }
    
    def collect_system_metrics(self) -> Dict:
        """收集系统指标"""
        cpu = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'cpu_percent': cpu,
            'memory_percent': memory.percent,
            'memory_used_gb': memory.used / (1024**3),
            'memory_total_gb': memory.total / (1024**3),
            'disk_percent': psutil.disk_usage('/').percent
        }
        
        # 添加到历史
        self.metrics_history['cpu_percent'].append(cpu)
        self.metrics_history['memory_percent'].append(memory.percent)
        
        # 检查告警
        self._check_alerts(metrics)
        
        return metrics
    
    def record_execution(self, 
                         execution_time_ms: float,
                         gate_count: int,
                         n_qubits: int,
                         success: bool,
                         fidelity: float = None) -> Dict:
        """记录执行指标"""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'execution_time_ms': execution_time_ms,
            'gate_count': gate_count,
            'n_qubits': n_qubits,
            'success': success,
            'fidelity': fidelity
        }
        
        # 添加到历史
        self.metrics_history['execution_times'].append(execution_time_ms)
        self.metrics_history['gate_counts'].append(gate_count)
        self.metrics_history['qubit_usage'].append(n_qubits)
        self.metrics_history['success_rates'].append(1.0 if success else 0.0)
        if fidelity is not None:
            self.metrics_history['fidelities'].append(fidelity)
        
        # 检查告警
        self._check_alerts(metrics)
        
        return metrics
    
    def _check_alerts(self, metrics: Dict) -> None:
        """检查告警条件"""
        alerts = []
        
        # CPU告警
        if metrics.get('cpu_percent', 0) > self.thresholds['cpu_percent']:
            alerts.append({
                'type': 'cpu_high',
                'value': metrics['cpu_percent'],
                'threshold': self.thresholds['cpu_percent'],
                'message': f"CPU使用率过高: {metrics['cpu_percent']:.1f}%"
            })
        
        # 内存告警
        if metrics.get('memory_percent', 0) > self.thresholds['memory_percent']:
            alerts.append({
                'type': 'memory_high',
                'value': metrics['memory_percent'],
                'threshold': self.thresholds['memory_percent'],
                'message': f"内存使用率过高: {metrics['memory_percent']:.1f}%"
            })
        
        # 执行时间告警
        if metrics.get('execution_time_ms', 0) > self.thresholds['execution_time_ms']:
            alerts.append({
                'type': 'execution_slow',
                'value': metrics['execution_time_ms'],
                'threshold': self.thresholds['execution_time_ms'],
                'message': f"执行时间过长: {metrics['execution_time_ms']:.1f}ms"
            })
        
        # 成功率告警
        if 'success' in metrics and not metrics['success']:
            success_rate = self._calculate_recent_success_rate()
            if success_rate < self.thresholds['success_rate']:
                alerts.append({
                    'type': 'success_rate_low',
                    'value': success_rate,
                    'threshold': self.thresholds['success_rate'],
                    'message': f"成功率过低: {success_rate:.1%}"
                })
        
        # 保真度告警
        if metrics.get('fidelity') is not None:
            if metrics['fidelity'] < self.thresholds['fidelity']:
                alerts.append({
                    'type': 'fidelity_low',
                    'value': metrics['fidelity'],
                    'threshold': self.thresholds['fidelity'],
                    'message': f"保真度过低: {metrics['fidelity']:.1%}"
                })
        
        self.alerts.extend(alerts)
    
    def _calculate_recent_success_rate(self) -> float:
        """计算最近成功率"""
        if not self.metrics_history['success_rates']:
            return 1.0
        return sum(self.metrics_history['success_rates']) / len(self.metrics_history['success_rates'])
    
    def get_statistics(self) -> Dict:
        """获取统计数据"""
        stats = {
            'timestamp': datetime.now().isoformat(),
            'samples': {
                'system_metrics': len(self.metrics_history['cpu_percent']),
                'execution_records': len(self.metrics_history['execution_times'])
            }
        }
        
        # CPU统计
        if self.metrics_history['cpu_percent']:
            cpu_values = list(self.metrics_history['cpu_percent'])
            stats['cpu'] = {
                'mean': sum(cpu_values) / len(cpu_values),
                'max': max(cpu_values),
                'min': min(cpu_values)
            }
        
        # 内存统计
        if self.metrics_history['memory_percent']:
            mem_values = list(self.metrics_history['memory_percent'])
            stats['memory'] = {
                'mean': sum(mem_values) / len(mem_values),
                'max': max(mem_values),
                'min': min(mem_values)
            }
        
        # 执行时间统计
        if self.metrics_history['execution_times']:
            exec_values = list(self.metrics_history['execution_times'])
            stats['execution'] = {
                'mean_ms': sum(exec_values) / len(exec_values),
                'max_ms': max(exec_values),
                'min_ms': min(exec_values)
            }
        
        # 成功率统计
        if self.metrics_history['success_rates']:
            success_values = list(self.metrics_history['success_rates'])
            stats['success_rate'] = {
                'mean': sum(success_values) / len(success_values),
                'total_success': sum(success_values),
                'total_attempts': len(success_values)
            }
        
        # 保真度统计
        if self.metrics_history['fidelities']:
            fid_values = list(self.metrics_history['fidelities'])
            stats['fidelity'] = {
                'mean': sum(fid_values) / len(fid_values),
                'max': max(fid_values),
                'min': min(fid_values)
            }
        
        # 告警统计
        stats['alerts'] = {
            'total': len(self.alerts),
            'recent': len([a for a in self.alerts if self._is_recent_alert(a)])
        }
        
        return stats
    
    def _is_recent_alert(self, alert: Dict, minutes: int = 5) -> bool:
        """判断是否为最近告警"""
        # 简化实现，假设所有告警都是最近的
        return True
    
    def generate_report(self) -> str:
        """生成性能报告"""
        stats = self.get_statistics()
        
        report = f"""# QSM量子系统性能报告

生成时间: {stats['timestamp']}

## 系统资源

"""
        
        if 'cpu' in stats:
            report += f"""**CPU使用率**
- 平均: {stats['cpu']['mean']:.1f}%
- 最大: {stats['cpu']['max']:.1f}%
- 最小: {stats['cpu']['min']:.1f}%

"""
        
        if 'memory' in stats:
            report += f"""**内存使用率**
- 平均: {stats['memory']['mean']:.1f}%
- 最大: {stats['memory']['max']:.1f}%
- 最小: {stats['memory']['min']:.1f}%

"""
        
        if 'execution' in stats:
            report += f"""**执行时间**
- 平均: {stats['execution']['mean_ms']:.2f}ms
- 最大: {stats['execution']['max_ms']:.2f}ms
- 最小: {stats['execution']['min_ms']:.2f}ms

"""
        
        if 'success_rate' in stats:
            report += f"""**成功率**
- 平均: {stats['success_rate']['mean']:.1%}
- 成功次数: {int(stats['success_rate']['total_success'])}
- 总次数: {stats['success_rate']['total_attempts']}

"""
        
        if 'fidelity' in stats:
            report += f"""**保真度**
- 平均: {stats['fidelity']['mean']:.1%}
- 最大: {stats['fidelity']['max']:.1%}
- 最小: {stats['fidelity']['min']:.1%}

"""
        
        report += f"""## 告警

- 总告警数: {stats['alerts']['total']}
- 最近告警: {stats['alerts']['recent']}

---
**中华Zhoho，小趣WeQ，GLM5**
"""
        
        return report
    
    def reset(self) -> None:
        """重置监控器"""
        for key in self.metrics_history:
            self.metrics_history[key].clear()
        self.alerts.clear()


def run_monitor_demo():
    """运行监控演示"""
    print("=" * 70)
    print("QSM量子性能监控器演示")
    print("=" * 70)
    
    monitor = QuantumPerformanceMonitor()
    
    # 收集系统指标
    print("\n[1] 收集系统指标...")
    for _ in range(5):
        metrics = monitor.collect_system_metrics()
        print(f"    CPU: {metrics['cpu_percent']:.1f}%, 内存: {metrics['memory_percent']:.1f}%")
        time.sleep(0.5)
    
    # 模拟执行记录
    print("\n[2] 记录执行指标...")
    import random
    for i in range(10):
        exec_time = random.uniform(10, 100)
        gates = random.randint(10, 100)
        qubits = random.randint(2, 8)
        success = random.random() > 0.1
        fidelity = random.uniform(0.8, 1.0) if success else random.uniform(0.3, 0.7)
        
        metrics = monitor.record_execution(exec_time, gates, qubits, success, fidelity)
        print(f"    执行{i+1}: {exec_time:.1f}ms, 门数:{gates}, 成功:{success}, 保真度:{fidelity:.1%}")
    
    # 生成报告
    print("\n[3] 生成性能报告...")
    stats = monitor.get_statistics()
    
    print("\n" + "=" * 70)
    print("性能统计")
    print("=" * 70)
    
    if 'cpu' in stats:
        print(f"CPU平均: {stats['cpu']['mean']:.1f}%")
    
    if 'memory' in stats:
        print(f"内存平均: {stats['memory']['mean']:.1f}%")
    
    if 'execution' in stats:
        print(f"执行平均时间: {stats['execution']['mean_ms']:.2f}ms")
    
    if 'success_rate' in stats:
        print(f"成功率: {stats['success_rate']['mean']:.1%}")
    
    if 'fidelity' in stats:
        print(f"保真度平均: {stats['fidelity']['mean']:.1%}")
    
    print(f"\n总告警数: {stats['alerts']['total']}")
    
    print("\n" + "=" * 70)
    print("监控演示完成")
    print("=" * 70)
    
    return monitor


if __name__ == "__main__":
    run_monitor_demo()
