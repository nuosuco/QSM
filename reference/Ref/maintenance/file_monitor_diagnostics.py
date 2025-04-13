#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
File Monitor Diagnostics Tool
Used to diagnose and repair the quantum file monitoring system
"""

import os
import sys
import time
import logging
import argparse
from pathlib import Path
import threading
import json

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('file_monitor_diagnostics.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("FileMonitorDiagnostics")

# 添加项目根目录到系统路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

# 尝试导入相关模块
try:
    from Ref.utils.file_monitor import get_file_monitor, QuantumFileMonitor
    file_monitor_available = True
    logger.info("Successfully imported file monitoring modules")
except ImportError as e:
    file_monitor_available = False
    logger.error(f"Could not import file monitoring modules: {e}")

class FileMonitorDiagnostics:
    """诊断工具，用于检查和修复文件监控系统"""
    
    def __init__(self):
        """初始化诊断工具"""
        self.logger = logging.getLogger("FileMonitorDiagnostics")
        self.file_monitor = None
        self.issues_found = []
        self.fixes_applied = []
        
    def run_diagnostics(self):
        """运行全面诊断"""
        self.logger.info("Starting file monitor diagnostics...")
        
        # 检查是否可以获取文件监控实例
        if not file_monitor_available:
            self.issues_found.append("File monitor modules not available")
            self.logger.error("Cannot run diagnostics: File monitor modules not available")
            return False
        
        # 获取文件监控实例
        try:
            self.file_monitor = get_file_monitor()
            self.logger.info("Successfully obtained file monitor instance")
        except Exception as e:
            self.issues_found.append(f"Failed to get file monitor instance: {str(e)}")
            self.logger.error(f"Failed to get file monitor instance: {str(e)}")
            return False
        
        # 执行一系列检查
        self._check_monitor_paths()
        self._check_observer_status()
        self._check_event_handler()
        self._check_monitor_thread()
        
        # 报告发现的问题
        if self.issues_found:
            self.logger.warning(f"Found {len(self.issues_found)} issues:")
            for i, issue in enumerate(self.issues_found, 1):
                self.logger.warning(f"  {i}. {issue}")
        else:
            self.logger.info("No issues found. File monitor system appears healthy.")
        
        return len(self.issues_found) == 0
    
    def _check_monitor_paths(self):
        """检查监控路径配置"""
        if not hasattr(self.file_monitor, 'paths_to_watch') or not self.file_monitor.paths_to_watch:
            self.issues_found.append("No paths configured for monitoring")
            self.logger.warning("No paths configured for monitoring")
            return
        
        # 检查路径是否存在
        invalid_paths = []
        for path in self.file_monitor.paths_to_watch:
            if not os.path.exists(path):
                invalid_paths.append(path)
        
        if invalid_paths:
            self.issues_found.append(f"Found {len(invalid_paths)} invalid monitoring paths")
            self.logger.warning(f"The following paths do not exist: {invalid_paths}")
        else:
            self.logger.info(f"All {len(self.file_monitor.paths_to_watch)} monitoring paths are valid")
    
    def _check_observer_status(self):
        """检查Observer状态"""
        if not hasattr(self.file_monitor, 'observer') or self.file_monitor.observer is None:
            self.issues_found.append("Observer not initialized")
            self.logger.warning("Observer not initialized - file monitor may not be started")
            return
        
        # 检查Observer是否正在运行
        if not hasattr(self.file_monitor.observer, 'is_alive') or not self.file_monitor.observer.is_alive():
            self.issues_found.append("Observer is not running")
            self.logger.warning("Observer is not running - file events will not be detected")
        else:
            self.logger.info("Observer is running properly")
    
    def _check_event_handler(self):
        """检查事件处理器"""
        if not hasattr(self.file_monitor, 'event_handler'):
            self.issues_found.append("Event handler not initialized")
            self.logger.warning("Event handler not initialized")
            return
        
        # 检查事件处理器的关键方法
        handler = self.file_monitor.event_handler
        required_methods = ['on_moved', '_process_moved_file']
        
        missing_methods = []
        for method in required_methods:
            if not hasattr(handler, method) or not callable(getattr(handler, method)):
                missing_methods.append(method)
        
        if missing_methods:
            self.issues_found.append(f"Event handler missing required methods: {', '.join(missing_methods)}")
            self.logger.warning(f"Event handler missing required methods: {', '.join(missing_methods)}")
        else:
            self.logger.info("Event handler has all required methods")
    
    def _check_monitor_thread(self):
        """检查监控线程状态"""
        if not hasattr(self.file_monitor, 'watch_thread'):
            self.issues_found.append("Watch thread not initialized")
            self.logger.warning("Watch thread not initialized")
            return
        
        if self.file_monitor.watch_thread is None:
            self.issues_found.append("Watch thread is None")
            self.logger.warning("Watch thread is None - monitor may not be running")
            return
        
        # 检查线程是否活跃
        if not self.file_monitor.watch_thread.is_alive():
            self.issues_found.append("Watch thread is not active")
            self.logger.warning("Watch thread is not active - monitor may be stalled")
        else:
            self.logger.info("Watch thread is active")
    
    def repair_issues(self):
        """尝试修复发现的问题"""
        if not self.issues_found:
            self.logger.info("No issues to repair")
            return True
        
        self.logger.info(f"Attempting to repair {len(self.issues_found)} issues...")
        
        # 尝试重启文件监控
        try:
            # 如果文件监控正在运行，先停止它
            if hasattr(self.file_monitor, 'running') and self.file_monitor.running:
                self.logger.info("Stopping file monitor before repairs...")
                self.file_monitor.stop()
                time.sleep(1)  # 给线程时间完全停止
            
            # 检查和修复监控路径
            self._repair_monitor_paths()
            
            # 启动文件监控
            self.logger.info("Starting file monitor with repaired configuration...")
            self.file_monitor.start()
            
            # 记录修复动作
            self.fixes_applied.append("Restarted file monitor with validated configuration")
            self.logger.info("File monitor restarted successfully")
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to repair file monitor: {str(e)}")
            return False
    
    def _repair_monitor_paths(self):
        """修复监控路径"""
        # 确保监控路径存在
        if not hasattr(self.file_monitor, 'paths_to_watch') or not self.file_monitor.paths_to_watch:
            # 使用项目根目录作为默认路径
            self.file_monitor.paths_to_watch = [project_root]
            self.fixes_applied.append(f"Set default monitoring path to project root: {project_root}")
            self.logger.info(f"Set default monitoring path to project root: {project_root}")
        else:
            # 过滤掉不存在的路径
            valid_paths = [path for path in self.file_monitor.paths_to_watch if os.path.exists(path)]
            invalid_paths = [path for path in self.file_monitor.paths_to_watch if not os.path.exists(path)]
            
            if invalid_paths:
                self.logger.warning(f"Removing {len(invalid_paths)} invalid paths")
                self.fixes_applied.append(f"Removed {len(invalid_paths)} invalid monitoring paths")
            
            # 如果所有路径都不存在，添加项目根目录
            if not valid_paths:
                valid_paths = [project_root]
                self.fixes_applied.append("Added project root as fallback monitoring path")
                self.logger.info("Added project root as fallback monitoring path")
            
            self.file_monitor.paths_to_watch = valid_paths
            self.logger.info(f"Updated monitoring paths to: {valid_paths}")
    
    def generate_report(self, output_file=None):
        """生成诊断报告"""
        report = {
            "timestamp": time.time(),
            "date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "file_monitor_available": file_monitor_available,
            "issues_found": self.issues_found,
            "fixes_applied": self.fixes_applied,
            "status": "healthy" if not self.issues_found else "issues_found"
        }
        
        # 添加文件监控状态
        if self.file_monitor:
            report["monitor_status"] = {
                "running": getattr(self.file_monitor, 'running', False),
                "paths_monitored": getattr(self.file_monitor, 'paths_to_watch', []),
                "observer_alive": (
                    getattr(self.file_monitor.observer, 'is_alive', lambda: False)() 
                    if hasattr(self.file_monitor, 'observer') and self.file_monitor.observer 
                    else False
                )
            }
        
        # 将报告保存到文件
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(report, f, indent=2, ensure_ascii=False)
                self.logger.info(f"Report saved to {output_file}")
            except Exception as e:
                self.logger.error(f"Failed to save report to {output_file}: {str(e)}")
        
        # 返回报告数据
        return report

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="File Monitor Diagnostics Tool")
    parser.add_argument("--repair", action="store_true", help="Attempt to repair found issues")
    parser.add_argument("--report", action="store_true", help="Generate a diagnostic report")
    parser.add_argument("--output", help="Output file for the report (default: file_monitor_report.json)")
    
    args = parser.parse_args()
    
    # 创建诊断工具实例
    diagnostics = FileMonitorDiagnostics()
    
    # 运行诊断
    diagnostics.run_diagnostics()
    
    # 尝试修复问题
    if args.repair and diagnostics.issues_found:
        diagnostics.repair_issues()
    
    # 生成报告
    if args.report or args.output:
        output_file = args.output or "file_monitor_report.json"
        report = diagnostics.generate_report(output_file)
        
        # 打印报告摘要
        print("\nDiagnostic Report Summary:")
        print(f"Status: {report['status'].upper()}")
        print(f"Issues found: {len(report['issues_found'])}")
        print(f"Fixes applied: {len(report['fixes_applied'])}")
        if args.output:
            print(f"Full report saved to: {args.output}")

if __name__ == "__main__":
    main()

"""

    """
    # 
"""
量子基因编码: QE-DIAG-73F9A52CB841
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
"""
    """
    
# 纠缠状态: 活跃
# 纠缠对象: []
# 纠缠强度: 0.98
""" 