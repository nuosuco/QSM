"""
QNT 日志系统
"""
import logging
import os
from datetime import datetime
from typing import Optional


class QNTLogger:
    """QNT专用日志器"""
    
    _instance = None
    _logger = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_logger()
        return cls._instance
    
    def _init_logger(self):
        """初始化日志器"""
        self._logger = logging.getLogger('QNT')
        self._logger.setLevel(logging.INFO)
        
        # 避免重复添加handler
        if self._logger.handlers:
            return
        
        # 创建日志目录
        log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        # 文件handler
        log_file = os.path.join(log_dir, f'qnt_{datetime.now().strftime("%Y%m%d")}.log')
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # 控制台handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self._logger.addHandler(file_handler)
        self._logger.addHandler(console_handler)
    
    def info(self, message: str):
        self._logger.info(message)
    
    def debug(self, message: str):
        self._logger.debug(message)
    
    def warning(self, message: str):
        self._logger.warning(message)
    
    def error(self, message: str):
        self._logger.error(message)
    
    def critical(self, message: str):
        self._logger.critical(message)


# 全局日志实例
log = QNTLogger()
