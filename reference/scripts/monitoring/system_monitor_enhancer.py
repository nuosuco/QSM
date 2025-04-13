#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
系统监控增强器
用于增强系统监控功能，包括量子基因标记监控等
"""

import os
import time
import psutil
import logging
from typing import Dict, Any, Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('system_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("System-Monitor")

class SystemMonitorEnhancer:
    """系统监控增强器"""
    
    def __init__(self, ref_core):
        """初始化系统监控增强器
        
        Args:
            ref_core: Ref核心系统实例
        """
        self.ref_core = ref_core
        self.running = False
        self.monitoring_interval = 60  # 监控间隔（秒）
        self.last_check = 0
        self.system_stats = {}
        
    def start_monitoring(self):
        """启动系统监控"""
        if self.running:
            logger.warning("系统监控已在运行")
            return
        
        self.running = True
        logger.info("系统监控已启动")
        
        while self.running:
            try:
                self._check_system_status()
                time.sleep(self.monitoring_interval)
            except Exception as e:
                logger.error(f"系统监控出错: {str(e)}")
                time.sleep(5)  # 出错后等待5秒再重试
    
    def stop_monitoring(self):
        """停止系统监控"""
        self.running = False
        logger.info("系统监控已停止")
    
    def _check_system_status(self):
        """检查系统状态"""
        try:
            # 获取CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 获取内存使用情况
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # 获取磁盘使用情况
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            # 更新系统状态
            self.system_stats = {
                'timestamp': time.time(),
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'disk_percent': disk_percent
            }
            
            # 检查是否需要发出警告
            self._check_warnings()
            
            logger.debug(f"系统状态: CPU {cpu_percent}%, 内存 {memory_percent}%, 磁盘 {disk_percent}%")
            
        except Exception as e:
            logger.error(f"检查系统状态时出错: {str(e)}")
    
    def _check_warnings(self):
        """检查是否需要发出警告"""
        # CPU使用率超过80%
        if self.system_stats['cpu_percent'] > 80:
            logger.warning(f"CPU使用率过高: {self.system_stats['cpu_percent']}%")
        
        # 内存使用率超过90%
        if self.system_stats['memory_percent'] > 90:
            logger.warning(f"内存使用率过高: {self.system_stats['memory_percent']}%")
        
        # 磁盘使用率超过85%
        if self.system_stats['disk_percent'] > 85:
            logger.warning(f"磁盘使用率过高: {self.system_stats['disk_percent']}%")
    
    def get_system_stats(self) -> Dict[str, Any]:
        """获取系统状态统计信息
        
        Returns:
            系统状态统计信息字典
        """
        return self.system_stats.copy()
    
    def enhance_monitoring(self, target_path: Optional[str] = None):
        """增强系统监控
        
        Args:
            target_path: 目标路径，如果为None则监控整个系统
        """
        try:
            if not self.running:
                logger.warning("系统监控增强器未启动")
                return
            
            if target_path and not os.path.exists(target_path):
                logger.error(f"目标路径不存在: {target_path}")
                return
            
            # 在这里添加具体的监控增强逻辑
            logger.info(f"正在增强系统监控: {target_path if target_path else '整个系统'}")
            
        except Exception as e:
            logger.error(f"增强系统监控时出错: {str(e)}") 

"""
"""
量子基因编码: QE-SYS-8292ECE55EE3
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
""""""

// 开发团队：中华 ZhoHo ，Claude 
