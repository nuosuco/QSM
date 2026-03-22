#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QSM量子系统配置管理器
管理量子系统的配置和设置

功能：
1. 配置加载和保存
2. 默认配置管理
3. 环境变量支持
4. 配置验证
"""

import os
import json
import yaml
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime


class QuantumConfig:
    """量子系统配置"""
    
    # 默认配置
    DEFAULT_CONFIG = {
        'system': {
            'name': 'QSM Quantum System',
            'version': '1.0.0',
            'log_level': 'INFO',
            'max_qubits': 32,
            'default_shots': 1024
        },
        'simulator': {
            'backend': 'aer_simulator',
            'noise_model': None,
            'coupling_map': None,
            'basis_gates': None
        },
        'algorithms': {
            'grover': {
                'iterations': 2,
                'default_qubits': 3
            },
            'qft': {
                'default_qubits': 3,
                'inverse': False
            },
            'shor': {
                'max_attempts': 10,
                'classical_fallback': True
            }
        },
        'error_correction': {
            'enabled': True,
            'code_type': 'shor',
            'threshold': 0.1
        },
        'cryptography': {
            'qkd_protocol': 'BB84',
            'key_length': 256,
            'security_level': 'high'
        },
        'ml': {
            'n_qubits': 4,
            'depth': 2,
            'learning_rate': 0.01
        },
        'optimization': {
            'qaoa_layers': 2,
            'max_iterations': 50,
            'convergence_threshold': 0.001
        },
        'network': {
            'topology': 'star',
            'n_nodes': 5,
            'fidelity_threshold': 0.7
        },
        'output': {
            'docs_dir': '/root/QSM/docs/quantum_modules',
            'results_dir': '/root/QSM/results',
            'export_format': 'json'
        }
    }
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path
        self.config = self.DEFAULT_CONFIG.copy()
        
        if config_path:
            self.load(config_path)
        
        # 从环境变量覆盖
        self._load_from_env()
    
    def load(self, config_path: str) -> bool:
        """加载配置文件"""
        if not os.path.exists(config_path):
            return False
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.endswith('.json'):
                    loaded_config = json.load(f)
                elif config_path.endswith(('.yml', '.yaml')):
                    loaded_config = yaml.safe_load(f)
                else:
                    return False
            
            # 深度合并
            self._deep_merge(self.config, loaded_config)
            return True
            
        except Exception as e:
            print(f"配置加载失败: {e}")
            return False
    
    def save(self, config_path: str = None) -> bool:
        """保存配置文件"""
        path = config_path or self.config_path
        if not path:
            return False
        
        try:
            os.makedirs(os.path.dirname(path) if os.path.dirname(path) else '.', exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                if path.endswith('.json'):
                    json.dump(self.config, f, indent=2, ensure_ascii=False)
                elif path.endswith(('.yml', '.yaml')):
                    yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
            
            return True
            
        except Exception as e:
            print(f"配置保存失败: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值（支持点号分隔的键）"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """设置配置值"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def _deep_merge(self, base: Dict, override: Dict) -> None:
        """深度合并配置"""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
    
    def _load_from_env(self) -> None:
        """从环境变量加载配置"""
        env_mappings = {
            'QSM_MAX_QUBITS': ('system', 'max_qubits'),
            'QSM_SHOTS': ('system', 'default_shots'),
            'QSM_BACKEND': ('simulator', 'backend'),
            'QSM_LOG_LEVEL': ('system', 'log_level'),
            'QSM_QKD_KEY_LENGTH': ('cryptography', 'key_length'),
        }
        
        for env_var, config_keys in env_mappings.items():
            value = os.environ.get(env_var)
            if value:
                # 导航到配置位置
                config = self.config
                for key in config_keys[:-1]:
                    config = config.setdefault(key, {})
                
                # 尝试类型转换
                try:
                    typed_value = json.loads(value)
                except:
                    typed_value = value
                
                config[config_keys[-1]] = typed_value
    
    def validate(self) -> Dict:
        """验证配置"""
        errors = []
        warnings = []
        
        # 验证量子比特数
        max_qubits = self.get('system.max_qubits', 32)
        if max_qubits < 1:
            errors.append('max_qubits必须大于0')
        elif max_qubits > 64:
            warnings.append(f'max_qubits={max_qubits}可能导致内存问题')
        
        # 验证shots
        shots = self.get('system.default_shots', 1024)
        if shots < 1:
            errors.append('shots必须大于0')
        
        # 验证key_length
        key_length = self.get('cryptography.key_length', 256)
        if key_length < 64:
            warnings.append('key_length过短，建议至少64')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return self.config.copy()
    
    def __repr__(self) -> str:
        return f"QuantumConfig({json.dumps(self.config, indent=2, ensure_ascii=False)})"


class QuantumConfigManager:
    """量子配置管理器"""
    
    DEFAULT_CONFIG_PATH = '/root/QSM/config/quantum_config.json'
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self.config = QuantumConfig()
    
    def load_config(self, path: str = None) -> Dict:
        """加载配置"""
        config_path = path or self.config_path
        
        if os.path.exists(config_path):
            self.config.load(config_path)
        
        return self.config.to_dict()
    
    def save_config(self, path: str = None) -> bool:
        """保存配置"""
        return self.config.save(path or self.config_path)
    
    def get_config(self) -> QuantumConfig:
        """获取配置对象"""
        return self.config
    
    def reset_to_defaults(self) -> None:
        """重置为默认配置"""
        self.config = QuantumConfig()
    
    def create_default_config_file(self, path: str = None) -> bool:
        """创建默认配置文件"""
        save_path = path or self.config_path
        
        # 创建目录
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # 保存默认配置
        default_config = QuantumConfig()
        return default_config.save(save_path)


def create_default_config():
    """创建默认配置文件"""
    print("=" * 70)
    print("QSM量子系统配置管理器")
    print("=" * 70)
    
    manager = QuantumConfigManager()
    
    # 创建默认配置文件
    print("\n创建默认配置文件...")
    success = manager.create_default_config_file()
    
    if success:
        print(f"✅ 配置文件已创建: {manager.config_path}")
    else:
        print(f"❌ 配置文件创建失败")
    
    # 验证配置
    print("\n验证配置...")
    validation = manager.config.validate()
    
    if validation['valid']:
        print("✅ 配置验证通过")
    else:
        print(f"❌ 配置验证失败: {validation['errors']}")
    
    if validation['warnings']:
        for warning in validation['warnings']:
            print(f"⚠️ {warning}")
    
    # 显示配置
    print("\n当前配置:")
    print(manager.config)
    
    return manager


if __name__ == "__main__":
    create_default_config()
