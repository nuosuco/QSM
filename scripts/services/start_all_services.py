#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
统一服务启动脚本

该脚本用于启动所有QSM相关服务，包括QSM服务、WeQ服务、SOM服务和Ref服务。
脚本会调用每个模块自己的启动脚本，而不是直接启动各个服务。
支持并行启动多个服务，并提供日志记录功能。

用法:
    python scripts/services/start_all_services.py [--parallel] [--services SERVICE1 SERVICE2 ...]

参数:
    --parallel: 并行启动所有服务
    --services: 指定要启动的服务，可选值: qsm, weq, som, ref, all (默认: all)
    --retry: 启动失败时的重试次数 (默认: 3)
    --health-check: 是否进行健康检查 (默认: True)
    --health-check-interval: 健康检查间隔(秒) (默认: 30)
    --log-level: 日志级别 (默认: INFO)
    --log-dir: 日志目录 (默认: .logs)
"""

import os
import sys
import time
import argparse
import subprocess
import datetime
import platform
import signal
from pathlib import Path
import threading
import queue
import importlib.util
import atexit
import json
import requests
import logging
from logging.handlers import RotatingFileHandler
from typing import Dict, List, Optional, Tuple

# 获取项目根目录
ROOT_DIR = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 创建日志目录
LOG_DIR = ROOT_DIR / '.logs'
LOG_DIR.mkdir(exist_ok=True)

# 配置基本日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(
            LOG_DIR / 'service_manager.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        ),
        logging.StreamHandler()
    ]
)

# 导入日志管理器
sys.path.append(str(ROOT_DIR))
from Ref.utils.log_manager import LogManager

# 初始化日志管理器
log_manager = LogManager(ROOT_DIR)
logger = log_manager.get_service_logger('service_manager')

# 模块启动脚本定义
MODULE_SCRIPTS = {
    'qsm': {
        'name': 'QSM模块',
        'script': ROOT_DIR / 'QSM/scripts/services/QSM_start_services.py',
        'args': ['--port', '5000'],
        'description': 'QSM量子自组织市场模块',
        'process': None,
        'dependencies': [],
        'optional_dependencies': [],
        'health_check': {
            'url': 'http://localhost:5000/health',
            'method': 'GET',
            'expected_status': 200,
            'metrics': ['cpu_usage', 'memory_usage', 'response_time'],
            'thresholds': {
                'cpu_usage': 80,
                'memory_usage': 90,
                'response_time': 5000
            }
        },
        'retry_count': 0,
        'status': 'stopped',
        'recovery': {
            'max_attempts': 3,
            'interval': 60,
            'strategy': 'restart'
        }
    },
    'weq': {
        'name': 'WeQ模块',
        'script': ROOT_DIR / 'WeQ/scripts/services/WeQ_start_services.py',
        'args': ['--all'],
        'description': 'WeQ量子纠缠网络模块',
        'process': None,
        'dependencies': ['qsm'],
        'optional_dependencies': [],
        'health_check': {
            'url': 'http://localhost:5003/health',
            'method': 'GET',
            'expected_status': 200,
            'metrics': ['cpu_usage', 'memory_usage', 'response_time', 'entanglement_strength'],
            'thresholds': {
                'cpu_usage': 80,
                'memory_usage': 90,
                'response_time': 5000,
                'entanglement_strength': 0.8
            }
        },
        'retry_count': 0,
        'status': 'stopped',
        'recovery': {
            'max_attempts': 3,
            'interval': 60,
            'strategy': 'restart'
        }
    },
    'som': {
        'name': 'SOM模块',
        'script': ROOT_DIR / 'SOM/scripts/services/SOM_start_services.py',
        'args': ['--all'],
        'description': 'SOM自组织映射模块',
        'process': None,
        'dependencies': ['qsm', 'weq'],
        'optional_dependencies': [],
        'health_check': {
            'url': 'http://localhost:5004/health',
            'method': 'GET',
            'expected_status': 200,
            'metrics': ['cpu_usage', 'memory_usage', 'response_time', 'mapping_quality'],
            'thresholds': {
                'cpu_usage': 80,
                'memory_usage': 90,
                'response_time': 5000,
                'mapping_quality': 0.9
            }
        },
        'retry_count': 0,
        'status': 'stopped',
        'recovery': {
            'max_attempts': 3,
            'interval': 60,
            'strategy': 'restart'
        }
    },
    'ref': {
        'name': 'Ref模块',
        'script': ROOT_DIR / 'Ref/scripts/services/Ref_start_services.py',
        'args': ['--all'],
        'description': '量子基因引用模块',
        'process': None,
        'dependencies': ['qsm', 'weq', 'som'],
        'optional_dependencies': [],
        'services': {
            'project_organizer': {
                'name': '项目组织器',
                'script': ROOT_DIR / 'Ref/scripts/services/project_organizer.py',
                'health_check': {
                    'type': 'file_monitor',
                    'paths': ['project_status.json', '.logs/project_organizer.log']
                }
            },
            'core': {
                'name': 'Ref核心服务',
        'script': ROOT_DIR / 'Ref/ref_core.py',
                'args': ['--daemon']
            },
            'validate': {
                'name': '标记验证服务',
                'script': ROOT_DIR / 'Ref/scripts/validate/validate_service.py',
                'args': ['--daemon', '--interval', '60']
            },
            'optimize': {
                'name': '系统优化服务',
                'script': ROOT_DIR / 'Ref/scripts/optimize/optimize_service.py',
                'args': ['--daemon', '--schedule', 'daily']
            },
            'repair': {
                'name': '模型修复服务',
                'script': ROOT_DIR / 'Ref/scripts/repair/repair_service.py',
                'args': ['--daemon', '--monitor']
            },
            'monitor': {
                'name': '量子基因标记监控',
                'script': ROOT_DIR / 'Ref/monitor/quantum_monitor.py',
                'args': ['--daemon']
            },
            'file_monitor': {
                'name': '文件监管系统',
                'script': ROOT_DIR / 'Ref/monitor/file_monitor.py',
                'args': ['--daemon', '--watch-dirs', 'QSM,WeQ,SOM,Ref']
            }
        },
        'health_check': {
            'url': 'http://localhost:5004/health',
            'method': 'GET',
            'expected_status': 200,
            'metrics': ['cpu_usage', 'memory_usage', 'response_time', 'ref_status'],
            'thresholds': {
                'cpu_usage': 80,
                'memory_usage': 90,
                'response_time': 5000,
                'ref_status': 'healthy'
            }
        },
        'retry_count': 0,
        'status': 'stopped',
        'recovery': {
            'max_attempts': 3,
            'interval': 60,
            'strategy': 'restart'
        }
    }
}

# 服务分组
SERVICE_GROUPS = {
    'qsm': ['qsm'],
    'weq': ['weq'],
    'som': ['som'],
    'ref': ['ref'],
    'all': list(MODULE_SCRIPTS.keys())
}

class ServiceManager:
    """服务管理器类"""
    
    def __init__(self, retry_count: int = 3, health_check_interval: int = 30,
                 log_level: str = 'INFO', log_dir: str = '.logs'):
        self.retry_count = retry_count
        self.health_check_interval = health_check_interval
        self.stop_event = threading.Event()
        self.health_checker = None
        self.recovery_queue = queue.Queue()
        
        # 设置日志
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self._setup_logging(log_level)
        
    def _setup_logging(self, log_level: str):
        """设置日志系统"""
        for module_id in MODULE_SCRIPTS:
            module = MODULE_SCRIPTS[module_id]
            log_file = self.log_dir / f"{module_id}.log"
            
            handler = RotatingFileHandler(
                log_file,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            
            module_logger = logging.getLogger(f"service.{module_id}")
            module_logger.setLevel(getattr(logging, log_level.upper()))
            module_logger.addHandler(handler)
            
    def validate_dependencies(self) -> Tuple[bool, List[str]]:
        """验证服务依赖关系"""
        visited = set()
        temp_visited = set()
        order = []
        
        def visit(module_id: str) -> bool:
            if module_id in temp_visited:
                return False  # 检测到循环依赖
            if module_id in visited:
                return True
                
            temp_visited.add(module_id)
            
            # 检查必需依赖
            for dep in MODULE_SCRIPTS[module_id]['dependencies']:
                if not visit(dep):
        return False
    
            # 检查可选依赖
            for dep in MODULE_SCRIPTS[module_id]['optional_dependencies']:
                if dep in MODULE_SCRIPTS:
                    visit(dep)
                    
            temp_visited.remove(module_id)
            visited.add(module_id)
            order.append(module_id)
            return True
            
        # 验证所有服务的依赖
        for module_id in MODULE_SCRIPTS:
            if not visit(module_id):
                return False, []
                
        return True, order
        
    def start_service(self, module_id: str) -> bool:
        """启动单个服务"""
        module = MODULE_SCRIPTS[module_id]
        module_logger = logging.getLogger(f"service.{module_id}")
        
        try:
            logger.info(f"正在启动服务: {module['name']}")
            
            # 检查依赖
            for dep in module['dependencies']:
                if MODULE_SCRIPTS[dep]['status'] != 'running':
                    logger.error(f"依赖服务未运行: {module['name']} 依赖 {MODULE_SCRIPTS[dep]['name']}")
                    return False
                    
            # 准备环境变量
            env = os.environ.copy()
            env['SERVICE_LOG_DIR'] = str(self.log_dir)
            
            # 启动主服务进程
            cmd = [sys.executable, str(module['script'])] + module['args']
            logger.info(f"执行命令: {' '.join(cmd)}")
        
        process = subprocess.Popen(
            cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                env=env,
                cwd=str(ROOT_DIR)
            )
            
            module['process'] = process
            module['status'] = 'starting'
            logger.info(f"服务进程已启动: {module['name']}, PID: {process.pid}")
            
            # 如果有子服务,启动子服务
            if 'services' in module:
                for service_id, service in module['services'].items():
                    logger.info(f"正在启动子服务: {service['name']}")
                    service_cmd = [sys.executable, str(service['script'])]
                    if 'args' in service:
                        service_cmd.extend(service['args'])
                        
                    service_process = subprocess.Popen(
                        service_cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        universal_newlines=True,
                        env=env,
                        cwd=str(ROOT_DIR)
                    )
                    
                    logger.info(f"子服务进程已启动: {service['name']}, PID: {service_process.pid}")
                    
            # 等待服务启动
            time.sleep(5)
            
            # 检查服务是否成功启动
            health_status = self._check_service_health(module_id)
            if health_status['status']:
                module['status'] = 'running'
                logger.info(f"服务启动成功: {module['name']}")
                logger.info(f"健康检查指标: {health_status['metrics']}")
        return True
            else:
                module['status'] = 'failed'
                logger.error(f"服务启动失败: {module['name']}")
                logger.error(f"健康检查失败原因: {health_status['error']}")
                return False
    
    except Exception as e:
            logger.error(f"启动服务时发生错误: {module['name']}, 错误: {str(e)}")
            module['status'] = 'failed'
        return False

    def _check_service_health(self, module_id: str) -> Dict:
        """检查服务健康状态"""
        module = MODULE_SCRIPTS[module_id]
        try:
            health_check = module['health_check']
            response = requests.request(
                method=health_check['method'],
                url=health_check['url'],
                timeout=5
            )
            
            if response.status_code != health_check['expected_status']:
                return {
                    'status': False,
                    'error': f"状态码不匹配: {response.status_code}",
                    'metrics': {}
                }
                
            # 解析健康检查指标
            metrics = response.json()
            for metric in health_check['metrics']:
                if metric in metrics:
                    value = metrics[metric]
                    threshold = health_check['thresholds'].get(metric)
                    if threshold is not None and value > threshold:
                        return {
                            'status': False,
                            'error': f"指标 {metric} 超过阈值: {value} > {threshold}",
                            'metrics': metrics
                        }
                        
            return {
                'status': True,
                'error': None,
                'metrics': metrics
            }
            
        except Exception as e:
            return {
                'status': False,
                'error': str(e),
                'metrics': {}
            }
            
    def start_services(self, services: List[str], parallel: bool = False):
        """启动多个服务"""
        logger.info(f"开始启动服务: {', '.join(services)}")
        
        # 验证依赖关系
        valid, order = self.validate_dependencies()
        if not valid:
            logger.error("检测到循环依赖，无法启动服务")
            return
            
        # 过滤要启动的服务
        services_to_start = [s for s in order if s in services]
        logger.info(f"服务启动顺序: {', '.join(services_to_start)}")
        
        if parallel:
            # 按依赖层次并行启动
            layers = self._get_dependency_layers(services_to_start)
            for i, layer in enumerate(layers):
                logger.info(f"正在启动第 {i+1} 层服务: {', '.join(layer)}")
                threads = []
                for service in layer:
        thread = threading.Thread(
                        target=self._start_service_with_retry,
                        args=(service,)
        )
        threads.append(thread)
        thread.start()
    
                for thread in threads:
                    thread.join()
        else:
            # 按顺序启动
            for service in services_to_start:
                logger.info(f"正在启动服务: {service}")
                self._start_service_with_retry(service)
                
        # 启动健康检查和恢复管理
        self.start_health_check()
        self.start_recovery_manager()
        
        # 输出启动结果
        running_services = [s for s in services_to_start if MODULE_SCRIPTS[s]['status'] == 'running']
        failed_services = [s for s in services_to_start if MODULE_SCRIPTS[s]['status'] == 'failed']
        
        logger.info("服务启动完成:")
        logger.info(f"成功: {len(running_services)} 个 - {', '.join(running_services)}")
        if failed_services:
            logger.error(f"失败: {len(failed_services)} 个 - {', '.join(failed_services)}")
        
    def _get_dependency_layers(self, services: List[str]) -> List[List[str]]:
        """获取服务的依赖层次"""
        layers = []
        remaining = set(services)
        
        while remaining:
            layer = set()
            for service in remaining:
                deps = set(MODULE_SCRIPTS[service]['dependencies'])
                if not (deps & remaining):  # 如果没有未处理的依赖
                    layer.add(service)
            layers.append(list(layer))
            remaining -= layer
            
        return layers
        
    def start_recovery_manager(self):
        """启动恢复管理器"""
        def recovery_loop():
            while not self.stop_event.is_set():
                try:
                    module_id = self.recovery_queue.get(timeout=1)
                    module = MODULE_SCRIPTS[module_id]
                    
                    if module['recovery']['max_attempts'] > 0:
                        logger.info(f"尝试恢复服务: {module['name']}")
                        
                        if self._start_service_with_retry(module_id):
                            module['recovery']['max_attempts'] -= 1
                            logger.info(f"服务恢复成功: {module['name']}")
                        else:
                            logger.error(f"服务恢复失败: {module['name']}")
                            
                except queue.Empty:
                    continue
                    
        self.recovery_thread = threading.Thread(target=recovery_loop)
        self.recovery_thread.daemon = True
        self.recovery_thread.start()
        
    def stop_services(self):
        """停止所有服务"""
    logger.info("正在停止所有服务...")
        
        # 停止健康检查和恢复管理
        self.stop_event.set()
        if self.health_checker:
            self.health_checker.stop()
        if hasattr(self, 'recovery_thread'):
            self.recovery_thread.join(timeout=5)
            
        # 按依赖关系的反序停止服务
        _, order = self.validate_dependencies()
        for module_id in reversed(order):
            self.stop_service(module_id)
            
    def stop_service(self, module_id: str):
        """停止单个服务"""
        module = MODULE_SCRIPTS[module_id]
        module_logger = logging.getLogger(f"service.{module_id}")
        
        if module['process']:
            module_logger.info(f"正在停止服务: {module['name']}")
            try:
                module['process'].terminate()
                module['process'].wait(timeout=10)
                module['status'] = 'stopped'
                module_logger.info(f"服务已停止: {module['name']}")
            except subprocess.TimeoutExpired:
                module_logger.warning(f"服务停止超时，强制终止: {module['name']}")
                module['process'].kill()
                module['status'] = 'stopped'
                
    def start_health_check(self):
        """启动健康检查"""
        if not self.health_checker:
            self.health_checker = ServiceHealthCheck(self.health_check_interval)
            self.health_checker.start()
            
    def _start_service_with_retry(self, service: str):
        """带重试的服务启动"""
        module = MODULE_SCRIPTS[service]
        for i in range(self.retry_count):
            if self.start_service(service):
                return
            logger.warning(f"服务启动失败，正在重试({i+1}/{self.retry_count}): {module['name']}")
            time.sleep(5)
            
class ServiceHealthCheck:
    """服务健康检查类"""
    
    def __init__(self, interval: int = 30):
        self.interval = interval
        self.stop_event = threading.Event()
        
    def start(self):
        """启动健康检查线程"""
        self.thread = threading.Thread(target=self._health_check_loop)
        self.thread.daemon = True
        self.thread.start()
        
    def stop(self):
        """停止健康检查"""
        self.stop_event.set()
        self.thread.join(timeout=5)
        
    def _health_check_loop(self):
        """健康检查循环"""
        while not self.stop_event.is_set():
            self._check_all_services()
            time.sleep(self.interval)
            
    def _check_all_services(self):
        """检查所有服务的健康状态"""
        for module_id, module in MODULE_SCRIPTS.items():
            if module['status'] == 'running':
                self._check_service_health(module_id)
                
    def _check_service_health(self, module_id: str):
        """检查单个服务的健康状态"""
        module = MODULE_SCRIPTS[module_id]
        
        # 检查进程是否存活
        if not module['process'] or module['process'].poll() is not None:
            logger.warning(f"服务进程已终止: {module['name']}")
            module['status'] = 'failed'
            return
            
        # 检查健康检查接口
        try:
            health_check = module['health_check']
            response = requests.request(
                method=health_check['method'],
                url=health_check['url'],
                timeout=5
            )
            
            if response.status_code != health_check['expected_status']:
                logger.warning(f"服务健康检查失败: {module['name']}, 状态码: {response.status_code}")
                module['status'] = 'unhealthy'
            else:
                if module['status'] != 'running':
                    logger.info(f"服务恢复正常: {module['name']}")
                    module['status'] = 'running'
                    
        except Exception as e:
            logger.warning(f"服务健康检查异常: {module['name']}, 错误: {str(e)}")
            module['status'] = 'unhealthy'

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='QSM服务管理器')
    parser.add_argument('--parallel', action='store_true', help='并行启动服务')
    parser.add_argument('--services', nargs='+', default=['all'], help='要启动的服务')
    parser.add_argument('--retry', type=int, default=3, help='启动失败重试次数')
    parser.add_argument('--health-check-interval', type=int, default=30, help='健康检查间隔(秒)')
    parser.add_argument('--log-level', default='INFO', help='日志级别')
    parser.add_argument('--log-dir', default='.logs', help='日志目录')
    args = parser.parse_args()
    
    # 解析要启动的服务
    services_to_start = []
    for service in args.services:
        if service in SERVICE_GROUPS:
            services_to_start.extend(SERVICE_GROUPS[service])
    services_to_start = list(dict.fromkeys(services_to_start))  # 去重
    
    # 创建服务管理器
    service_manager = ServiceManager(
        retry_count=args.retry,
        health_check_interval=args.health_check_interval,
        log_level=args.log_level,
        log_dir=args.log_dir
    )
    
    # 注册退出处理
    def cleanup():
        service_manager.stop_services()
        
    atexit.register(cleanup)
    
    try:
        # 启动服务
        logger.info(f"正在启动服务: {', '.join(services_to_start)}")
        service_manager.start_services(services_to_start, args.parallel)
        
        # 等待中断信号
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在停止服务...")
        service_manager.stop_services()

if __name__ == '__main__':
    main()

"""
量子基因编码: QE-SRV-ALL-S7E2R9V2
纠缠状态: 活跃
纠缠对象: ['QSM/scripts/services/QSM_start_services.py', 'WeQ/scripts/services/WeQ_start_services.py',
          'SOM/scripts/services/SOM_start_services.py', 'Ref/scripts/services/Ref_start_services.py']
纠缠强度: 0.98
""" 