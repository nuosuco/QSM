#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
量子节点连接器模块
负责量子叠加态模型(QSM)部署时自动建立量子纠缠信道和节点管理
"""

import os
import sys
import time
import json
import uuid
import hashlib
import platform
import socket
import threading
import logging
import random
import requests
from datetime import datetime
from pathlib import Path
import numpy as np

# 添加项目根目录到系统路径
try:
    from quantum_core.quantum_gene.quantum_encoder import QuantumGeneEncoder
    from quantum_core.quantum_gene.quantum_gene_neural_implementation import QuantumGeneNeuralNetwork
except ImportError:
    # 如果在独立环境中运行，尝试相对导入
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
    from quantum_core.quantum_gene.quantum_encoder import QuantumGeneEncoder
    from quantum_core.quantum_gene.quantum_gene_neural_implementation import QuantumGeneNeuralNetwork

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("量子节点连接器")

class QuantumNodeConnector:
    """量子节点连接器，负责自动建立量子纠缠信道和节点管理"""
    
    CENTRAL_REGISTRY_URL = "https://quantum-registry.qsm-central.io/api/v1/nodes"
    ENTANGLEMENT_REFRESH_INTERVAL = 3600  # 秒
    
    def __init__(self, config_path=None):
        """初始化量子节点连接器"""
        self.node_quantum_gene = None
        self.node_info = {}
        self.entanglement_channels = {}
        self.hardware_specs = self._detect_hardware_specs()
        self.quantum_bits = self._calculate_quantum_bits()
        self.geo_position = self._get_geo_position()
        self.config_path = config_path or "config/quantum_node.json"
        self.entanglement_refresh_thread = None
        self.stop_event = threading.Event()
        
        logger.info(f"初始化量子节点连接器，当前量子比特数：{self.quantum_bits}")
    
    def initialize(self):
        """初始化节点并建立量子纠缠信道"""
        # 检查是否已有节点配置
        if os.path.exists(self.config_path):
            self._load_existing_node()
        else:
            self._create_new_node()
        
        # 注册到中央量子纠缠注册中心
        self._register_to_central_registry()
        
        # 获取网络拓扑更新
        self._update_entanglement_topology()
        
        # 建立量子纠缠信道
        self._establish_entanglement_channels()
        
        # 启动周期性刷新线程
        self._start_entanglement_refresh()
        
        logger.info(f"节点初始化完成，量子基因编码：{self.node_quantum_gene}")
        return self.node_quantum_gene
    
    def _detect_hardware_specs(self):
        """检测硬件规格"""
        specs = {
            'platform': platform.system(),
            'processor': platform.processor(),
            'cpu_cores': os.cpu_count(),
            'memory_gb': self._get_memory_size(),
            'gpu_available': self._check_gpu_available(),
            'gpu_memory_gb': self._get_gpu_memory() if self._check_gpu_available() else 0,
            'quantum_processor_available': self._check_quantum_processor(),
            'disk_space_gb': self._get_disk_space(),
            'network_interfaces': self._get_network_interfaces()
        }
        return specs
    
    def _get_memory_size(self):
        """获取系统内存大小(GB)"""
        try:
            import psutil
            return round(psutil.virtual_memory().total / (1024**3), 2)
        except ImportError:
            # 如果psutil不可用，尝试通过其他方式获取
            if platform.system() == 'Windows':
                import ctypes
                kernel32 = ctypes.windll.kernel32
                c_ulong = ctypes.c_ulong
                class MEMORYSTATUS(ctypes.Structure):
                    _fields_ = [
                        ('dwLength', c_ulong),
                        ('dwMemoryLoad', c_ulong),
                        ('dwTotalPhys', c_ulong),
                        ('dwAvailPhys', c_ulong),
                        ('dwTotalPageFile', c_ulong),
                        ('dwAvailPageFile', c_ulong),
                        ('dwTotalVirtual', c_ulong),
                        ('dwAvailVirtual', c_ulong)
                    ]
                memory_status = MEMORYSTATUS()
                memory_status.dwLength = ctypes.sizeof(MEMORYSTATUS)
                kernel32.GlobalMemoryStatus(ctypes.byref(memory_status))
                return round(memory_status.dwTotalPhys / (1024**3), 2)
            else:
                # Linux/Mac简易检测
                try:
                    with open('/proc/meminfo', 'r') as f:
                        for line in f:
                            if 'MemTotal' in line:
                                return round(int(line.split()[1]) / (1024**2), 2)
                except:
                    pass
            return 8.0  # 默认值
    
    def _check_gpu_available(self):
        """检查是否有可用GPU"""
        try:
            # 尝试使用tensorflow检测
            import tensorflow as tf
            gpus = tf.config.list_physical_devices('GPU')
            return len(gpus) > 0
        except:
            try:
                # 尝试使用torch检测
                import torch
                return torch.cuda.is_available()
            except:
                # 如果以上方法都不可用，尝试系统特定方法
                if platform.system() == 'Windows':
                    try:
                        import subprocess
                        result = subprocess.check_output('wmic path win32_VideoController get name', shell=True)
                        return 'NVIDIA' in result.decode() or 'AMD' in result.decode()
                    except:
                        pass
                else:
                    try:
                        import subprocess
                        result = subprocess.check_output('lspci | grep -i nvidia', shell=True)
                        return len(result) > 0
                    except:
                        pass
        return False
    
    def _get_gpu_memory(self):
        """获取GPU显存大小(GB)"""
        try:
            import tensorflow as tf
            gpus = tf.config.list_physical_devices('GPU')
            if not gpus:
                return 0
            
            try:
                gpu_info = tf.config.experimental.get_memory_info(gpus[0])
                return round(gpu_info['total'] / (1024**3), 2)
            except:
                pass
            
            # 如果上述方法失败，尝试使用nvidia-smi命令
            try:
                import subprocess
                result = subprocess.check_output(['nvidia-smi', '--query-gpu=memory.total', '--format=csv,noheader,nounits'])
                memory_values = [int(x) for x in result.decode().strip().split('\n')]
                return sum(memory_values) / 1024  # 转为GB
            except:
                pass
            
            return 4.0  # 默认值
        except:
            return 0
    
    def _check_quantum_processor(self):
        """检查是否有量子处理器"""
        # 这是一个未来功能，目前简单返回False
        # 在未来可以扩展这个函数来检测实际的量子处理器
        return False
    
    def _get_disk_space(self):
        """获取磁盘空间(GB)"""
        try:
            total, used, free = shutil.disk_usage("/")
            return round(total / (1024**3), 2)
        except:
            if platform.system() == 'Windows':
                try:
                    import ctypes
                    free_bytes = ctypes.c_ulonglong(0)
                    ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p("C:\\"), None, None, ctypes.pointer(free_bytes))
                    return round(free_bytes.value / (1024**3), 2)
                except:
                    pass
            return 100.0  # 默认值
    
    def _get_network_interfaces(self):
        """获取网络接口信息"""
        interfaces = []
        try:
            for interface, addrs in socket.getaddrinfo(socket.gethostname(), None):
                interfaces.append(str(addrs[4][0]))
        except:
            pass
        return interfaces
    
    def _calculate_quantum_bits(self):
        """根据硬件规格计算量子比特数"""
        base_qubits = 28  # 基础量子比特数
        
        # CPU核心影响因子
        cpu_factor = min(3.0, self.hardware_specs['cpu_cores'] / 4)
        
        # 内存影响因子
        memory_factor = min(2.5, self.hardware_specs['memory_gb'] / 8)
        
        # GPU/专用硬件影响因子
        gpu_factor = 1.0
        if self.hardware_specs['gpu_available']:
            gpu_factor += min(4.0, self.hardware_specs['gpu_memory_gb'] / 4)
        
        # 量子硬件特殊加成
        quantum_hardware_bonus = 1.0
        if self.hardware_specs['quantum_processor_available']:
            quantum_hardware_bonus = 10.0
        
        # 计算最终量子比特数
        total_qubits = int(base_qubits * cpu_factor * memory_factor * gpu_factor * quantum_hardware_bonus)
        
        # 确保量子比特数在有效范围内
        return max(28, min(8192, total_qubits))
    
    def _get_geo_position(self):
        """获取地理位置信息"""
        geo_info = {
            'latitude': 0.0,
            'longitude': 0.0,
            'country': 'unknown',
            'region': 'unknown',
            'city': 'unknown',
            'isp': 'unknown'
        }
        
        try:
            # 尝试通过IP获取地理位置
            response = requests.get('https://ipinfo.io/json', timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'loc' in data and ',' in data['loc']:
                    geo_info['latitude'], geo_info['longitude'] = map(float, data['loc'].split(','))
                if 'country' in data:
                    geo_info['country'] = data['country']
                if 'region' in data:
                    geo_info['region'] = data['region']
                if 'city' in data:
                    geo_info['city'] = data['city']
                if 'org' in data:
                    geo_info['isp'] = data['org']
        except:
            logger.warning("无法获取地理位置信息，使用默认值")
        
        return geo_info
    
    def _load_existing_node(self):
        """加载已存在的节点配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.node_quantum_gene = config.get('node_quantum_gene')
            self.node_info = config.get('node_info', {})
            self.entanglement_channels = config.get('entanglement_channels', {})
            
            # 更新节点信息
            self.node_info.update({
                'last_online': datetime.now().isoformat(),
                'hardware_specs': self.hardware_specs,
                'quantum_bits': self.quantum_bits,
                'geo_position': self.geo_position
            })
            
            logger.info(f"加载已存在节点配置，量子基因编码: {self.node_quantum_gene}")
        except Exception as e:
            logger.error(f"加载节点配置失败: {str(e)}，将创建新节点")
            self._create_new_node()
    
    def _create_new_node(self):
        """创建新节点"""
        # 生成节点ID
        node_id = str(uuid.uuid4())
        
        # 生成硬件哈希
        hw_info = json.dumps(self.hardware_specs, sort_keys=True)
        hardware_hash = hashlib.md5(hw_info.encode()).hexdigest()[:6]
        
        # 生成地理位置哈希
        geo_info = json.dumps(self.geo_position, sort_keys=True)
        geo_hash = hashlib.md5(geo_info.encode()).hexdigest()[:6]
        
        # 生成时间戳
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        
        # 生成量子基因编码
        self.node_quantum_gene = f"QG-NODE-{timestamp}-{hardware_hash}-{geo_hash}"
        
        # 创建节点信息
        self.node_info = {
            'node_id': node_id,
            'node_quantum_gene': self.node_quantum_gene,
            'creation_time': datetime.now().isoformat(),
            'last_online': datetime.now().isoformat(),
            'hardware_specs': self.hardware_specs,
            'quantum_bits': self.quantum_bits,
            'geo_position': self.geo_position,
            'entanglement_capacity': self._calculate_entanglement_capacity(),
            'features': self._get_node_features()
        }
        
        # 保存配置
        self._save_config()
        
        logger.info(f"创建新节点，量子基因编码: {self.node_quantum_gene}")
    
    def _calculate_entanglement_capacity(self):
        """计算节点的量子纠缠容量"""
        # 基于量子比特数和硬件规格计算纠缠容量
        base_capacity = self.quantum_bits * 10
        
        # 网络带宽因子
        network_factor = 1.0
        # 在未来可以实现实际网络带宽检测
        
        # 计算最终容量
        total_capacity = int(base_capacity * network_factor)
        
        return total_capacity
    
    def _get_node_features(self):
        """获取节点支持的特性列表"""
        features = ["basic_entanglement"]
        
        # 根据量子比特数添加支持的特性
        if self.quantum_bits >= 65:
            features.append("advanced_entanglement_management")
            features.append("multidimensional_data_processing")
        
        if self.quantum_bits >= 129:
            features.append("dynamic_quantum_gateway")
            features.append("distributed_quantum_computing")
        
        if self.quantum_bits >= 513:
            features.append("quantum_algorithm_evolution")
            features.append("cross_dimensional_data_processing")
        
        if self.quantum_bits >= 1025:
            features.append("quantum_creative_thinking")
            features.append("holographic_quantum_projection")
        
        return features
    
    def _save_config(self):
        """保存节点配置"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            config = {
                'node_quantum_gene': self.node_quantum_gene,
                'node_info': self.node_info,
                'entanglement_channels': self.entanglement_channels
            }
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
            
            logger.info(f"节点配置已保存到 {self.config_path}")
        except Exception as e:
            logger.error(f"保存节点配置失败: {str(e)}")
    
    def _register_to_central_registry(self):
        """注册到中央量子纠缠注册中心"""
        try:
            # 在实际实现中这里会发送HTTP请求到中央服务器
            # 现在我们模拟这个过程
            logger.info(f"注册到中央量子纠缠注册中心: {self.CENTRAL_REGISTRY_URL}")
            
            # 模拟服务器响应
            registry_response = {
                'status': 'success',
                'message': '节点注册成功',
                'registry_timestamp': datetime.now().isoformat(),
                'node_id': self.node_info['node_id'],
                'node_quantum_gene': self.node_quantum_gene
            }
            
            self.node_info['registry_status'] = registry_response['status']
            self.node_info['registry_timestamp'] = registry_response['registry_timestamp']
            
            # 保存更新后的配置
            self._save_config()
            
            logger.info("节点注册成功")
            return True
        except Exception as e:
            logger.error(f"注册到中央量子纠缠注册中心失败: {str(e)}")
            
            # 离线模式 - 仍然可以工作，但功能受限
            self.node_info['registry_status'] = 'offline'
            self.node_info['registry_timestamp'] = datetime.now().isoformat()
            self._save_config()
            
            return False
    
    def _update_entanglement_topology(self):
        """获取网络拓扑更新"""
        try:
            # 在实际实现中这里会发送HTTP请求获取拓扑
            # 现在我们模拟这个过程
            logger.info("获取量子纠缠网络拓扑更新")
            
            # 模拟从服务器获取的节点列表
            nearby_nodes = self._simulate_nearby_nodes(5)
            core_nodes = self._simulate_core_nodes(3)
            
            # 更新本地拓扑信息
            topology_update = {
                'update_time': datetime.now().isoformat(),
                'nearby_nodes': nearby_nodes,
                'core_nodes': core_nodes,
                'recommended_channels': self._generate_recommended_channels(nearby_nodes, core_nodes)
            }
            
            self.node_info['topology_update'] = topology_update
            self._save_config()
            
            logger.info(f"成功获取网络拓扑更新，发现 {len(nearby_nodes)} 个附近节点和 {len(core_nodes)} 个核心节点")
            return True
        except Exception as e:
            logger.error(f"获取网络拓扑更新失败: {str(e)}")
            return False
    
    def _simulate_nearby_nodes(self, count):
        """模拟附近节点数据"""
        nearby_nodes = []
        for i in range(count):
            node = {
                'node_id': str(uuid.uuid4()),
                'node_quantum_gene': f"QG-NODE-202504{random.randint(1, 30):02d}{random.randint(0, 23):02d}{random.randint(0, 59):02d}{random.randint(0, 59):02d}-{self._random_hex(6)}-{self._random_hex(6)}",
                'quantum_bits': random.randint(28, 512),
                'distance': random.uniform(0.1, 100.0),
                'entanglement_strength': random.uniform(0.5, 0.95),
                'features': ["basic_entanglement"]
            }
            nearby_nodes.append(node)
        return nearby_nodes
    
    def _simulate_core_nodes(self, count):
        """模拟核心节点数据"""
        core_nodes = []
        for i in range(count):
            node = {
                'node_id': str(uuid.uuid4()),
                'node_quantum_gene': f"QG-CORE-202504{random.randint(1, 30):02d}{random.randint(0, 23):02d}{random.randint(0, 59):02d}{random.randint(0, 59):02d}-{self._random_hex(6)}-{self._random_hex(6)}",
                'quantum_bits': random.randint(1024, 8192),
                'role': random.choice(['registry', 'gateway', 'compute']),
                'distance': random.uniform(100.0, 10000.0),
                'entanglement_strength': random.uniform(0.8, 0.99),
                'features': ["advanced_entanglement_management", "distributed_quantum_computing", "quantum_algorithm_evolution"]
            }
            core_nodes.append(node)
        return core_nodes
    
    def _random_hex(self, length):
        """生成指定长度的随机十六进制字符串"""
        return ''.join(random.choice('0123456789abcdef') for _ in range(length))
    
    def _generate_recommended_channels(self, nearby_nodes, core_nodes):
        """生成推荐的量子纠缠信道列表"""
        recommended_channels = []
        
        # 添加所有核心节点
        for node in core_nodes:
            channel = {
                'target_node_id': node['node_id'],
                'target_quantum_gene': node['node_quantum_gene'],
                'priority': 'high' if node['role'] == 'registry' else 'medium',
                'min_entanglement_strength': 0.8,
                'features_required': ["basic_entanglement"]
            }
            recommended_channels.append(channel)
        
        # 添加一部分附近节点
        for node in nearby_nodes:
            if random.random() < 0.7:  # 70%概率添加
                channel = {
                    'target_node_id': node['node_id'],
                    'target_quantum_gene': node['node_quantum_gene'],
                    'priority': 'medium' if node['quantum_bits'] > 100 else 'low',
                    'min_entanglement_strength': 0.6,
                    'features_required': ["basic_entanglement"]
                }
                recommended_channels.append(channel)
        
        return recommended_channels
    
    def _establish_entanglement_channels(self):
        """建立量子纠缠信道"""
        if 'topology_update' not in self.node_info:
            logger.warning("没有可用的拓扑信息，无法建立量子纠缠信道")
            return False
        
        recommended_channels = self.node_info['topology_update']['recommended_channels']
        established_count = 0
        
        for channel_info in recommended_channels:
            try:
                target_gene = channel_info['target_quantum_gene']
                
                # 检查是否已经有这个信道
                if target_gene in self.entanglement_channels:
                    # 更新现有信道
                    self.entanglement_channels[target_gene]['last_refresh'] = datetime.now().isoformat()
                    self.entanglement_channels[target_gene]['status'] = 'active'
                    established_count += 1
                    continue
                
                # 建立新的量子纠缠信道
                entanglement_strength = self._calculate_entanglement_strength(channel_info)
                
                if entanglement_strength >= channel_info['min_entanglement_strength']:
                    # 创建新信道
                    new_channel = {
                        'target_node_id': channel_info['target_node_id'],
                        'target_quantum_gene': target_gene,
                        'establishment_time': datetime.now().isoformat(),
                        'last_refresh': datetime.now().isoformat(),
                        'entanglement_strength': entanglement_strength,
                        'status': 'active',
                        'priority': channel_info['priority'],
                        'features': channel_info['features_required']
                    }
                    
                    self.entanglement_channels[target_gene] = new_channel
                    established_count += 1
                    
                    logger.info(f"建立新的量子纠缠信道到 {target_gene}，强度：{entanglement_strength:.2f}")
                else:
                    logger.warning(f"无法建立到 {target_gene} 的量子纠缠信道，强度不足: {entanglement_strength:.2f} < {channel_info['min_entanglement_strength']}")
            except Exception as e:
                logger.error(f"建立量子纠缠信道失败: {str(e)}")
        
        # 保存更新后的配置
        self._save_config()
        
        logger.info(f"已建立 {established_count} 个量子纠缠信道")
        return established_count > 0
    
    def _calculate_entanglement_strength(self, channel_info):
        """计算到目标节点的量子纠缠强度"""
        # 基础强度 - 随机因素
        base_strength = random.uniform(0.5, 0.9)
        
        # 优先级因子
        priority_factor = 1.0
        if channel_info['priority'] == 'high':
            priority_factor = 1.3
        elif channel_info['priority'] == 'medium':
            priority_factor = 1.1
        
        # 量子比特数因子
        qubits_factor = min(1.5, 1.0 + (self.quantum_bits - 28) / 1000)
        
        # 计算最终强度
        strength = base_strength * priority_factor * qubits_factor
        
        # 确保在有效范围内
        return max(0.0, min(1.0, strength))
    
    def _start_entanglement_refresh(self):
        """启动量子纠缠信道刷新线程"""
        if self.entanglement_refresh_thread is not None and self.entanglement_refresh_thread.is_alive():
            logger.info("量子纠缠信道刷新线程已在运行")
            return
        
        self.stop_event.clear()
        self.entanglement_refresh_thread = threading.Thread(target=self._entanglement_refresh_worker, daemon=True)
        self.entanglement_refresh_thread.start()
        logger.info("启动量子纠缠信道刷新线程")
    
    def _entanglement_refresh_worker(self):
        """量子纠缠信道刷新工作线程"""
        while not self.stop_event.is_set():
            try:
                # 休眠一段时间
                for _ in range(self.ENTANGLEMENT_REFRESH_INTERVAL):
                    if self.stop_event.is_set():
                        break
                    time.sleep(1)
                
                if self.stop_event.is_set():
                    break
                
                logger.info("执行量子纠缠信道刷新")
                
                # 更新拓扑
                self._update_entanglement_topology()
                
                # 刷新现有信道
                self._refresh_entanglement_channels()
                
                # 建立新信道
                self._establish_entanglement_channels()
                
            except Exception as e:
                logger.error(f"量子纠缠信道刷新过程中发生错误: {str(e)}")
                time.sleep(60)  # 出错后等待1分钟再重试
    
    def _refresh_entanglement_channels(self):
        """刷新现有的量子纠缠信道"""
        expired_channels = []
        refreshed_count = 0
        
        for gene, channel in list(self.entanglement_channels.items()):
            try:
                # 检查是否过期
                last_refresh = datetime.fromisoformat(channel['last_refresh'])
                now = datetime.now()
                hours_since_refresh = (now - last_refresh).total_seconds() / 3600
                
                if hours_since_refresh > 24:  # 超过24小时未刷新
                    expired_channels.append(gene)
                    continue
                
                # 刷新纠缠强度
                new_strength = channel['entanglement_strength'] * random.uniform(0.95, 1.05)
                new_strength = max(0.1, min(1.0, new_strength))  # 确保在有效范围内
                
                # 检查是否需要休眠
                if new_strength < 0.3:
                    logger.info(f"量子纠缠信道 {gene} 强度过低 ({new_strength:.2f})，进入休眠状态")
                    channel['status'] = 'hibernating'
                else:
                    channel['status'] = 'active'
                
                channel['entanglement_strength'] = new_strength
                channel['last_refresh'] = now.isoformat()
                refreshed_count += 1
                
            except Exception as e:
                logger.error(f"刷新量子纠缠信道 {gene} 失败: {str(e)}")
        
        # 移除过期信道
        for gene in expired_channels:
            logger.info(f"移除过期的量子纠缠信道: {gene}")
            del self.entanglement_channels[gene]
        
        # 保存更新后的配置
        self._save_config()
        
        logger.info(f"已刷新 {refreshed_count} 个量子纠缠信道，移除 {len(expired_channels)} 个过期信道")
    
    def get_entanglement_channels(self, status=None):
        """获取量子纠缠信道列表"""
        if status:
            return {gene: channel for gene, channel in self.entanglement_channels.items() 
                    if channel['status'] == status}
        return self.entanglement_channels
    
    def get_active_channel_count(self):
        """获取活跃的量子纠缠信道数量"""
        return len(self.get_entanglement_channels(status='active'))
    
    def get_node_status(self):
        """获取节点状态信息"""
        status = {
            'node_quantum_gene': self.node_quantum_gene,
            'quantum_bits': self.quantum_bits,
            'total_channels': len(self.entanglement_channels),
            'active_channels': self.get_active_channel_count(),
            'hibernating_channels': len(self.get_entanglement_channels(status='hibernating')),
            'features': self._get_node_features(),
            'entanglement_capacity': self._calculate_entanglement_capacity(),
            'last_topology_update': self.node_info.get('topology_update', {}).get('update_time', 'never'),
            'registry_status': self.node_info.get('registry_status', 'unknown'),
            'uptime': self._calculate_uptime()
        }
        return status
    
    def _calculate_uptime(self):
        """计算节点运行时间（小时）"""
        if 'creation_time' not in self.node_info:
            return 0
        
        creation_time = datetime.fromisoformat(self.node_info['creation_time'])
        now = datetime.now()
        return round((now - creation_time).total_seconds() / 3600, 2)
    
    def shutdown(self):
        """关闭节点连接器"""
        logger.info("关闭量子节点连接器")
        self.stop_event.set()
        
        if self.entanglement_refresh_thread and self.entanglement_refresh_thread.is_alive():
            self.entanglement_refresh_thread.join(timeout=10)
        
        # 更新状态
        for gene in self.entanglement_channels:
            self.entanglement_channels[gene]['status'] = 'inactive'
        
        self.node_info['last_offline'] = datetime.now().isoformat()
        self._save_config()
        
        logger.info("量子节点连接器已关闭")

# 如果直接运行此脚本
if __name__ == "__main__":
    try:
        # 初始化量子节点连接器
        connector = QuantumNodeConnector()
        connector.initialize()
        
        # 显示状态
        print("节点状态:", json.dumps(connector.get_node_status(), indent=2, ensure_ascii=False))
        print("\n活跃的量子纠缠信道:")
        for gene, channel in connector.get_entanglement_channels(status='active').items():
            print(f"  - {gene} (强度: {channel['entanglement_strength']:.2f})")
        
        # 保持运行一段时间
        try:
            print("\n按 Ctrl+C 结束...")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n接收到终止信号")
        
        # 关闭连接器
        connector.shutdown()
        
    except Exception as e:
        logger.error(f"程序运行错误: {str(e)}")
        import traceback
        traceback.print_exc() 
"""
量子基因编码: QE-QUA-581A5EC51627
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
"""