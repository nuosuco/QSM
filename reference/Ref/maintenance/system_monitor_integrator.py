#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
System Monitor Integrator
Integrates system monitoring and file monitoring diagnostics
"""

import os
import sys
import time
import logging
import argparse
import threading
import json
from datetime import datetime
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('system_monitor_integrated.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("SystemMonitorIntegrator")

# 添加项目根目录到系统路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

# 尝试导入相关模块
system_monitor_available = False
file_monitor_available = False
file_diagnostics_available = False

try:
    from Ref.maintenance.system_monitor_enhancer import SystemMonitorEnhancer
    system_monitor_available = True
    logger.info("Successfully imported system monitoring modules")
except ImportError as e:
    logger.error(f"Could not import system monitoring modules: {e}")

try:
    from Ref.utils.file_monitor import get_file_monitor
    file_monitor_available = True
    logger.info("Successfully imported file monitoring modules")
except ImportError as e:
    logger.error(f"Could not import file monitoring modules: {e}")

try:
    from Ref.maintenance.file_monitor_diagnostics import FileMonitorDiagnostics
    file_diagnostics_available = True
    logger.info("Successfully imported file monitor diagnostics modules")
except ImportError as e:
    logger.error(f"Could not import file monitor diagnostics: {e}")

class SystemMonitorIntegrator:
    """集成系统监控和文件监控诊断"""
    
    def __init__(self):
        """初始化集成监控器"""
        self.logger = logging.getLogger("SystemMonitorIntegrator")
        self.ref_core = None
        self.system_monitor = None
        self.file_diagnostics = None
        self.running = False
        self.integrated_thread = None
        self.check_interval = 900  # 15分钟检查一次
        self.last_check = 0
        self.status_history = []
        
        # 如果存在logs目录，将日志文件保存到那里
        log_dir = os.path.join(project_root, '.logs')
        if not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir)
                logger.info(f"Created log directory: {log_dir}")
            except Exception as e:
                logger.warning(f"Could not create log directory: {e}")
        
        # 尝试加载各个组件
        self._load_components()
    
    def _load_components(self):
        """加载各个监控组件"""
        # 创建一个空的ref_core对象供SystemMonitorEnhancer使用
        class SimpleRefCore:
            def __init__(self):
                self.project_root = project_root
        
        self.ref_core = SimpleRefCore()
        
        # 初始化系统监控增强器
        if system_monitor_available:
            try:
                self.system_monitor = SystemMonitorEnhancer(ref_core=self.ref_core)
                logger.info("Initialized system monitor enhancer")
            except Exception as e:
                logger.error(f"Failed to initialize system monitor: {e}")
        
        # 初始化文件监控诊断
        if file_diagnostics_available:
            try:
                self.file_diagnostics = FileMonitorDiagnostics()
                logger.info("Initialized file monitor diagnostics")
            except Exception as e:
                logger.error(f"Failed to initialize file diagnostics: {e}")
    
    def start(self):
        """启动集成监控"""
        if self.running:
            logger.warning("Integrated monitor is already running")
            return
        
        self.running = True
        logger.info("Starting integrated system monitoring")
        
        # 启动系统监控
        if self.system_monitor:
            try:
                self.system_monitor.start_monitoring()
                logger.info("Started system monitoring")
            except Exception as e:
                logger.error(f"Failed to start system monitoring: {e}")
        
        # 立即运行文件监控诊断
        if self.file_diagnostics:
            try:
                self._run_file_diagnostics()
            except Exception as e:
                logger.error(f"Initial file diagnostics failed: {e}")
        
        # 启动集成线程
        self.integrated_thread = threading.Thread(
            target=self._integrated_loop,
            name="IntegratedMonitorThread",
            daemon=True
        )
        self.integrated_thread.start()
        logger.info("Integrated monitoring thread started")
    
    def stop(self):
        """停止集成监控"""
        if not self.running:
            return
        
        self.running = False
        logger.info("Stopping integrated system monitoring")
        
        # 停止系统监控
        if self.system_monitor:
            try:
                self.system_monitor.stop_monitoring()
                logger.info("Stopped system monitoring")
            except Exception as e:
                logger.error(f"Failed to stop system monitoring: {e}")
        
        # 等待集成线程结束
        if self.integrated_thread:
            self.integrated_thread.join(timeout=5)
            self.integrated_thread = None
        
        logger.info("Integrated monitoring stopped")
    
    def _integrated_loop(self):
        """集成监控循环"""
        try:
            while self.running:
                current_time = time.time()
                
                # 检查是否应该运行诊断
                if (current_time - self.last_check) >= self.check_interval:
                    logger.info("Running scheduled integrated monitoring checks")
                    
                    # 获取系统状态
                    system_stats = self._get_system_stats()
                    
                    # 运行文件监控诊断
                    file_monitor_status = self._run_file_diagnostics()
                    
                    # 记录状态历史
                    self._record_status(system_stats, file_monitor_status)
                    
                    # 更新最后检查时间
                    self.last_check = current_time
                
                # 睡眠一段时间
                time.sleep(60)  # 每分钟检查一次是否应该运行诊断
                
        except Exception as e:
            logger.error(f"Error in integrated monitoring loop: {e}")
        finally:
            self.running = False
    
    def _get_system_stats(self):
        """获取系统状态"""
        if not self.system_monitor:
            return {"status": "not_available", "timestamp": time.time()}
        
        try:
            return self.system_monitor.get_system_stats()
        except Exception as e:
            logger.error(f"Failed to get system stats: {e}")
            return {"status": "error", "timestamp": time.time(), "error": str(e)}
    
    def _run_file_diagnostics(self):
        """运行文件监控诊断"""
        if not self.file_diagnostics:
            return {"status": "not_available", "timestamp": time.time()}
        
        try:
            # 运行诊断
            diagnostics_result = self.file_diagnostics.run_diagnostics()
            
            # 如果有问题，尝试修复
            if not diagnostics_result and self.file_diagnostics.issues_found:
                repair_result = self.file_diagnostics.repair_issues()
                logger.info(f"Repair attempt result: {repair_result}")
            
            # 生成报告
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = os.path.join(project_root, '.logs', f'file_monitor_report_{timestamp}.json')
            
            report = self.file_diagnostics.generate_report(report_file)
            logger.info(f"File diagnostics report generated: {report_file}")
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to run file diagnostics: {e}")
            return {"status": "error", "timestamp": time.time(), "error": str(e)}
    
    def _record_status(self, system_stats, file_monitor_status):
        """记录状态历史"""
        status_entry = {
            "timestamp": time.time(),
            "date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "system_stats": system_stats,
            "file_monitor_status": file_monitor_status
        }
        
        # 添加到历史记录
        self.status_history.append(status_entry)
        
        # 限制历史记录的大小
        max_history = 50
        if len(self.status_history) > max_history:
            self.status_history = self.status_history[-max_history:]
        
        # 保存历史记录到文件
        try:
            history_file = os.path.join(project_root, '.logs', 'monitor_history.json')
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(self.status_history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save status history: {e}")
    
    def generate_status_report(self, output_file=None):
        """生成状态报告"""
        # 获取最新状态
        system_stats = self._get_system_stats()
        file_monitor_status = self._run_file_diagnostics()
        
        # 创建报告
        report = {
            "timestamp": time.time(),
            "date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "system_monitor_available": system_monitor_available,
            "file_monitor_available": file_monitor_available,
            "file_diagnostics_available": file_diagnostics_available,
            "current_status": {
                "system": system_stats,
                "file_monitor": file_monitor_status
            },
            "history_entries": len(self.status_history)
        }
        
        # 计算系统健康状态
        system_healthy = True
        if system_stats.get("status") == "error":
            system_healthy = False
        if isinstance(system_stats.get("cpu_percent"), (int, float)) and system_stats.get("cpu_percent", 0) > 90:
            system_healthy = False
        if isinstance(system_stats.get("memory_percent"), (int, float)) and system_stats.get("memory_percent", 0) > 95:
            system_healthy = False
        
        # 计算文件监控健康状态
        file_monitor_healthy = file_monitor_status.get("status") == "healthy"
        
        # 添加综合健康状态
        report["health"] = {
            "system": "healthy" if system_healthy else "issues_found",
            "file_monitor": "healthy" if file_monitor_healthy else "issues_found",
            "overall": "healthy" if (system_healthy and file_monitor_healthy) else "issues_found"
        }
        
        # 将报告保存到文件
        if output_file:
            try:
                output_dir = os.path.dirname(output_file)
                if output_dir and not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                    
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(report, f, indent=2, ensure_ascii=False)
                logger.info(f"Status report saved to {output_file}")
            except Exception as e:
                logger.error(f"Failed to save status report to {output_file}: {e}")
        
        # 返回报告数据
        return report

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Integrated System and File Monitor")
    parser.add_argument("--report", action="store_true", help="Generate a status report")
    parser.add_argument("--monitor", action="store_true", help="Run continuous monitoring")
    parser.add_argument("--output", help="Output file for the report (default: integrated_monitor_report.json)")
    parser.add_argument("--interval", type=int, default=900, help="Check interval in seconds (default: 900)")
    
    args = parser.parse_args()
    
    # 创建集成监控器
    integrator = SystemMonitorIntegrator()
    
    # 设置检查间隔
    if args.interval:
        integrator.check_interval = args.interval
    
    # 是否应该运行连续监控
    if args.monitor:
        try:
            integrator.start()
            logger.info("Press Ctrl+C to stop monitoring")
            
            # 保持程序运行
            try:
                while integrator.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("User interrupted. Stopping monitoring...")
            finally:
                integrator.stop()
                
        except Exception as e:
            logger.error(f"Monitoring failed: {e}")
    
    # 是否应该生成报告
    if args.report or args.output:
        output_file = args.output or os.path.join(project_root, '.logs', 'integrated_monitor_report.json')
        report = integrator.generate_status_report(output_file)
        
        # 打印报告摘要
        print("\nIntegrated Monitor Report Summary:")
        print(f"Date: {report['date']}")
        print(f"System health: {report['health']['system'].upper()}")
        print(f"File monitor health: {report['health']['file_monitor'].upper()}")
        print(f"Overall system health: {report['health']['overall'].upper()}")
        
        if args.output:
            print(f"Full report saved to: {output_file}")
    
    # 如果没有指定任何操作，显示帮助
    if not (args.report or args.output or args.monitor):
        parser.print_help()

if __name__ == "__main__":
    main()

"""

    """
    # 
"""
量子基因编码: QE-SMON-B47F1C9D3A62
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
"""
    """
    
# 纠缠状态: 活跃
# 纠缠对象: []
# 纠缠强度: 0.98
""" 