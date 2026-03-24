#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QSM量子系统日志记录器
提供统一的日志记录功能

功能：
1. 多级别日志记录
2. 日志文件管理
3. 控制台输出
4. JSON格式日志
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, Optional, Any
from pathlib import Path


class QuantumLogger:
    """量子系统日志记录器"""
    
    # 日志级别
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL
    
    def __init__(self,
                 name: str = "QSM",
                 log_dir: str = "/root/QSM/logs",
                 level: int = logging.INFO,
                 console_output: bool = True,
                 file_output: bool = True,
                 json_format: bool = False):
        
        self.name = name
        self.log_dir = log_dir
        self.level = level
        self.console_output = console_output
        self.file_output = file_output
        self.json_format = json_format
        
        # 创建日志目录
        os.makedirs(log_dir, exist_ok=True)
        
        # 创建logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # 清除已有handlers
        self.logger.handlers.clear()
        
        # 创建格式器
        if json_format:
            self.formatter = logging.Formatter(
                '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
                '"name": "%(name)s", "message": "%(message)s"}'
            )
        else:
            self.formatter = logging.Formatter(
                '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        
        # 添加handlers
        if console_output:
            self._add_console_handler()
        
        if file_output:
            self._add_file_handler()
    
    def _add_console_handler(self) -> None:
        """添加控制台处理器"""
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(self.level)
        handler.setFormatter(self.formatter)
        self.logger.addHandler(handler)
    
    def _add_file_handler(self) -> None:
        """添加文件处理器"""
        log_file = os.path.join(
            self.log_dir,
            f"{self.name.lower()}_{datetime.now().strftime('%Y%m%d')}.log"
        )
        
        handler = logging.FileHandler(log_file, encoding='utf-8')
        handler.setLevel(self.level)
        handler.setFormatter(self.formatter)
        self.logger.addHandler(handler)
    
    def debug(self, message: str, **kwargs) -> None:
        """记录DEBUG级别日志"""
        self.logger.debug(message, **kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """记录INFO级别日志"""
        self.logger.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """记录WARNING级别日志"""
        self.logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """记录ERROR级别日志"""
        self.logger.error(message, **kwargs)
    
    def critical(self, message: str, **kwargs) -> None:
        """记录CRITICAL级别日志"""
        self.logger.critical(message, **kwargs)
    
    def exception(self, message: str, **kwargs) -> None:
        """记录异常日志"""
        self.logger.exception(message, **kwargs)
    
    def log_algorithm(self,
                      algorithm: str,
                      action: str,
                      result: str = None,
                      metrics: Dict = None) -> None:
        """记录算法执行日志"""
        log_data = {
            'type': 'algorithm',
            'algorithm': algorithm,
            'action': action,
            'timestamp': datetime.now().isoformat()
        }
        
        if result:
            log_data['result'] = result
        
        if metrics:
            log_data['metrics'] = metrics
        
        self.info(json.dumps(log_data, ensure_ascii=False))
    
    def log_quantum_operation(self,
                               operation: str,
                               n_qubits: int,
                               gates: int,
                               execution_time_ms: float,
                               success: bool) -> None:
        """记录量子操作日志"""
        log_data = {
            'type': 'quantum_operation',
            'operation': operation,
            'n_qubits': n_qubits,
            'gates': gates,
            'execution_time_ms': execution_time_ms,
            'success': success,
            'timestamp': datetime.now().isoformat()
        }
        
        level = logging.INFO if success else logging.WARNING
        self.logger.log(level, json.dumps(log_data, ensure_ascii=False))
    
    def log_performance(self,
                        metric_name: str,
                        value: float,
                        unit: str = None,
                        threshold: float = None) -> None:
        """记录性能指标日志"""
        log_data = {
            'type': 'performance',
            'metric': metric_name,
            'value': value,
            'timestamp': datetime.now().isoformat()
        }
        
        if unit:
            log_data['unit'] = unit
        
        if threshold is not None:
            log_data['threshold'] = threshold
            if value > threshold:
                log_data['status'] = 'exceeded'
                self.warning(json.dumps(log_data, ensure_ascii=False))
                return
        
        self.info(json.dumps(log_data, ensure_ascii=False))
    
    def log_error_with_context(self,
                                error: Exception,
                                context: Dict = None) -> None:
        """记录带上下文的错误日志"""
        log_data = {
            'type': 'error',
            'error_type': type(error).__name__,
            'error_message': str(error),
            'timestamp': datetime.now().isoformat()
        }
        
        if context:
            log_data['context'] = context
        
        self.error(json.dumps(log_data, ensure_ascii=False))


class QuantumLogManager:
    """量子日志管理器"""
    
    _loggers: Dict[str, QuantumLogger] = {}
    _default_config = {
        'log_dir': '/root/QSM/logs',
        'level': logging.INFO,
        'console_output': True,
        'file_output': True,
        'json_format': False
    }
    
    @classmethod
    def get_logger(cls, name: str = "QSM", **kwargs) -> QuantumLogger:
        """获取或创建logger"""
        if name not in cls._loggers:
            config = cls._default_config.copy()
            config.update(kwargs)
            cls._loggers[name] = QuantumLogger(name=name, **config)
        
        return cls._loggers[name]
    
    @classmethod
    def set_default_config(cls, **kwargs) -> None:
        """设置默认配置"""
        cls._default_config.update(kwargs)
    
    @classmethod
    def list_loggers(cls) -> list:
        """列出所有logger"""
        return list(cls._loggers.keys())
    
    @classmethod
    def get_log_files(cls, log_dir: str = None) -> list:
        """获取日志文件列表"""
        directory = log_dir or cls._default_config['log_dir']
        if not os.path.exists(directory):
            return []
        
        return [f for f in os.listdir(directory) if f.endswith('.log')]


def run_logger_demo():
    """运行日志记录器演示"""
    print("=" * 70)
    print("QSM量子系统日志记录器演示")
    print("=" * 70)
    
    # 创建logger
    logger = QuantumLogger(
        name="QSM_Demo",
        console_output=True,
        file_output=True
    )
    
    print("\n[1] 基本日志记录...")
    logger.debug("这是一条DEBUG日志")
    logger.info("这是一条INFO日志")
    logger.warning("这是一条WARNING日志")
    logger.error("这是一条ERROR日志")
    
    print("\n[2] 算法执行日志...")
    logger.log_algorithm(
        algorithm="Grover",
        action="search",
        result="found",
        metrics={'iterations': 2, 'success_rate': 0.95}
    )
    
    print("\n[3] 量子操作日志...")
    logger.log_quantum_operation(
        operation="QFT",
        n_qubits=4,
        gates=12,
        execution_time_ms=45.3,
        success=True
    )
    
    print("\n[4] 性能指标日志...")
    logger.log_performance(
        metric_name="cpu_usage",
        value=75.5,
        unit="percent",
        threshold=90.0
    )
    
    print("\n[5] 错误日志...")
    try:
        raise ValueError("示例错误")
    except Exception as e:
        logger.log_error_with_context(e, {'operation': 'demo', 'step': 5})
    
    print("\n" + "=" * 70)
    print("日志记录器演示完成")
    print("=" * 70)
    
    # 显示日志文件
    log_files = QuantumLogManager.get_log_files()
    print(f"\n日志文件: {log_files}")
    
    return logger


if __name__ == "__main__":
    run_logger_demo()
