#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
量子日志系统 - 量子计算日志记录
"""

import os
import json
from datetime import datetime
from collections import deque

class QuantumLogger:
    """量子日志系统"""

    def __init__(self, log_file='/var/log/quantum.log', max_entries=10000):
        self.log_file = log_file
        self.max_entries = max_entries
        self.logs = deque(maxlen=max_entries)
        self.level = 'INFO'
        self.levels = {'DEBUG': 0, 'INFO': 1, 'WARNING': 2, 'ERROR': 3}
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 量子日志系统初始化")

        # 确保日志目录存在
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

    def log(self, level, message, module='quantum', data=None):
        """记录日志"""
        if self.levels.get(level, 1) < self.levels.get(self.level, 1):
            return

        entry = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'module': module,
            'message': message,
            'data': data
        }

        self.logs.append(entry)
        self._write_to_file(entry)

        return entry

    def debug(self, message, module='quantum', data=None):
        """调试日志"""
        return self.log('DEBUG', message, module, data)

    def info(self, message, module='quantum', data=None):
        """信息日志"""
        return self.log('INFO', message, module, data)

    def warning(self, message, module='quantum', data=None):
        """警告日志"""
        return self.log('WARNING', message, module, data)

    def error(self, message, module='quantum', data=None):
        """错误日志"""
        return self.log('ERROR', message, module, data)

    def _write_to_file(self, entry):
        """写入日志文件"""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        except:
            pass

    def get_logs(self, level=None, module=None, limit=100):
        """获取日志"""
        logs = list(self.logs)

        if level:
            logs = [l for l in logs if l['level'] == level]

        if module:
            logs = [l for l in logs if l['module'] == module]

        return logs[-limit:]

    def get_statistics(self):
        """获取日志统计"""
        if not self.logs:
            return {'total': 0}

        level_counts = {}
        module_counts = {}

        for log in self.logs:
            level_counts[log['level']] = level_counts.get(log['level'], 0) + 1
            module_counts[log['module']] = module_counts.get(log['module'], 0) + 1

        return {
            'total': len(self.logs),
            'level_counts': level_counts,
            'module_counts': module_counts,
            'last_log': self.logs[-1] if self.logs else None
        }

    def clear_logs(self):
        """清除日志"""
        self.logs.clear()
        return {'cleared': True}

    def set_level(self, level):
        """设置日志级别"""
        if level in self.levels:
            self.level = level
            return {'level_set': level}
        return {'error': 'Invalid level'}

    def log_circuit_execution(self, circuit_name, gates, result):
        """记录电路执行"""
        self.info(f'Circuit executed: {circuit_name}', 'circuit', {
            'gates': len(gates),
            'result': str(result)[:100]
        })

    def log_gate_operation(self, gate_type, targets):
        """记录门操作"""
        self.debug(f'Gate: {gate_type} on {targets}', 'gate', {
            'gate': gate_type,
            'targets': targets
        })

    def log_measurement(self, result, shots):
        """记录测量"""
        self.info(f'Measurement: {shots} shots', 'measurement', {
            'result': result,
            'shots': shots
        })

    def log_error(self, error_type, error_message, context=None):
        """记录错误"""
        self.error(f'{error_type}: {error_message}', 'error', context)

def main():
    print("=" * 60)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 量子日志系统测试")
    print("=" * 60)

    logger = QuantumLogger('/tmp/quantum_test.log')

    # 测试各级别日志
    print("\n记录日志:")
    logger.debug('调试信息', 'test')
    logger.info('普通信息', 'simulator', {'qubits': 4})
    logger.warning('警告信息', 'optimizer')
    logger.error('错误信息', 'api', {'error_code': 500})

    # 记录电路执行
    print("\n记录电路执行:")
    logger.log_circuit_execution('Bell Circuit', [{'type': 'H'}, {'type': 'CNOT'}], {'result': 'success'})

    # 记录门操作
    print("\n记录门操作:")
    logger.log_gate_operation('H', ['q0'])
    logger.log_gate_operation('CNOT', ['q0', 'q1'])

    # 记录测量
    print("\n记录测量:")
    logger.log_measurement({'00': 512, '11': 512}, 1024)

    # 获取统计
    print("\n日志统计:")
    stats = logger.get_statistics()
    print(f"  总日志数: {stats['total']}")
    print(f"  级别分布: {stats['level_counts']}")

    # 获取日志
    print("\n获取INFO级别日志:")
    logs = logger.get_logs(level='INFO', limit=3)
    for log in logs:
        print(f"  [{log['timestamp'][:16]}] {log['message']}")

    print("\n" + "=" * 60)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 测试完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
