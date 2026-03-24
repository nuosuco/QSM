#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
量子资源管理器 - 量子计算资源管理
"""

import os
import math
from datetime import datetime
from collections import defaultdict

class QuantumResourceManager:
    """量子资源管理器"""

    def __init__(self):
        self.allocated_qubits = 0
        self.max_qubits = 64
        self.memory_limit = 4 * 1024 * 1024 * 1024  # 4GB
        self.allocations = {}
        self.usage_history = []
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 量子资源管理器初始化")

    def allocate_qubits(self, count, task_id=None):
        """分配量子比特"""
        if self.allocated_qubits + count > self.max_qubits:
            return {
                'success': False,
                'error': f'Not enough qubits. Requested: {count}, Available: {self.max_qubits - self.allocated_qubits}'
            }

        allocation_id = task_id or f'alloc_{len(self.allocations)}'
        self.allocations[allocation_id] = {
            'qubits': count,
            'allocated_at': datetime.now().isoformat()
        }
        self.allocated_qubits += count

        self._record_usage()

        return {
            'success': True,
            'allocation_id': allocation_id,
            'qubits_allocated': count,
            'remaining': self.max_qubits - self.allocated_qubits
        }

    def deallocate_qubits(self, allocation_id):
        """释放量子比特"""
        if allocation_id not in self.allocations:
            return {'success': False, 'error': 'Allocation not found'}

        allocation = self.allocations[allocation_id]
        self.allocated_qubits -= allocation['qubits']
        del self.allocations[allocation_id]

        self._record_usage()

        return {
            'success': True,
            'freed_qubits': allocation['qubits'],
            'remaining_allocated': self.allocated_qubits
        }

    def _record_usage(self):
        """记录使用情况"""
        self.usage_history.append({
            'timestamp': datetime.now().isoformat(),
            'allocated_qubits': self.allocated_qubits,
            'active_allocations': len(self.allocations)
        })

    def estimate_memory(self, num_qubits):
        """估算内存需求"""
        # 量子态需要2^n个复数
        num_states = 2 ** num_qubits
        bytes_per_complex = 16  # 2个双精度浮点数
        total_bytes = num_states * bytes_per_complex
        total_mb = total_bytes / (1024 * 1024)

        return {
            'num_qubits': num_qubits,
            'num_states': num_states,
            'memory_bytes': total_bytes,
            'memory_mb': round(total_mb, 2),
            'memory_gb': round(total_mb / 1024, 4),
            'feasible': total_bytes < self.memory_limit
        }

    def get_available_resources(self):
        """获取可用资源"""
        import psutil

        try:
            mem = psutil.virtual_memory()
            system_memory_gb = mem.total / (1024**3)
            available_memory_gb = mem.available / (1024**3)
        except:
            system_memory_gb = 8
            available_memory_gb = 6

        return {
            'qubits': {
                'max': self.max_qubits,
                'allocated': self.allocated_qubits,
                'available': self.max_qubits - self.allocated_qubits
            },
            'memory': {
                'limit_gb': self.memory_limit / (1024**3),
                'system_total_gb': round(system_memory_gb, 2),
                'system_available_gb': round(available_memory_gb, 2)
            },
            'active_allocations': len(self.allocations)
        }

    def can_execute(self, num_qubits, num_gates):
        """检查是否可以执行"""
        # 检查量子比特
        if num_qubits > self.max_qubits - self.allocated_qubits:
            return {
                'can_execute': False,
                'reason': f'Not enough qubits. Need {num_qubits}, have {self.max_qubits - self.allocated_qubits}'
            }

        # 检查内存
        mem_estimate = self.estimate_memory(num_qubits)
        if not mem_estimate['feasible']:
            return {
                'can_execute': False,
                'reason': f'Memory insufficient. Need {mem_estimate["memory_mb"]} MB'
            }

        return {
            'can_execute': True,
            'estimated_memory_mb': mem_estimate['memory_mb'],
            'estimated_gates': num_gates
        }

    def get_usage_statistics(self):
        """获取使用统计"""
        if not self.usage_history:
            return {'error': 'No usage history'}

        qubits_used = [u['allocated_qubits'] for u in self.usage_history]

        return {
            'total_records': len(self.usage_history),
            'current_allocated': self.allocated_qubits,
            'max_allocated': max(qubits_used) if qubits_used else 0,
            'avg_allocated': round(sum(qubits_used) / len(qubits_used), 2) if qubits_used else 0,
            'active_allocations': len(self.allocations)
        }

    def optimize_allocation(self, tasks):
        """优化任务分配"""
        # 按所需量子比特数排序
        sorted_tasks = sorted(tasks, key=lambda x: x.get('qubits', 0))

        allocation_plan = []
        current_used = 0

        for task in sorted_tasks:
            needed = task.get('qubits', 0)
            if current_used + needed <= self.max_qubits:
                allocation_plan.append({
                    'task_id': task.get('id'),
                    'qubits': needed,
                    'can_execute': True
                })
                current_used += needed
            else:
                allocation_plan.append({
                    'task_id': task.get('id'),
                    'qubits': needed,
                    'can_execute': False,
                    'reason': 'Not enough resources'
                })

        return {
            'total_tasks': len(tasks),
            'executable': len([t for t in allocation_plan if t['can_execute']]),
            'plan': allocation_plan,
            'total_qubits_used': current_used
        }

def main():
    print("=" * 60)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 量子资源管理器测试")
    print("=" * 60)

    manager = QuantumResourceManager()

    # 分配量子比特
    print("\n分配量子比特:")
    result = manager.allocate_qubits(4, 'task_001')
    print(f"  任务1分配4量子比特: {result['success']}")
    print(f"  剩余: {result['remaining']}")

    result = manager.allocate_qubits(8, 'task_002')
    print(f"  任务2分配8量子比特: {result['success']}")
    print(f"  剩余: {result['remaining']}")

    # 估算内存
    print("\n内存估算:")
    mem = manager.estimate_memory(10)
    print(f"  10量子比特需要: {mem['memory_mb']} MB")

    mem = manager.estimate_memory(20)
    print(f"  20量子比特需要: {mem['memory_mb']} MB")

    # 可用资源
    print("\n可用资源:")
    resources = manager.get_available_resources()
    print(f"  量子比特: {resources['qubits']['available']}/{resources['qubits']['max']}")

    # 释放资源
    print("\n释放资源:")
    result = manager.deallocate_qubits('task_001')
    print(f"  释放任务1: {result['success']}")
    print(f"  剩余分配: {result['remaining_allocated']}")

    # 使用统计
    print("\n使用统计:")
    stats = manager.get_usage_statistics()
    print(f"  当前分配: {stats['current_allocated']}")
    print(f"  最大分配: {stats['max_allocated']}")

    print("\n" + "=" * 60)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 测试完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
