#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
量子调度器模块 - 量子任务调度和管理
"""

import time
import queue
import threading
from datetime import datetime
from collections import defaultdict

class QuantumScheduler:
    """量子任务调度器"""

    def __init__(self, max_concurrent=4):
        self.max_concurrent = max_concurrent
        self.task_queue = queue.PriorityQueue()
        self.running_tasks = {}
        self.completed_tasks = []
        self.task_counter = 0
        self.lock = threading.Lock()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 量子调度器初始化 (最大并发: {max_concurrent})")

    def submit_task(self, task_type, task_data, priority=5):
        """
        提交量子任务
        priority: 1-10, 1最高优先级
        """
        with self.lock:
            self.task_counter += 1
            task_id = f"qtask_{self.task_counter:06d}"

            task = {
                'task_id': task_id,
                'task_type': task_type,
                'task_data': task_data,
                'priority': priority,
                'status': 'queued',
                'submitted_at': datetime.now().isoformat()
            }

            self.task_queue.put((priority, task_id, task))
            return task_id

    def get_next_task(self):
        """获取下一个待执行任务"""
        if self.task_queue.empty():
            return None

        priority, task_id, task = self.task_queue.get()
        return task

    def start_task(self, task):
        """开始执行任务"""
        with self.lock:
            task['status'] = 'running'
            task['started_at'] = datetime.now().isoformat()
            self.running_tasks[task['task_id']] = task

        # 模拟任务执行
        result = self._execute_task(task)

        with self.lock:
            task['status'] = 'completed'
            task['completed_at'] = datetime.now().isoformat()
            task['result'] = result

            if task['task_id'] in self.running_tasks:
                del self.running_tasks[task['task_id']]

            self.completed_tasks.append(task)

        return result

    def _execute_task(self, task):
        """执行量子任务"""
        task_type = task['task_type']
        task_data = task['task_data']

        if task_type == 'bell_state':
            return self._create_bell_state()
        elif task_type == 'ghz_state':
            return self._create_ghz_state(task_data.get('num_qubits', 3))
        elif task_type == 'quantum_fourier':
            return self._quantum_fourier_transform(task_data.get('num_qubits', 4))
        elif task_type == 'grover_search':
            return self._grover_search(task_data.get('items', 8))
        else:
            return {'status': 'unknown_task_type'}

    def _create_bell_state(self):
        """创建Bell态"""
        return {
            'type': 'Bell',
            'state': [1, 0, 0, 1],
            'probabilities': [0.5, 0, 0, 0.5],
            'fidelity': 1.0
        }

    def _create_ghz_state(self, num_qubits):
        """创建GHZ态"""
        dim = 2 ** num_qubits
        state = [0] * dim
        state[0] = 1
        state[-1] = 1

        return {
            'type': 'GHZ',
            'num_qubits': num_qubits,
            'state': state,
            'probabilities': [1/dim if i in [0, dim-1] else 0 for i in range(dim)]
        }

    def _quantum_fourier_transform(self, num_qubits):
        """量子傅里叶变换"""
        return {
            'type': 'QFT',
            'num_qubits': num_qubits,
            'gates_required': num_qubits * (num_qubits + 1) // 2,
            'description': f'{num_qubits}量子比特量子傅里叶变换'
        }

    def _grover_search(self, items):
        """Grover搜索"""
        iterations = int((items) ** 0.5)
        return {
            'type': 'Grover',
            'items': items,
            'iterations': iterations,
            'success_probability': 1 - (1/2**(items//2)),
            'speedup': 'quadratic'
        }

    def get_queue_status(self):
        """获取队列状态"""
        return {
            'queued': self.task_queue.qsize(),
            'running': len(self.running_tasks),
            'completed': len(self.completed_tasks),
            'max_concurrent': self.max_concurrent
        }

    def cancel_task(self, task_id):
        """取消任务"""
        with self.lock:
            if task_id in self.running_tasks:
                return {'error': 'Task already running'}
            return {'cancelled': task_id}

    def get_task_result(self, task_id):
        """获取任务结果"""
        for task in self.completed_tasks:
            if task['task_id'] == task_id:
                return task
        return {'error': 'Task not found'}

    def run_scheduler(self, num_tasks=5):
        """运行调度器处理任务"""
        results = []

        while len(results) < num_tasks:
            task = self.get_next_task()
            if task is None:
                break

            result = self.start_task(task)
            results.append(result)

        return results

def main():
    print("=" * 60)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 量子调度器模块测试")
    print("=" * 60)

    scheduler = QuantumScheduler(max_concurrent=4)

    # 提交各种量子任务
    print("\n提交量子任务:")
    task1 = scheduler.submit_task('bell_state', {}, priority=1)
    print(f"  任务1: {task1} (Bell态, 优先级最高)")

    task2 = scheduler.submit_task('ghz_state', {'num_qubits': 4}, priority=2)
    print(f"  任务2: {task2} (GHZ态, 4量子比特)")

    task3 = scheduler.submit_task('quantum_fourier', {'num_qubits': 3}, priority=3)
    print(f"  任务3: {task3} (QFT)")

    task4 = scheduler.submit_task('grover_search', {'items': 16}, priority=4)
    print(f"  任务4: {task4} (Grover搜索)")

    task5 = scheduler.submit_task('bell_state', {}, priority=5)
    print(f"  任务5: {task5} (Bell态)")

    # 查看队列状态
    print("\n队列状态:")
    status = scheduler.get_queue_status()
    print(f"  排队中: {status['queued']}")
    print(f"  最大并发: {status['max_concurrent']}")

    # 运行调度器
    print("\n执行任务:")
    results = scheduler.run_scheduler(num_tasks=5)

    for i, result in enumerate(results):
        print(f"  任务{i+1}: {result['type']} - 完成")

    # 最终状态
    print("\n最终状态:")
    status = scheduler.get_queue_status()
    print(f"  已完成: {status['completed']}")
    print(f"  排队中: {status['queued']}")

    print("\n" + "=" * 60)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 测试完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
