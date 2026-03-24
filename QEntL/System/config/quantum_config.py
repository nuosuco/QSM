#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
量子配置管理器 - 量子系统配置管理
"""

import json
import os
from datetime import datetime

class QuantumConfig:
    """量子配置管理器"""

    def __init__(self, config_path='/root/QSM/config/quantum_config.json'):
        self.config_path = config_path
        self.config = self._load_default_config()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 量子配置管理器初始化")

    def _load_default_config(self):
        """加载默认配置"""
        return {
            'simulator': {
                'max_qubits': 16,
                'default_shots': 1024,
                'seed': None
            },
            'optimization': {
                'level': 2,  # 0-3
                'remove_redundant': True,
                'merge_gates': True
            },
            'error_correction': {
                'enabled': False,
                'code': 'surface',
                'distance': 3
            },
            'api': {
                'host': '0.0.0.0',
                'port': 8765,
                'cors': True
            },
            'logging': {
                'level': 'INFO',
                'file': '/var/log/quantum.log',
                'console': True
            },
            'cryptography': {
                'key_length': 256,
                'protocol': 'BB84'
            },
            'network': {
                'max_connections': 10,
                'timeout_ms': 5000
            }
        }

    def load(self):
        """从文件加载配置"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    self.config.update(loaded)
                    return {'loaded': True, 'path': self.config_path}
            except Exception as e:
                return {'loaded': False, 'error': str(e)}
        return {'loaded': False, 'error': 'File not found'}

    def save(self):
        """保存配置到文件"""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
        return {'saved': True, 'path': self.config_path}

    def get(self, key, default=None):
        """获取配置值"""
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key, value):
        """设置配置值"""
        keys = key.split('.')
        config = self.config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value
        return {'set': True, 'key': key, 'value': value}

    def get_simulator_config(self):
        """获取模拟器配置"""
        return self.config.get('simulator', {})

    def get_optimization_config(self):
        """获取优化配置"""
        return self.config.get('optimization', {})

    def get_api_config(self):
        """获取API配置"""
        return self.config.get('api', {})

    def validate(self):
        """验证配置"""
        errors = []

        # 检查量子比特数
        max_qubits = self.get('simulator.max_qubits', 16)
        if max_qubits < 1 or max_qubits > 64:
            errors.append(f'Invalid max_qubits: {max_qubits}')

        # 检查优化级别
        level = self.get('optimization.level', 2)
        if level < 0 or level > 3:
            errors.append(f'Invalid optimization level: {level}')

        # 检查端口
        port = self.get('api.port', 8765)
        if port < 1 or port > 65535:
            errors.append(f'Invalid port: {port}')

        return {
            'valid': len(errors) == 0,
            'errors': errors
        }

    def get_all(self):
        """获取所有配置"""
        return self.config.copy()

    def reset(self):
        """重置为默认配置"""
        self.config = self._load_default_config()
        return {'reset': True}

def main():
    print("=" * 60)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 量子配置管理器测试")
    print("=" * 60)

    config = QuantumConfig()

    # 测试获取配置
    print("\n获取配置:")
    print(f"  最大量子比特: {config.get('simulator.max_qubits')}")
    print(f"  默认测量次数: {config.get('simulator.default_shots')}")
    print(f"  API端口: {config.get('api.port')}")

    # 测试设置配置
    print("\n设置配置:")
    result = config.set('simulator.max_qubits', 32)
    print(f"  设置max_qubits=32: {result['set']}")
    print(f"  新值: {config.get('simulator.max_qubits')}")

    # 获取模块配置
    print("\n获取模块配置:")
    sim_config = config.get_simulator_config()
    print(f"  模拟器配置: {sim_config}")

    # 验证配置
    print("\n验证配置:")
    validation = config.validate()
    print(f"  有效: {validation['valid']}")

    # 保存配置
    print("\n保存配置:")
    result = config.save()
    print(f"  保存: {result['saved']}")

    # 重置配置
    print("\n重置配置:")
    config.reset()
    print(f"  max_qubits恢复: {config.get('simulator.max_qubits')}")

    print("\n" + "=" * 60)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 测试完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
