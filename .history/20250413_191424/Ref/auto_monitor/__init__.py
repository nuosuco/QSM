<<<<<<< HEAD
# -*- coding: utf-8 -*- 
"""文件监控服务包初始化文件""" 
 
from .startup_hook import install_startup_hook 
 
__all__ = ['install_startup_hook'] 
=======
"""
Ref自动监控系统

提供文件变化自动监控和实时文件完整性检查功能
"""

from Ref.auto_monitor.file_watcher_service import (
    start_monitor_service, 
    stop_monitor_service,
    is_monitor_running,
    get_monitor_status
)

__all__ = [
    'start_monitor_service', 
    'stop_monitor_service',
    'is_monitor_running',
    'get_monitor_status'
] 

"""

"""
量子基因编码: QE-INI-DE1938688663
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
"""
"""

// 开发团队：中华 ZhoHo ，Claude 
>>>>>>> c8ee4fc6e39ad3985ce941a8efbcb072b6ba0eea
