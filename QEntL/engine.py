# 
"""
"""
量子基因编码: Q-B9FC-A8B3-7D1D
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
""""""
# 开发团队：中华 ZhoHo ，Claude

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
QEntL引擎模块
提供量子纠缠语言的核心引擎功能
"""

import os
import sys
import json
import time
import logging
import hashlib
import threading
import importlib
import inspect
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
from pathlib import Path
from datetime import datetime
import re
import random

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('qentl_engine.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("QEntL-Engine")

class EntanglementState:
    """量子纠缠状态，表示纠缠对象之间的共享信息状态"""
    
    def __init__(self, channel_id: str):
        """初始化纠缠状态
        
        Args:
            channel_id: 纠缠信道ID
        """
        self.channel_id = channel_id
        self.state_data = {}  # 共享状态数据
        self.last_update = time.time()
        self.observers = []  # 观察此状态的对象
        self.lock = threading.RLock()  # 用于线程安全操作的锁
        self.fidelity = 1.0  # 纠缠保真度，范围0-1
        self.active = True  # 纠缠是否活跃
    
    def update(self, key: str, value: Any) -> bool:
        """更新状态中的特定键值
        
        Args:
            key: 要更新的键
            value: 新值
            
        Returns:
            操作是否成功
        """
        with self.lock:
            try:
                old_value = self.state_data.get(key)
                self.state_data[key] = value
                self.last_update = time.time()
                
                # 通知所有观察者状态变化
                for observer in self.observers:
                    try:
                        observer.on_state_changed(self.channel_id, key, old_value, value)
                    except Exception as e:
                        logger.error(f"通知观察者失败: {e}")
                
                return True
            except Exception as e:
                logger.error(f"更新纠缠状态失败: {e}")
                return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取状态中的值
        
        Args:
            key: 键
            default: 键不存在时的默认值
            
        Returns:
            键对应的值，或默认值
        """
        with self.lock:
            return self.state_data.get(key, default)
    
    def get_all(self) -> Dict[str, Any]:
        """获取完整的状态数据
        
        Returns:
            状态数据字典的副本
        """
        with self.lock:
            return self.state_data.copy()
    
    def add_observer(self, observer) -> bool:
        """添加状态观察者
        
        Args:
            observer: 实现on_state_changed方法的观察者对象
            
        Returns:
            操作是否成功
        """
        with self.lock:
            if observer not in self.observers:
                self.observers.append(observer)
                return True
            return False
    
    def remove_observer(self, observer) -> bool:
        """移除状态观察者
        
        Args:
            observer: 要移除的观察者对象
            
        Returns:
            操作是否成功
        """
        with self.lock:
            if observer in self.observers:
                self.observers.remove(observer)
                return True
            return False
    
    def degrade_fidelity(self, amount: float = 0.01) -> float:
        """降低纠缠保真度，模拟现实中的退相干
        
        Args:
            amount: 降低的幅度
            
        Returns:
            新的保真度
        """
        with self.lock:
            self.fidelity = max(0.0, self.fidelity - amount)
            if self.fidelity < 0.5:
                self.active = False
            return self.fidelity
    
    def is_active(self) -> bool:
        """检查纠缠是否活跃
        
        Returns:
            如果纠缠活跃则为True，否则为False
        """
        return self.active and self.fidelity > 0.5


class EntanglementChannel:
    """量子纠缠通信信道，用于连接多个纠缠对象"""
    
    def __init__(self, channel_id: str, source_object: str, target_objects: List[str]):
        """初始化纠缠信道
        
        Args:
            channel_id: 信道的唯一标识符
            source_object: 源对象的标识符（文件路径或对象ID）
            target_objects: 目标对象标识符列表
        """
        self.channel_id = channel_id
        self.source_object = source_object
        self.target_objects = target_objects
        self.state = EntanglementState(channel_id)
        self.creation_time = time.time()
        self.last_activity = time.time()
        self.bandwidth = 1000  # 每秒可传输的状态更新数
        self.active = True
    
    def add_target(self, target_object: str) -> bool:
        """添加目标对象到信道
        
        Args:
            target_object: 目标对象标识符
            
        Returns:
            操作是否成功
        """
        if target_object not in self.target_objects:
            self.target_objects.append(target_object)
            return True
        return False
    
    def remove_target(self, target_object: str) -> bool:
        """从信道移除目标对象
        
        Args:
            target_object: 目标对象标识符
            
        Returns:
            操作是否成功
        """
        if target_object in self.target_objects:
            self.target_objects.remove(target_object)
            return True
        return False
    
    def update_state(self, key: str, value: Any) -> bool:
        """更新信道状态
        
        Args:
            key: 状态键
            value: 状态值
            
        Returns:
            操作是否成功
        """
        self.last_activity = time.time()
        return self.state.update(key, value)
    
    def get_state(self, key: str, default: Any = None) -> Any:
        """获取信道状态中的特定值
        
        Args:
            key: 状态键
            default: 默认值
            
        Returns:
            状态值
        """
        return self.state.get(key, default)
    
    def close(self) -> bool:
        """关闭信道
        
        Returns:
            操作是否成功
        """
        if self.active:
            self.active = False
            self.state.active = False
            return True
        return False
    
    def is_active(self) -> bool:
        """检查信道是否活跃
        
        Returns:
            如果信道活跃则为True，否则为False
        """
        return self.active and self.state.is_active()


class EntangledObject:
    """表示参与量子纠缠的对象（如文件、模块或资源）"""
    
    def __init__(self, object_id: str, object_type: str = "file"):
        """初始化纠缠对象
        
        Args:
            object_id: 对象的唯一标识符（通常是文件路径）
            object_type: 对象类型（file、module、resource等）
        """
        self.object_id = object_id
        self.object_type = object_type
        self.channels = {}  # 字典，键为信道ID，值为EntanglementChannel对象
        self.last_update = time.time()
        self.metadata = {}
        self.active = True
    
    def add_channel(self, channel: EntanglementChannel) -> bool:
        """将对象关联到信道
        
        Args:
            channel: 纠缠信道对象
            
        Returns:
            操作是否成功
        """
        if channel.channel_id not in self.channels:
            self.channels[channel.channel_id] = channel
            return True
        return False
    
    def remove_channel(self, channel_id: str) -> bool:
        """移除对象与信道的关联
        
        Args:
            channel_id: 信道ID
            
        Returns:
            操作是否成功
        """
        if channel_id in self.channels:
            del self.channels[channel_id]
            return True
        return False
    
    def update_via_channel(self, channel_id: str, key: str, value: Any) -> bool:
        """通过指定信道更新状态
        
        Args:
            channel_id: 信道ID
            key: 状态键
            value: 状态值
            
        Returns:
            操作是否成功
        """
        if channel_id in self.channels and self.channels[channel_id].is_active():
            return self.channels[channel_id].update_state(key, value)
        return False
    
    def get_from_channel(self, channel_id: str, key: str, default: Any = None) -> Any:
        """从指定信道获取状态值
        
        Args:
            channel_id: 信道ID
            key: 状态键
            default: 默认值
            
        Returns:
            状态值
        """
        if channel_id in self.channels and self.channels[channel_id].is_active():
            return self.channels[channel_id].get_state(key, default)
        return default
    
    def has_active_channel(self) -> bool:
        """检查对象是否有活跃的信道
        
        Returns:
            如果有活跃信道则为True，否则为False
        """
        return any(channel.is_active() for channel in self.channels.values())
    
    def on_state_changed(self, channel_id: str, key: str, old_value: Any, new_value: Any):
        """当关联信道状态变化时调用的回调方法
        
        Args:
            channel_id: 信道ID
            key: 状态键
            old_value: 旧值
            new_value: 新值
        """
        # 在子类中实现具体的响应逻辑
        pass


class EntanglementRegistry:
    """管理所有纠缠对象和信道的注册表"""
    
    def __init__(self):
        """初始化注册表"""
        self.objects = {}  # 对象注册表，键为对象ID，值为EntangledObject
        self.channels = {}  # 信道注册表，键为信道ID，值为EntanglementChannel
        self.lock = threading.RLock()
        self.maintenance_thread = None
        self.running = False
    
    def register_object(self, object_id: str, object_type: str = "file") -> EntangledObject:
        """注册一个纠缠对象
        
        Args:
            object_id: 对象ID
            object_type: 对象类型
            
        Returns:
            创建的EntangledObject对象
        """
        with self.lock:
            if object_id not in self.objects:
                obj = EntangledObject(object_id, object_type)
                self.objects[object_id] = obj
                logger.info(f"已注册纠缠对象: {object_id} (类型: {object_type})")
                return obj
            return self.objects[object_id]
    
    def unregister_object(self, object_id: str) -> bool:
        """注销一个纠缠对象
        
        Args:
            object_id: 对象ID
            
        Returns:
            操作是否成功
        """
        with self.lock:
            if object_id in self.objects:
                # 移除所有关联的信道
                for channel_id in list(self.objects[object_id].channels.keys()):
                    self.remove_channel(channel_id)
                
                # 移除对象
                del self.objects[object_id]
                logger.info(f"已注销纠缠对象: {object_id}")
                return True
            return False
    
    def create_channel(self, source_id: str, target_ids: List[str]) -> Optional[str]:
        """创建一个新的纠缠信道
        
        Args:
            source_id: 源对象ID
            target_ids: 目标对象ID列表
            
        Returns:
            创建的信道ID，失败则返回None
        """
        with self.lock:
            # 确保所有对象都已注册
            if source_id not in self.objects:
                self.register_object(source_id)
            
            for target_id in target_ids:
                if target_id not in self.objects:
                    self.register_object(target_id)
            
            # 创建唯一的信道ID
            channel_id = self._generate_channel_id(source_id, target_ids)
            
            # 创建信道对象
            channel = EntanglementChannel(channel_id, source_id, target_ids)
            self.channels[channel_id] = channel
            
            # 将信道关联到所有参与对象
            self.objects[source_id].add_channel(channel)
            for target_id in target_ids:
                self.objects[target_id].add_channel(channel)
            
            logger.info(f"已创建纠缠信道: {channel_id} (源: {source_id}, 目标: {target_ids})")
            return channel_id
    
    def remove_channel(self, channel_id: str) -> bool:
        """移除纠缠信道
        
        Args:
            channel_id: 信道ID
            
        Returns:
            操作是否成功
        """
        with self.lock:
            if channel_id in self.channels:
                channel = self.channels[channel_id]
                
                # 从所有参与对象中移除信道引用
                for object_id in [channel.source_object] + channel.target_objects:
                    if object_id in self.objects:
                        self.objects[object_id].remove_channel(channel_id)
                
                # 关闭信道
                channel.close()
                
                # 从注册表中移除
                del self.channels[channel_id]
                logger.info(f"已移除纠缠信道: {channel_id}")
                return True
            return False
    
    def get_object(self, object_id: str) -> Optional[EntangledObject]:
        """获取纠缠对象
        
        Args:
            object_id: 对象ID
            
        Returns:
            EntangledObject对象，不存在则返回None
        """
        return self.objects.get(object_id)
    
    def get_channel(self, channel_id: str) -> Optional[EntanglementChannel]:
        """获取纠缠信道
        
        Args:
            channel_id: 信道ID
            
        Returns:
            EntanglementChannel对象，不存在则返回None
        """
        return self.channels.get(channel_id)
    
    def update_state(self, source_id: str, key: str, value: Any) -> List[str]:
        """从源对象更新状态到所有连接的信道
        
        Args:
            source_id: 源对象ID
            key: 状态键
            value: 状态值
            
        Returns:
            更新成功的信道ID列表
        """
        with self.lock:
            if source_id not in self.objects:
                return []
            
            source_obj = self.objects[source_id]
            successful_channels = []
            
            for channel_id, channel in source_obj.channels.items():
                if channel.source_object == source_id and channel.is_active():
                    if channel.update_state(key, value):
                        successful_channels.append(channel_id)
            
            return successful_channels
    
    def start(self):
        """启动注册表维护线程"""
        if not self.running:
            self.running = True
            self.maintenance_thread = threading.Thread(
                target=self._maintenance_loop,
                name="EntanglementMaintenanceThread",
                daemon=True
            )
            self.maintenance_thread.start()
            logger.info("已启动纠缠注册表维护线程")
    
    def stop(self):
        """停止注册表维护线程"""
        if self.running:
            self.running = False
            if self.maintenance_thread:
                self.maintenance_thread.join(timeout=5)
            logger.info("已停止纠缠注册表维护线程")
    
    def _maintenance_loop(self):
        """维护循环，定期检查和清理无效信道和对象"""
        maintenance_interval = 300  # 每5分钟
        
        while self.running:
            try:
                time.sleep(maintenance_interval)
                
                with self.lock:
                    # 检查并清理无效信道
                    inactive_channels = [
                        channel_id for channel_id, channel in self.channels.items()
                        if not channel.is_active()
                    ]
                    
                    for channel_id in inactive_channels:
                        self.remove_channel(channel_id)
                    
                    # 检查并清理无有效信道的对象
                    inactive_objects = [
                        object_id for object_id, obj in self.objects.items()
                        if not obj.has_active_channel()
                    ]
                    
                    for object_id in inactive_objects:
                        self.unregister_object(object_id)
                    
                    logger.info(f"维护运行完成: 移除了 {len(inactive_channels)} 个无效信道和 {len(inactive_objects)} 个无效对象")
                
            except Exception as e:
                logger.error(f"维护过程中出错: {e}")
    
    def _generate_channel_id(self, source_id: str, target_ids: List[str]) -> str:
        """生成唯一的信道ID
        
        Args:
            source_id: 源对象ID
            target_ids: 目标对象ID列表
            
        Returns:
            唯一的信道ID
        """
        combined = source_id + ":" + ",".join(sorted(target_ids))
        timestamp = int(time.time())
        hash_base = f"{combined}-{timestamp}"
        channel_hash = hashlib.md5(hash_base.encode()).hexdigest()[:12]
        return f"qent-channel-{channel_hash}"


class QEntLEngine:
    """QEntL量子纠缠引擎"""
    
    def __init__(self):
        """初始化QEntL引擎"""
        self.running = False
        self.registered_files = {}  # 注册的文件 {file_path: file_info}
        self.entanglement_graph = {}  # 纠缠图 {file_path: [entangled_files]}
        self.state_cache = {}  # 文件状态缓存 {file_path: state_hash}
        self.lock = threading.RLock()
        self.monitor_thread = None
        self.callbacks = {
            'file_changed': [],  # 文件变化的回调函数
            'propagation': []    # 状态传播的回调函数
        }
    
    def start(self):
        """启动QEntL引擎"""
        with self.lock:
            if self.running:
                logger.info("QEntL引擎已经在运行")
                return
            
            self.running = True
            logger.info("QEntL引擎启动")
            
            # 启动监控线程
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
    
    def stop(self):
        """停止QEntL引擎"""
        with self.lock:
            if not self.running:
                logger.info("QEntL引擎已经停止")
                return
            
            self.running = False
            logger.info("QEntL引擎停止")
            
            # 等待监控线程结束
            if self.monitor_thread and self.monitor_thread.is_alive():
                self.monitor_thread.join(timeout=2)
    
    def register_file(self, file_path: str) -> Dict[str, Any]:
        """注册文件到引擎
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件信息字典
        """
        with self.lock:
            # 检查文件是否存在
            if not os.path.isfile(file_path):
                logger.error(f"注册文件失败: 文件不存在 - {file_path}")
                return {"success": False, "error": "文件不存在"}
            
            # 读取文件内容
            try:
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
            except Exception as e:
                logger.error(f"注册文件失败: 无法读取文件 - {file_path}, {str(e)}")
                return {"success": False, "error": f"无法读取文件: {str(e)}"}
            
            # 提取量子基因信息
            gene_info = self._extract_gene_info(content)
            
            # 如果没有量子基因编码，则跳过
            if not gene_info.get('gene_code'):
                logger.warning(f"跳过注册: 文件没有量子基因编码 - {file_path}")
                return {"success": False, "error": "文件没有量子基因编码"}
            
            # 计算文件状态哈希
            state_hash = self._calculate_state_hash(content)
            
            # 注册文件
            file_info = {
                'path': file_path,
                'gene_code': gene_info.get('gene_code'),
                'entanglement_state': gene_info.get('entanglement_state', '潜伏'),
                'entangled_objects': gene_info.get('entangled_objects', []),
                'entanglement_strength': gene_info.get('entanglement_strength', 0.95),
                'last_updated': time.time(),
                'state_hash': state_hash
            }
            
            self.registered_files[file_path] = file_info
            self.state_cache[file_path] = state_hash
            
            # 更新纠缠图
            self._update_entanglement_graph(file_path, file_info['entangled_objects'])
            
            logger.info(f"文件注册成功: {file_path} (基因编码: {file_info['gene_code']})")
            return {"success": True, "file_info": file_info}
    
    def unregister_file(self, file_path: str) -> bool:
        """取消注册文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            如果成功取消注册则返回True，否则返回False
        """
        with self.lock:
            if file_path in self.registered_files:
                # 从纠缠图中移除
                self._remove_from_entanglement_graph(file_path)
                
                # 删除文件信息
                del self.registered_files[file_path]
                
                # 删除状态缓存
                if file_path in self.state_cache:
                    del self.state_cache[file_path]
                
                logger.info(f"文件取消注册: {file_path}")
                return True
            else:
                logger.warning(f"取消注册失败: 文件未注册 - {file_path}")
                return False
    
    def update_file_state(self, file_path: str, content: str = None) -> Dict[str, Any]:
        """更新文件状态
        
        Args:
            file_path: 文件路径
            content: 文件内容，如果为None则读取文件
            
        Returns:
            更新结果字典
        """
        with self.lock:
            # 检查文件是否注册
            if file_path not in self.registered_files:
                logger.warning(f"更新状态失败: 文件未注册 - {file_path}")
                return {"success": False, "error": "文件未注册"}
            
            # 如果没有提供内容，则读取文件
            if content is None:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                        content = f.read()
                except Exception as e:
                    logger.error(f"更新状态失败: 无法读取文件 - {file_path}, {str(e)}")
                    return {"success": False, "error": f"无法读取文件: {str(e)}"}
            
            # 计算新的状态哈希
            new_state_hash = self._calculate_state_hash(content)
            old_state_hash = self.state_cache.get(file_path)
            
            # 如果状态没有变化，则跳过
            if new_state_hash == old_state_hash:
                return {"success": True, "changed": False}
            
            # 提取量子基因信息
            gene_info = self._extract_gene_info(content)
            
            # 更新文件信息
            self.registered_files[file_path].update({
                'entanglement_state': gene_info.get('entanglement_state', self.registered_files[file_path]['entanglement_state']),
                'entangled_objects': gene_info.get('entangled_objects', self.registered_files[file_path]['entangled_objects']),
                'entanglement_strength': gene_info.get('entanglement_strength', self.registered_files[file_path]['entanglement_strength']),
                'last_updated': time.time(),
                'state_hash': new_state_hash
            })
            
            # 更新状态缓存
            self.state_cache[file_path] = new_state_hash
            
            # 更新纠缠图
            self._update_entanglement_graph(file_path, self.registered_files[file_path]['entangled_objects'])
            
            # 触发文件变化回调
            self._trigger_callbacks('file_changed', file_path, new_state_hash, old_state_hash)
            
            # 传播状态变化
            propagation_result = self._propagate_state_change(file_path)
            
            logger.info(f"文件状态已更新: {file_path}")
            return {
                "success": True, 
                "changed": True,
                "propagation": propagation_result
            }
    
    def get_file_state(self, file_path: str) -> Dict[str, Any]:
        """获取文件状态
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件状态字典
        """
        with self.lock:
            if file_path in self.registered_files:
                return {
                    "success": True,
                    "file_info": self.registered_files[file_path]
                }
            else:
                return {"success": False, "error": "文件未注册"}
    
    def add_callback(self, event_type: str, callback):
        """添加回调函数
        
        Args:
            event_type: 事件类型，'file_changed'或'propagation'
            callback: 回调函数
        """
        with self.lock:
            if event_type in self.callbacks:
                if callback not in self.callbacks[event_type]:
                    self.callbacks[event_type].append(callback)
                    logger.debug(f"已添加{event_type}回调函数: {callback.__name__ if hasattr(callback, '__name__') else str(callback)}")
    
    def remove_callback(self, event_type: str, callback):
        """移除回调函数
        
        Args:
            event_type: 事件类型，'file_changed'或'propagation'
            callback: 回调函数
        """
        with self.lock:
            if event_type in self.callbacks and callback in self.callbacks[event_type]:
                self.callbacks[event_type].remove(callback)
                logger.debug(f"已移除{event_type}回调函数: {callback.__name__ if hasattr(callback, '__name__') else str(callback)}")
    
    def scan_directory(self, directory: str, recursive: bool = True) -> Dict[str, Any]:
        """扫描目录并注册文件
        
        Args:
            directory: 目录路径
            recursive: 是否递归扫描子目录
            
        Returns:
            扫描结果字典
        """
        result = {
            'total_files': 0,
            'registered_files': 0,
            'skipped_files': 0,
            'errors': 0
        }
        
        # 构建glob模式
        pattern = '**/*' if recursive else '*'
        
        # 扫描目录
        for path in Path(directory).glob(pattern):
            if not path.is_file():
                continue
            
            result['total_files'] += 1
            
            # 注册文件
            reg_result = self.register_file(str(path))
            if reg_result.get('success'):
                result['registered_files'] += 1
            else:
                error = reg_result.get('error', '')
                if error == "文件没有量子基因编码":
                    result['skipped_files'] += 1
                else:
                    result['errors'] += 1
        
        return result
    
    def _extract_gene_info(self, content: str) -> Dict[str, Any]:
        """从文件内容中提取量子基因信息
        
        Args:
            content: 文件内容
            
        Returns:
            包含量子基因信息的字典
        """
        gene_info = {}
        
        # 提取量子基因编码
        gene_code_match = re.search(r'
"""
"""
量子基因编码: Q-B9FC-A8B3-7D1D
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
""""""
        if strength_match:
            gene_info['entanglement_strength'] = float(strength_match.group(1))
        
        return gene_info
    
    def _update_entanglement_graph(self, file_path: str, entangled_objects: List[str]):
        """更新纠缠图
        
        Args:
            file_path: 文件路径
            entangled_objects: 纠缠对象列表
        """
        # 初始化文件的纠缠关系
        if file_path not in self.entanglement_graph:
            self.entanglement_graph[file_path] = set()
        
        # 清除现有的纠缠关系
        old_entangled = set(self.entanglement_graph[file_path])
        
        # 查找匹配的文件
        new_entangled = set()
        for obj in entangled_objects:
            # 在已注册的文件中查找匹配的文件
            for path, info in self.registered_files.items():
                if path == file_path:
                    continue
                
                # 检查文件名是否匹配纠缠对象
                if (obj in path or 
                    Path(path).stem == obj or 
                    os.path.basename(path) == obj or
                    any(part == obj for part in Path(path).parts)):
                    new_entangled.add(path)
        
        # 更新纠缠图
        self.entanglement_graph[file_path] = new_entangled
        
        # 对于不再纠缠的文件，从它们的纠缠关系中移除当前文件
        for path in old_entangled - new_entangled:
            if path in self.entanglement_graph:
                self.entanglement_graph[path].discard(file_path)
        
        # 对于新纠缠的文件，添加当前文件到它们的纠缠关系中
        for path in new_entangled - old_entangled:
            if path not in self.entanglement_graph:
                self.entanglement_graph[path] = set()
            self.entanglement_graph[path].add(file_path)
    
    def _remove_from_entanglement_graph(self, file_path: str):
        """从纠缠图中移除文件
        
        Args:
            file_path: 文件路径
        """
        # 对于所有与该文件纠缠的文件，移除该文件
        if file_path in self.entanglement_graph:
            for path in self.entanglement_graph[file_path]:
                if path in self.entanglement_graph:
                    self.entanglement_graph[path].discard(file_path)
            
            # 删除该文件的纠缠关系
            del self.entanglement_graph[file_path]
    
    def _propagate_state_change(self, source_file: str) -> Dict[str, Any]:
        """传播状态变化
        
        Args:
            source_file: 源文件路径
            
        Returns:
            传播结果字典
        """
        if source_file not in self.registered_files:
            return {"propagated": 0}
        
        source_info = self.registered_files[source_file]
        propagated = set()
        to_propagate = {source_file}
        
        # 广度优先搜索传播状态变化
        while to_propagate:
            current = to_propagate.pop()
            
            # 跳过已处理的文件
            if current in propagated:
                continue
            
            propagated.add(current)
            
            # 获取当前文件的纠缠强度
            current_strength = self.registered_files.get(current, {}).get('entanglement_strength', 0.95)
            
            # 获取与当前文件纠缠的文件
            entangled_files = self.entanglement_graph.get(current, set())
            
            for file_path in entangled_files:
                # 跳过已处理的文件和源文件
                if file_path in propagated or file_path == source_file:
                    continue
                
                # 获取纠缠文件的信息
                file_info = self.registered_files.get(file_path)
                if not file_info:
                    continue
                
                # 根据纠缠强度决定是否传播
                file_strength = file_info.get('entanglement_strength', 0.95)
                
                # 计算传播概率
                prop_probability = current_strength * file_strength
                
                # 如果文件纠缠态为活跃或概率高，则传播
                if (file_info.get('entanglement_state') == '活跃' or 
                    random.random() < prop_probability):
                    # 添加到要传播的文件列表
                    to_propagate.add(file_path)
                    
                    # 触发传播回调
                    self._trigger_callbacks('propagation', current, file_path, prop_probability)
        
        # 返回传播结果
        return {
            "propagated": len(propagated) - 1,  # 不包括源文件
            "affected_files": list(propagated - {source_file})
        }
    
    def _monitor_loop(self):
        """监控循环，定期检查注册文件的状态"""
        while self.running:
            try:
                # 复制注册文件列表，避免在遍历过程中修改
                paths = list(self.registered_files.keys())
                
                for file_path in paths:
                    # 如果文件不存在，则取消注册
                    if not os.path.isfile(file_path):
                        with self.lock:
                            self.unregister_file(file_path)
                        continue
                    
                    # 读取文件内容
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                            content = f.read()
                        
                        # 更新文件状态
                        with self.lock:
                            self.update_file_state(file_path, content)
                    
                    except Exception as e:
                        logger.error(f"监控文件时出错: {file_path}, {str(e)}")
                
                # 休眠一段时间
                time.sleep(5)
            
            except Exception as e:
                logger.error(f"监控循环异常: {str(e)}")
                time.sleep(10)  # 如果出错，等待更长时间
    
    def _trigger_callbacks(self, event_type: str, *args, **kwargs):
        """触发回调函数
        
        Args:
            event_type: 事件类型
            *args, **kwargs: 传递给回调函数的参数
        """
        callbacks = self.callbacks.get(event_type, [])
        for callback in callbacks:
            try:
                callback(*args, **kwargs)
            except Exception as e:
                logger.error(f"触发回调函数出错: {callback.__name__ if hasattr(callback, '__name__') else str(callback)}, {str(e)}")

# 创建全局单例
_qentl_engine = None

def get_qentl_engine() -> QEntLEngine:
    """获取QEntL引擎单例
    
    Returns:
        QEntL引擎实例
    """
    global _qentl_engine
    
    if _qentl_engine is None:
        _qentl_engine = QEntLEngine()
    
    return _qentl_engine

def register_file(file_path: str) -> bool:
    """注册文件到QEntL引擎的便捷函数
    
    Args:
        file_path: 文件路径
        
    Returns:
        操作是否成功
    """
    engine = get_qentl_engine()
    if not engine.running:
        engine.start()
    
    return engine.register_file(file_path)

def update_file_state(file_path: str, key: str, value: Any) -> bool:
    """更新文件状态的便捷函数
    
    Args:
        file_path: 文件路径
        key: 状态键
        value: 状态值
        
    Returns:
        操作是否成功
    """
    engine = get_qentl_engine()
    if not engine.running:
        engine.start()
    
    return engine.update_file_state(file_path, key, value)

def get_file_state(file_path: str, key: str, default: Any = None) -> Any:
    """获取文件状态的便捷函数
    
    Args:
        file_path: 文件路径
        key: 状态键
        default: 默认值
        
    Returns:
        状态值
    """
    engine = get_qentl_engine()
    if not engine.running:
        engine.start()
    
    return engine.get_file_state(file_path, key, default)

# 如果作为主程序运行
if __name__ == "__main__":
    print("启动QEntL引擎...")
    engine = get_qentl_engine()
    engine.start()
    
    # 扫描当前目录
    print("扫描当前目录...")
    result = engine.scan_directory(".")
    print(f"扫描完成: 已注册 {result['registered_files']} 个文件，跳过 {result['skipped_files']} 个文件")
    
    # 保持运行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("正在停止QEntL引擎...")
        engine.stop()
        print("已停止。") 