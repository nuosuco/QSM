#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
项目自动归类与管理系统
功能：
1. 自动归类文件到合适的目录
2. 监控项目性能，防止系统卡顿
3. 智能搜索文件
4. 自动备份修改的文件
"""

import os
import shutil
import json
import time
import re
import logging
import hashlib
import psutil
from datetime import datetime
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
import queue

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('project_manager.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('项目管理系统')

# 项目配置
CONFIG_FILE = 'project_config.json'
DEFAULT_CONFIG = {
    # 文件类型分类规则
    'file_categories': {
        'python_files': ['.py'],
        'javascript_files': ['.js', '.jsx', '.ts', '.tsx'],
        'html_files': ['.html', '.htm'],
        'css_files': ['.css', '.scss', '.sass'],
        'data_files': ['.json', '.csv', '.xml', '.yaml', '.yml'],
        'documentation': ['.md', '.txt', '.pdf', '.docx'],
        'images': ['.jpg', '.jpeg', '.png', '.gif', '.svg'],
        'config_files': ['.ini', '.conf', '.cfg', '.toml'],
        'log_files': ['.log'],
        'binary_files': ['.pkl', '.bin', '.dat'],
    },
    
    # 目录结构定义
    'directory_structure': {
        'src': ['python_files', 'javascript_files'],
        'data': ['data_files', 'binary_files'],
        'docs': ['documentation'],
        'static': ['images', 'css_files', 'html_files'],
        'config': ['config_files'],
        'logs': ['log_files'],
    },
    
    # 备份设置
    'backup': {
        'enabled': True,
        'backup_dir': 'backups',
        'auto_backup_interval': 3600,  # 每小时自动备份一次
        'keep_versions': 5,  # 保留最近5个版本
    },
    
    # 性能监控设置
    'performance': {
        'cpu_threshold': 80,  # CPU使用率达到80%时警告
        'memory_threshold': 80,  # 内存使用率达到80%时警告
        'disk_threshold': 90,  # 磁盘使用率达到90%时警告
        'check_interval': 60,  # 每分钟检查一次
    },
    
    # 索引设置
    'indexing': {
        'enabled': True,
        'rebuild_interval': 3600,  # 每小时重建一次索引
        'exclude_patterns': [
            '.*/__pycache__/.*',
<<<<<<< HEAD
            '.*///.git/.*',
            '.*/node_modules/.*',
            '.*/env/.*',
            '.*/venv/.*',
            '.*///.vscode/.*',
            '.*///.idea/.*',
=======
            '.*/\\.git/.*',
            '.*/node_modules/.*',
            '.*/env/.*',
            '.*/venv/.*',
            '.*/\\.vscode/.*',
            '.*/\\.idea/.*',
>>>>>>> c8ee4fc6e39ad3985ce941a8efbcb072b6ba0eea
            '.*/backups/.*',
            '.*\\.log$',
            '.*\\.tmp$',
        ]
    },
    
    # 自动整理设置
    'auto_organize': {
        'enabled': True,
        'organize_on_startup': True,
        'organize_interval': 86400,  # 每天自动整理一次
    }
}

class ProjectManager:
    def __init__(self, project_root='.'):
        self.project_root = Path(project_root).absolute()
        self.config = self.load_config()
        self.file_index = {}
        self.backup_queue = queue.Queue()
        
        # 创建所需目录
        self.create_directory_structure()
        
        # 初始化子系统
        self.backup_system = BackupSystem(self)
        self.indexing_system = IndexingSystem(self)
        self.performance_monitor = PerformanceMonitor(self)
        self.file_organizer = FileOrganizer(self)
        
    def load_config(self):
        """加载配置文件，如果不存在则创建默认配置"""
        config_path = self.project_root / CONFIG_FILE
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                logger.info(f"已加载配置文件: {config_path}")
                return config
            except Exception as e:
                logger.error(f"加载配置文件失败: {e}")
                
        # 创建默认配置
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_CONFIG, f, indent=4, ensure_ascii=False)
        logger.info(f"已创建默认配置文件: {config_path}")
        return DEFAULT_CONFIG
    
    def save_config(self):
        """保存配置到文件"""
        config_path = self.project_root / CONFIG_FILE
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)
        logger.info(f"已保存配置文件: {config_path}")
    
    def create_directory_structure(self):
        """创建目录结构"""
        for dir_name in self.config['directory_structure']:
            dir_path = self.project_root / dir_name
            if not dir_path.exists():
                dir_path.mkdir(parents=True)
                logger.info(f"已创建目录: {dir_path}")
        
        # 创建备份目录
        backup_dir = self.project_root / self.config['backup']['backup_dir']
        if not backup_dir.exists():
            backup_dir.mkdir(parents=True)
            logger.info(f"已创建备份目录: {backup_dir}")
    
    def start(self):
        """启动所有系统"""
        # 如果配置了启动时自动整理，则执行
        if self.config['auto_organize']['enabled'] and self.config['auto_organize']['organize_on_startup']:
            self.file_organizer.organize_files()
        
        # 构建初始索引
        if self.config['indexing']['enabled']:
            self.indexing_system.build_index()
            
        # 启动文件监控
        self.start_file_monitoring()
        
        # 启动性能监控
        self.performance_monitor.start()
        
        # 启动备份系统
        self.backup_system.start()
        
        logger.info("项目管理系统已启动")
    
    def start_file_monitoring(self):
        """启动文件系统监控"""
        event_handler = FileChangeHandler(self)
        observer = Observer()
        observer.schedule(event_handler, str(self.project_root), recursive=True)
        observer.start()
        logger.info("文件监控系统已启动")
        return observer
    
    def find_file(self, query):
        """搜索文件"""
        return self.indexing_system.search(query)

    def backup_file(self, file_path):
        """将文件加入备份队列"""
        self.backup_queue.put(file_path)
    
    def stop(self):
        """停止所有系统"""
        self.performance_monitor.stop()
        self.backup_system.stop()
        # 保存索引
        self.indexing_system.save_index()
        logger.info("项目管理系统已停止")


class BackupSystem:
    def __init__(self, manager):
        self.manager = manager
        self.running = False
        self.thread = None
    
    def start(self):
        """启动备份系统"""
        if not self.manager.config['backup']['enabled']:
            logger.info("备份系统已禁用")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self.backup_worker)
        self.thread.daemon = True
        self.thread.start()
        logger.info("备份系统已启动")
        
        # 启动定时备份
        self.schedule_auto_backup()
    
    def backup_worker(self):
        """处理备份队列的工作线程"""
        while self.running:
            try:
                file_path = self.manager.backup_queue.get(timeout=1)
                self.backup_single_file(file_path)
                self.manager.backup_queue.task_done()
            except queue.Empty:
                pass
            except Exception as e:
                logger.error(f"备份文件时发生错误: {e}")
    
    def backup_single_file(self, file_path):
        """备份单个文件"""
        try:
            rel_path = os.path.relpath(file_path, self.manager.project_root)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 创建备份文件路径
            backup_root = self.manager.project_root / self.manager.config['backup']['backup_dir']
            backup_dir = backup_root / timestamp
            if not backup_dir.exists():
                backup_dir.mkdir(parents=True)
            
            backup_file_dir = backup_dir / os.path.dirname(rel_path)
            if not backup_file_dir.exists():
                backup_file_dir.mkdir(parents=True)
            
            backup_file_path = backup_dir / rel_path
            
            # 复制文件
            shutil.copy2(file_path, backup_file_path)
            logger.info(f"已备份文件: {file_path} -> {backup_file_path}")
            
            # 清理过期备份
            self.cleanup_old_backups()
        except Exception as e:
            logger.error(f"备份文件失败 {file_path}: {e}")
    
    def cleanup_old_backups(self):
        """清理过期的备份，保留指定数量的最新备份"""
        try:
            backup_root = self.manager.project_root / self.manager.config['backup']['backup_dir']
            backups = sorted([d for d in backup_root.iterdir() if d.is_dir()])
            
            keep_versions = self.manager.config['backup']['keep_versions']
            if len(backups) > keep_versions:
                for old_backup in backups[:-keep_versions]:
                    shutil.rmtree(old_backup)
                    logger.info(f"已删除过期备份: {old_backup}")
        except Exception as e:
            logger.error(f"清理旧备份失败: {e}")
    
    def schedule_auto_backup(self):
        """计划自动备份任务"""
        if not self.running:
            return
            
        # 创建完整项目备份
        self.create_full_backup()
        
        # 计划下次备份
        interval = self.manager.config['backup']['auto_backup_interval']
        threading.Timer(interval, self.schedule_auto_backup).start()
    
    def create_full_backup(self):
        """创建完整项目备份"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_root = self.manager.project_root / self.manager.config['backup']['backup_dir']
            backup_dir = backup_root / f"full_{timestamp}"
            
            # 要排除的目录
            exclude_patterns = self.manager.config['indexing']['exclude_patterns']
            exclude_dirs = [self.manager.config['backup']['backup_dir']]
            
            # 复制文件
            for root, dirs, files in os.walk(self.manager.project_root):
                # 排除特定目录
                dirs[:] = [d for d in dirs if not any(re.match(pattern, os.path.join(root, d)) for pattern in exclude_patterns) and d not in exclude_dirs]
                
                rel_path = os.path.relpath(root, self.manager.project_root)
                backup_path = backup_dir / rel_path
                
                if not backup_path.exists() and rel_path != '.':
                    backup_path.mkdir(parents=True)
                
                for file in files:
                    src_file = Path(root) / file
                    if not any(re.match(pattern, str(src_file)) for pattern in exclude_patterns):
                        dst_file = backup_path / file
                        shutil.copy2(src_file, dst_file)
            
            logger.info(f"已创建完整项目备份: {backup_dir}")
        except Exception as e:
            logger.error(f"创建完整备份失败: {e}")
    
    def stop(self):
        """停止备份系统"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        logger.info("备份系统已停止")


class IndexingSystem:
    def __init__(self, manager):
        self.manager = manager
        self.index_file = self.manager.project_root / 'file_index.json'
        self.running = False
        self.thread = None
    
    def build_index(self):
        """构建文件索引"""
        try:
            # 如果索引文件存在，先加载
            if self.index_file.exists():
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    self.manager.file_index = json.load(f)
                logger.info(f"已加载索引文件: {self.index_file}")
            
            # 重新扫描文件系统
            new_index = {}
            exclude_patterns = self.manager.config['indexing']['exclude_patterns']
            
            for root, dirs, files in os.walk(self.manager.project_root):
                # 排除特定目录
                dirs[:] = [d for d in dirs if not any(re.match(pattern, os.path.join(root, d)) for pattern in exclude_patterns)]
                
                for file in files:
                    file_path = os.path.join(root, file)
                    if not any(re.match(pattern, file_path) for pattern in exclude_patterns):
                        # 计算相对路径
                        rel_path = os.path.relpath(file_path, self.manager.project_root)
                        
                        # 获取文件信息
                        file_info = {
                            'path': rel_path,
                            'size': os.path.getsize(file_path),
                            'modified': os.path.getmtime(file_path),
                            'extension': os.path.splitext(file)[1].lower(),
                            'category': self.get_file_category(file),
                            'name': file,
                        }
                        
                        # 添加到索引
                        new_index[rel_path] = file_info
            
            # 更新索引
            self.manager.file_index = new_index
            self.save_index()
            logger.info(f"已构建索引，共 {len(new_index)} 个文件")
            
            # 启动定时重建
            self.schedule_index_rebuild()
        except Exception as e:
            logger.error(f"构建索引失败: {e}")
    
    def save_index(self):
        """保存索引到文件"""
        try:
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(self.manager.file_index, f, indent=2)
            logger.info(f"已保存索引到文件: {self.index_file}")
        except Exception as e:
            logger.error(f"保存索引失败: {e}")
    
    def get_file_category(self, filename):
        """根据文件名确定文件类别"""
        ext = os.path.splitext(filename)[1].lower()
        
        for category, extensions in self.manager.config['file_categories'].items():
            if ext in extensions:
                return category
        
        return 'other'
    
    def schedule_index_rebuild(self):
        """计划定时重建索引"""
        if not self.manager.config['indexing']['enabled']:
            return
            
        interval = self.manager.config['indexing']['rebuild_interval']
        threading.Timer(interval, self.build_index).start()
    
    def search(self, query):
        """搜索文件索引"""
        results = []
        query = query.lower()
        
        for file_path, info in self.manager.file_index.items():
            # 按文件名、路径和类别搜索
            if (query in file_path.lower() or 
                query in info['name'].lower() or 
                query in info['category'].lower()):
                results.append(info)
        
        # 按相关性排序
        results.sort(key=lambda x: (
            -self._calculate_relevance(x, query),  # 相关性越高排越前
            -x['modified']  # 最近修改的排前面
        ))
        
        return results[:20]  # 限制返回数量
    
    def _calculate_relevance(self, file_info, query):
        """计算文件与查询的相关性分数"""
        score = 0
        
        # 文件名完全匹配加高分
        if query == file_info['name'].lower():
            score += 100
        # 文件名包含查询词加分
        elif query in file_info['name'].lower():
            score += 50
        
        # 路径包含查询词加分
        if query in file_info['path'].lower():
            score += 30
        
        # 类别匹配加分
        if query in file_info['category'].lower():
            score += 20
        
        return score


class PerformanceMonitor:
    def __init__(self, manager):
        self.manager = manager
        self.running = False
        self.thread = None
    
    def start(self):
        """启动性能监控"""
        self.running = True
        self.thread = threading.Thread(target=self.monitor_loop)
        self.thread.daemon = True
        self.thread.start()
        logger.info("性能监控系统已启动")
    
    def monitor_loop(self):
        """监控循环"""
        while self.running:
            try:
                # 检查系统资源
                cpu_percent = psutil.cpu_percent(interval=1)
                memory_percent = psutil.virtual_memory().percent
                disk_percent = psutil.disk_usage('/').percent
                
                # 记录当前状态
                status = {
                    'cpu': cpu_percent,
                    'memory': memory_percent,
                    'disk': disk_percent,
                    'timestamp': time.time()
                }
                
                # 检查是否超过阈值
                self.check_thresholds(status)
                
                # 等待下次检查
                time.sleep(self.manager.config['performance']['check_interval'])
            except Exception as e:
                logger.error(f"性能监控发生错误: {e}")
                time.sleep(10)  # 出错后等待一段时间再继续
    
    def check_thresholds(self, status):
        """检查资源使用是否超过阈值"""
        # CPU检查
        if status['cpu'] > self.manager.config['performance']['cpu_threshold']:
            logger.warning(f"CPU使用率过高: {status['cpu']}%，超过阈值 {self.manager.config['performance']['cpu_threshold']}%")
            self.take_action('cpu')
        
        # 内存检查
        if status['memory'] > self.manager.config['performance']['memory_threshold']:
            logger.warning(f"内存使用率过高: {status['memory']}%，超过阈值 {self.manager.config['performance']['memory_threshold']}%")
            self.take_action('memory')
        
        # 磁盘检查
        if status['disk'] > self.manager.config['performance']['disk_threshold']:
            logger.warning(f"磁盘使用率过高: {status['disk']}%，超过阈值 {self.manager.config['performance']['disk_threshold']}%")
            self.take_action('disk')
    
    def take_action(self, resource_type):
        """根据资源类型采取相应措施"""
        if resource_type == 'memory':
            # 尝试清理内存
            self.clean_memory()
        elif resource_type == 'disk':
            # 尝试清理磁盘
            self.clean_disk()
    
    def clean_memory(self):
        """清理内存"""
        try:
            # 强制垃圾回收
            import gc
            gc.collect()
            logger.info("已执行内存垃圾回收")
        except Exception as e:
            logger.error(f"内存清理失败: {e}")
    
    def clean_disk(self):
        """清理磁盘空间"""
        try:
            # 清理临时文件
            patterns = ['*.tmp', '*.temp', '*.bak', '~*']
            files_removed = 0
            bytes_freed = 0
            
            for pattern in patterns:
                for root, _, files in os.walk(self.manager.project_root):
                    for file in files:
                        if any(file.endswith(p.replace('*', '')) for p in patterns):
                            file_path = os.path.join(root, file)
                            size = os.path.getsize(file_path)
                            os.remove(file_path)
                            files_removed += 1
                            bytes_freed += size
            
            logger.info(f"磁盘清理：已删除 {files_removed} 个临时文件，释放 {bytes_freed/1024/1024:.2f} MB 空间")
        except Exception as e:
            logger.error(f"磁盘清理失败: {e}")
    
    def stop(self):
        """停止性能监控"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        logger.info("性能监控系统已停止")


class FileOrganizer:
    def __init__(self, manager):
        self.manager = manager
    
    def organize_files(self):
        """整理项目文件"""
        logger.info("开始整理项目文件...")
        
        # 获取所有文件
        files_to_organize = []
        exclude_patterns = self.manager.config['indexing']['exclude_patterns']
        
        for root, dirs, files in os.walk(self.manager.project_root):
            # 排除特定目录
            dirs[:] = [d for d in dirs if not any(re.match(pattern, os.path.join(root, d)) for pattern in exclude_patterns)]
            
            for file in files:
                file_path = os.path.join(root, file)
                if not any(re.match(pattern, file_path) for pattern in exclude_patterns):
                    files_to_organize.append(file_path)
        
        # 根据文件类型整理
        organized_count = 0
        for file_path in files_to_organize:
            if self.organize_file(file_path):
                organized_count += 1
        
        logger.info(f"文件整理完成，共整理 {organized_count} 个文件")
    
    def organize_file(self, file_path):
        """整理单个文件"""
        try:
            # 获取文件类别
            filename = os.path.basename(file_path)
            file_category = self.manager.indexing_system.get_file_category(filename)
            
            # 确定目标目录
            target_dir = None
            for dir_name, categories in self.manager.config['directory_structure'].items():
                if file_category in categories:
                    target_dir = self.manager.project_root / dir_name
                    break
            
            # 如果没有找到对应目录，跳过
            if not target_dir:
                return False
            
            # 检查文件是否已在正确的目录中
            rel_path = os.path.relpath(file_path, self.manager.project_root)
            if rel_path.startswith(os.path.basename(target_dir)):
                return False  # 文件已在正确位置
            
            # 确定新的文件路径
            new_file_path = target_dir / filename
            
            # 如果文件已存在，添加哈希值避免冲突
            if new_file_path.exists():
                file_hash = hashlib.md5(open(file_path, 'rb').read()).hexdigest()[:8]
                base_name, ext = os.path.splitext(filename)
                new_file_path = target_dir / f"{base_name}_{file_hash}{ext}"
            
            # 移动文件前先备份
            self.manager.backup_file(file_path)
            
            # 移动文件
            shutil.move(file_path, new_file_path)
            logger.info(f"已整理文件: {file_path} -> {new_file_path}")
            
            return True
        except Exception as e:
            logger.error(f"整理文件失败 {file_path}: {e}")
            return False


class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, manager):
        self.manager = manager
    
    def on_modified(self, event):
        """文件被修改时的处理"""
        if event.is_directory:
            return
            
        file_path = event.src_path
        # 排除索引文件、配置文件和日志文件
        if file_path.endswith('.json') or file_path.endswith('.log'):
            return
            
        # 备份修改的文件
        self.manager.backup_file(file_path)
    
    def on_created(self, event):
        """文件被创建时的处理"""
        if event.is_directory:
            return
            
        # 检查文件是否需要整理
        if self.manager.config['auto_organize']['enabled']:
            self.manager.file_organizer.organize_file(event.src_path)


if __name__ == "__main__":
    try:
        # 创建和启动管理器
        manager = ProjectManager()
        manager.start()
        
        print("项目管理系统已启动，按Ctrl+C退出...")
        
        # 保持主线程运行
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("正在停止项目管理系统...")
        manager.stop()
        print("已停止，再见！") 

"""

"""
量子基因编码: QE-PRO-5A7C3F40EDE9
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
"""
"""

// 开发团队：中华 ZhoHo ，Claude 
