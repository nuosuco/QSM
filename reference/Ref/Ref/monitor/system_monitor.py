#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Ref系统 - 系统监控增强器
负责监控系统状态和自动优化
"""

import os
import sys
import time
import logging
import threading
import psutil
from typing import Dict, Any, List, Optional

# 配置日志记录器
logger = logging.getLogger("System-Monitor")
if not logger.handlers:
    # 避免重复配置
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # 添加控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 添加文件处理器
    try:
        # 确保日志目录存在
        os.makedirs("Ref/logs", exist_ok=True)
        file_handler = logging.FileHandler("Ref/logs/system_monitor.log")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"配置日志处理器时出错: {str(e)}")

class SystemMonitorEnhancer:
    """系统监控增强器，负责收集系统状态并提供优化"""
    
    def __init__(self, ref_core=None):
        """初始化系统监控增强器
        
        Args:
            ref_core: Ref核心实例，可选
        """
        self.ref_core = ref_core
        self.monitoring = False
        self.monitor_thread = None
        self.status_history = []
        self.max_history_entries = 100  # 保留最近100条状态记录
        self.last_check = 0
        self.check_interval = 300  # 5分钟检查一次
        
        # 备份系统索引路径
        self.index_backup_dir = "Ref/backup/index_backups"
        os.makedirs(self.index_backup_dir, exist_ok=True)
    
    def start_monitoring(self):
        """启动系统监控"""
        if self.monitoring:
            logger.warning("系统监控已经在运行中")
            return
        
        self.monitoring = True
        
        # 创建并启动监控线程
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            name="SystemMonitorThread",
            daemon=True
        )
        self.monitor_thread.start()
        
        logger.info("系统监控已启动")
    
    def stop_monitoring(self):
        """停止系统监控"""
        if not self.monitoring:
            logger.warning("系统监控未在运行")
            return
        
        self.monitoring = False
        
        # 等待监控线程结束
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
            self.monitor_thread = None
        
        logger.info("系统监控已停止")
    
    def _monitoring_loop(self):
        """监控循环，定期检查系统状态"""
        check_interval = 60  # 每分钟检查一次系统状态
        optimize_interval = 3600  # 每小时尝试一次优化
        last_optimize = 0
        
        while self.monitoring:
            try:
                # 收集系统状态
                status = self._collect_system_status()
                
                # 添加到历史记录
                self._add_status_to_history(status)
                
                # 是否需要优化
                current_time = time.time()
                if (current_time - last_optimize) >= optimize_interval:
                    self._check_and_optimize()
                    last_optimize = current_time
            
            except Exception as e:
                logger.error(f"监控循环出错: {str(e)}")
            
            # 休眠一段时间
            time.sleep(check_interval)
    
    def _collect_system_status(self) -> Dict[str, Any]:
        """收集系统状态
        
        Returns:
            包含系统状态信息的字典
        """
        status = {
            'timestamp': time.time(),
            'cpu': {
                'usage_percent': psutil.cpu_percent(interval=1),
                'count': psutil.cpu_count(),
                'logical_count': psutil.cpu_count(logical=True)
            },
            'memory': {
                'total': psutil.virtual_memory().total,
                'available': psutil.virtual_memory().available,
                'used': psutil.virtual_memory().used,
                'percent': psutil.virtual_memory().percent
            },
            'disk': {
                'total': psutil.disk_usage('/').total,
                'used': psutil.disk_usage('/').used,
                'free': psutil.disk_usage('/').free,
                'percent': psutil.disk_usage('/').percent
            },
            'network': {
                'bytes_sent': psutil.net_io_counters().bytes_sent,
                'bytes_recv': psutil.net_io_counters().bytes_recv
            },
            'models': self._get_models_status()
        }
        
        return status
    
    def _get_models_status(self) -> Dict[str, Any]:
        """获取已注册模型的状态
        
        Returns:
            包含模型状态的字典
        """
        if not self.ref_core:
            return {}
        
        models_status = {}
        for model_id, model_info in self.ref_core.registered_models.items():
            models_status[model_id] = {
                'health_status': model_info.get('health_status', 'unknown'),
                'last_check': model_info.get('last_check', 0),
                'last_repair': model_info.get('last_repair', 0),
                'repair_count': model_info.get('repair_count', 0)
            }
        
        return models_status
    
    def _add_status_to_history(self, status: Dict[str, Any]):
        """将状态添加到历史记录
        
        Args:
            status: 系统状态字典
        """
        self.status_history.append(status)
        
        # 限制历史记录长度
        if len(self.status_history) > self.max_history_entries:
            self.status_history.pop(0)
    
    def _check_and_optimize(self):
        """检查系统状态并执行优化"""
        if not self.status_history or len(self.status_history) < 2:
            return
        
        # 获取最新和最旧的状态记录
        latest = self.status_history[-1]
        oldest = self.status_history[0]
        
        # 检查内存使用率的变化
        mem_increase = latest['memory']['percent'] - oldest['memory']['percent']
        
        # 检查磁盘使用率的变化
        disk_increase = latest['disk']['percent'] - oldest['disk']['percent']
        
        # 如果内存使用率增加了10%以上，尝试优化内存使用
        if mem_increase > 10:
            logger.warning(f"内存使用率增加了 {mem_increase:.1f}%，尝试优化")
            self._optimize_memory()
        
        # 如果磁盘使用率增加了5%以上，尝试优化磁盘空间
        if disk_increase > 5:
            logger.warning(f"磁盘使用率增加了 {disk_increase:.1f}%，尝试优化")
            self._optimize_disk_space()
    
    def _optimize_memory(self):
        """优化内存使用"""
        logger.info("优化内存使用...")
        
        # 在实际应用中，这里应该实现具体的内存优化逻辑
        # 例如清理缓存、重载模块等
        
        # 模拟优化操作
        if self.ref_core:
            # 重新加载注册模型
            self.ref_core._load_registered_models()
        
        # 强制垃圾回收
        import gc
        gc.collect()
        
        logger.info("内存优化完成")
    
    def _optimize_disk_space(self):
        """优化磁盘空间"""
        logger.info("优化磁盘空间...")
        
        # 在实际应用中，这里应该实现具体的磁盘优化逻辑
        # 例如清理临时文件、压缩日志等
        
        # 清理旧的日志文件
        logs_dir = "Ref/logs"
        if os.path.exists(logs_dir):
            for filename in os.listdir(logs_dir):
                if not filename.endswith('.log'):
                    continue
                
                file_path = os.path.join(logs_dir, filename)
                try:
                    # 如果日志文件超过10MB，截断它
                    if os.path.getsize(file_path) > 10 * 1024 * 1024:
                        # 保留最后1MB的内容
                        with open(file_path, 'rb') as f:
                            f.seek(-1024 * 1024, 2)
                            tail_content = f.read()
                        
                        with open(file_path, 'wb') as f:
                            f.write(tail_content)
                        
                        logger.info(f"已优化日志文件: {filename}")
                except Exception as e:
                    logger.error(f"优化日志文件 {filename} 出错: {str(e)}")
        
        # 清理临时文件
        tmp_dir = "Ref/tmp"
        if os.path.exists(tmp_dir):
            for filename in os.listdir(tmp_dir):
                file_path = os.path.join(tmp_dir, filename)
                try:
                    os.remove(file_path)
                    logger.debug(f"已删除临时文件: {filename}")
                except Exception as e:
                    logger.error(f"删除临时文件 {filename} 出错: {str(e)}")
        
        logger.info("磁盘空间优化完成")
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取当前系统状态
        
        Returns:
            包含系统状态的字典
        """
        return self._collect_system_status()
    
    def get_detailed_status(self) -> Dict[str, Any]:
        """获取详细的系统状态
        
        Returns:
            包含详细系统状态的字典
        """
        status = self.get_system_status()
        
        # 添加更多详细信息
        status['processes'] = []
        
        for proc in psutil.process_iter(['pid', 'name', 'username', 'memory_percent', 'cpu_percent']):
            try:
                pinfo = proc.as_dict()
                status['processes'].append(pinfo)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        # 获取历史状态统计
        if self.status_history:
            status['history'] = {
                'entries': len(self.status_history),
                'first_timestamp': self.status_history[0]['timestamp'],
                'last_timestamp': self.status_history[-1]['timestamp'],
                'cpu_avg': sum(entry['cpu']['usage_percent'] for entry in self.status_history) / len(self.status_history),
                'memory_avg': sum(entry['memory']['percent'] for entry in self.status_history) / len(self.status_history),
                'disk_avg': sum(entry['disk']['percent'] for entry in self.status_history) / len(self.status_history)
            }
        
        return status
    
    def _optimize_indices(self) -> bool:
        """优化项目索引
        
        Returns:
            如果优化成功则返回True，否则返回False
        """
        logger.info("优化项目索引...")
        
        # 在实际应用中，这里应该实现具体的索引优化逻辑
        # 例如重建搜索索引、优化数据库索引等
        
        # 示例实现：备份当前索引
        timestamp = int(time.time())
        backup_path = os.path.join(self.index_backup_dir, f"index_backup_{timestamp}")
        os.makedirs(backup_path, exist_ok=True)
        
        # 优化系统状态
        # 这里只是模拟优化过程
        time.sleep(1)
        
        # 优化日志索引
        try:
            self._optimize_log_indices()
            logger.info("日志索引优化完成")
        except Exception as e:
            logger.error(f"优化日志索引时出错: {str(e)}")
        
        # 优化模型索引
        try:
            self._optimize_model_indices()
            logger.info("模型索引优化完成")
        except Exception as e:
            logger.error(f"优化模型索引时出错: {str(e)}")
        
        logger.info("项目索引优化完成")
        return True
    
    def _optimize_log_indices(self):
        """优化日志索引"""
        # 在实际应用中实现具体的日志索引优化逻辑
        pass
    
    def _optimize_model_indices(self):
        """优化模型索引"""
        # 在实际应用中实现具体的模型索引优化逻辑
        pass
    
    def auto_optimize(self) -> Dict[str, Any]:
        """自动优化系统
        
        Returns:
            包含优化结果的字典
        """
        logger.info("开始自动优化...")
        
        results = {
            'started_at': time.time(),
            'operations': [],
            'status': 'in_progress'
        }
        
        try:
            # 优化内存
            mem_before = psutil.virtual_memory().percent
            self._optimize_memory()
            mem_after = psutil.virtual_memory().percent
            
            results['operations'].append({
                'type': 'memory_optimization',
                'before': mem_before,
                'after': mem_after,
                'change': mem_before - mem_after,
                'success': True
            })
            
            # 优化磁盘空间
            disk_before = psutil.disk_usage('/').percent
            self._optimize_disk_space()
            disk_after = psutil.disk_usage('/').percent
            
            results['operations'].append({
                'type': 'disk_optimization',
                'before': disk_before,
                'after': disk_after,
                'change': disk_before - disk_after,
                'success': True
            })
            
            # 优化索引
            index_optimization = self._optimize_indices()
            
            results['operations'].append({
                'type': 'index_optimization',
                'success': index_optimization
            })
            
            results['status'] = 'completed'
            results['completed_at'] = time.time()
            results['duration'] = results['completed_at'] - results['started_at']
            
            logger.info(f"自动优化完成，耗时 {results['duration']:.2f} 秒")
            
        except Exception as e:
            logger.error(f"自动优化失败: {str(e)}")
            
            results['status'] = 'failed'
            results['error'] = str(e)
            results['completed_at'] = time.time()
            results['duration'] = results['completed_at'] - results['started_at']
        
        return results


# 单例实例
_monitor_instance = None

def get_system_monitor(ref_core=None) -> SystemMonitorEnhancer:
    """获取系统监控增强器单例
    
    Args:
        ref_core: Ref核心实例，可选
        
    Returns:
        系统监控增强器实例
    """
    global _monitor_instance
    
    if _monitor_instance is None:
        _monitor_instance = SystemMonitorEnhancer(ref_core)
    
    return _monitor_instance


if __name__ == "__main__":
    # 如果作为主程序运行，则启动监控
    monitor = get_system_monitor()
    monitor.start_monitoring()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        monitor.stop_monitoring()
        print("系统监控已停止") 

"""

"""
量子基因编码: QE-SYS-796FB2BEE03F
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
"""
"""

// 开发团队：中华 ZhoHo ，Claude 

