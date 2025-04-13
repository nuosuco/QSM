#!/usr/bin/env python3
import sys
import os
import time
import curses
import random
import threading
import logging
from typing import Dict, List, Any, Optional, Tuple

# 添加父目录到路径以导入QEntL模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.quantum_network import (
    QuantumNetwork, 
    ChannelType,
    ChannelState
)

# 配置日志
logging.basicConfig(
    filename='qentl_network_monitor.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("QEntL.NetworkMonitor")

class QuantumNetworkMonitor:
    """量子网络状态监控终端UI"""
    
    def __init__(self):
        self.network = QuantumNetwork()
        self.running = False
        self.update_thread = None
        self.screen = None
        self.node_positions: Dict[str, Tuple[int, int]] = {}
        self.connection_status: Dict[str, Dict[str, Any]] = {}
        self.event_log: List[str] = []
        self.max_log_entries = 10
        
    def start(self):
        """启动网络监控UI"""
        try:
            # 初始化curses
            self.screen = curses.initscr()
            curses.noecho()
            curses.cbreak()
            self.screen.keypad(True)
            curses.start_color()
            curses.use_default_colors()
            
            # 初始化颜色对
            curses.init_pair(1, curses.COLOR_GREEN, -1)    # 活跃节点/连接
            curses.init_pair(2, curses.COLOR_RED, -1)      # 错误
            curses.init_pair(3, curses.COLOR_YELLOW, -1)   # 警告/处理中
            curses.init_pair(4, curses.COLOR_CYAN, -1)     # 信息
            curses.init_pair(5, curses.COLOR_MAGENTA, -1)  # 特殊操作
            curses.init_pair(6, curses.COLOR_BLUE, -1)     # UI元素
            
            # 启动更新线程
            self.running = True
            self.update_thread = threading.Thread(target=self._update_network_status)
            self.update_thread.daemon = True
            self.update_thread.start()
            
            # 运行UI循环
            self._run_ui_loop()
            
        except Exception as e:
            logger.error(f"UI错误: {e}")
        finally:
            self._cleanup()
    
    def _cleanup(self):
        """退出时清理curses设置"""
        if self.screen:
            self.screen.keypad(False)
            curses.echo()
            curses.nocbreak()
            curses.endwin()
        self.running = False
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(timeout=1)
    
    def _update_network_status(self):
        """后台线程更新网络状态"""
        while self.running:
            try:
                # 更新节点状态
                for node_id, node in self.network.nodes.items():
                    # 更新通道状态
                    for channel_id, channel in node.channels.items():
                        key = f"{node_id}:{channel_id}"
                        target_node = channel.target_node_id
                        
                        if key not in self.connection_status:
                            self.connection_status[key] = {
                                "source": node_id,
                                "target": target_node,
                                "state": channel.state.value,
                                "type": channel.channel_type.value,
                                "activity": 0,
                                "entangled": False
                            }
                        else:
                            self.connection_status[key]["state"] = channel.state.value
                
                # 模拟一些网络活动用于演示目的
                if self.connection_status and random.random() < 0.3:
                    key = random.choice(list(self.connection_status.keys()))
                    event_type = random.choice(["PING", "QUBIT_TRANSFER", "ENTANGLEMENT", "MEASUREMENT"])
                    
                    # 更新连接活动
                    self.connection_status[key]["activity"] = 5  # 活动计数器
                    
                    if event_type == "ENTANGLEMENT":
                        self.connection_status[key]["entangled"] = True
                        self._add_event_log(f"在 {self.connection_status[key]['source']} 和 {self.connection_status[key]['target']} 之间建立了纠缠")
                    elif event_type == "MEASUREMENT":
                        result = random.choice(["0", "1"])
                        self._add_event_log(f"在 {self.connection_status[key]['source']} 上测量了量子比特: {result}")
                        if self.connection_status[key]["entangled"]:
                            self.connection_status[key]["entangled"] = False
                            self._add_event_log(f"由于测量，纠缠被破坏")
                    elif event_type == "QUBIT_TRANSFER":
                        self._add_event_log(f"量子比特从 {self.connection_status[key]['source']} 传输到 {self.connection_status[key]['target']}")
                    
                # 衰减活动
                for key in self.connection_status:
                    if self.connection_status[key]["activity"] > 0:
                        self.connection_status[key]["activity"] -= 1
                
                time.sleep(0.5)
            except Exception as e:
                logger.error(f"更新错误: {e}")
                time.sleep(1)
    
    def _add_event_log(self, message: str):
        """添加带时间戳的事件日志条目"""
        timestamp = time.strftime("%H:%M:%S")
        self.event_log.append(f"[{timestamp}] {message}")
        if len(self.event_log) > self.max_log_entries:
            self.event_log.pop(0)
    
    def _draw_node(self, y: int, x: int, node_id: str, name: str, is_active: bool = True):
        """在指定位置绘制节点"""
        self.node_positions[node_id] = (y, x)
        
        color = curses.color_pair(1) if is_active else curses.color_pair(3)
        
        # 绘制节点框
        self.screen.addch(y-1, x-2, curses.ACS_ULCORNER)
        self.screen.addch(y-1, x-1, curses.ACS_HLINE)
        self.screen.addch(y-1, x, curses.ACS_HLINE)
        self.screen.addch(y-1, x+1, curses.ACS_HLINE)
        self.screen.addch(y-1, x+2, curses.ACS_URCORNER)
        
        self.screen.addch(y, x-2, curses.ACS_VLINE)
        self.screen.addstr(y, x-1, " ", color)
        self.screen.addch(y, x, ord('O'), color)
        self.screen.addstr(y, x+1, " ", color)
        self.screen.addch(y, x+2, curses.ACS_VLINE)
        
        self.screen.addch(y+1, x-2, curses.ACS_LLCORNER)
        self.screen.addch(y+1, x-1, curses.ACS_HLINE)
        self.screen.addch(y+1, x, curses.ACS_HLINE)
        self.screen.addch(y+1, x+1, curses.ACS_HLINE)
        self.screen.addch(y+1, x+2, curses.ACS_LRCORNER)
        
        # 绘制名称
        start_x = max(x - len(name)//2, 0)
        self.screen.addstr(y+2, start_x, name[:10], color)
    
    def _draw_connection(self, source_id: str, target_id: str, is_active: bool = False, 
                        is_entangled: bool = False, channel_type: str = "QUANTUM"):
        """绘制两个节点之间的连接"""
        if source_id not in self.node_positions or target_id not in self.node_positions:
            return
        
        sy, sx = self.node_positions[source_id]
        ty, tx = self.node_positions[target_id]
        
        # 根据连接类型和状态确定颜色
        if is_entangled:
            color = curses.color_pair(5)  # 紫色表示纠缠
        elif is_active:
            color = curses.color_pair(1)  # 绿色表示活跃
        elif channel_type == "CLASSICAL":
            color = curses.color_pair(6)  # 蓝色表示经典
        else:
            color = curses.color_pair(4)  # 青色表示量子
        
        # 绘制节点间的简单线条
        if sx == tx:
            # 垂直连接
            start_y = min(sy, ty) + 1
            end_y = max(sy, ty) - 1
            for y in range(start_y, end_y + 1):
                self.screen.addch(y, sx, curses.ACS_VLINE, color)
        elif sy == ty:
            # 水平连接
            start_x = min(sx, tx) + 3
            end_x = max(sx, tx) - 3
            for x in range(start_x, end_x + 1):
                self.screen.addch(sy, x, curses.ACS_HLINE, color)
        else:
            # 对角线连接(简化版)
            dy = 1 if ty > sy else -1
            dx = 1 if tx > sx else -1
            
            y, x = sy + dy, sx + (3 * dx)
            while abs(y - ty) > 1 and abs(x - tx) > 3:
                self.screen.addch(y, x, '\\' if dy * dx > 0 else '/', color)
                y += dy
                x += dx
    
    def _run_ui_loop(self):
        """主UI循环"""
        # 创建一些演示节点用于可视化
        demo_nodes = [
            {"id": "node1", "name": "量子实验室", "pos": (5, 15)},
            {"id": "node2", "name": "卫星", "pos": (5, 50)},
            {"id": "node3", "name": "数据中心", "pos": (12, 50)},
            {"id": "node4", "name": "中继器", "pos": (12, 15)},
            {"id": "node5", "name": "终端用户", "pos": (18, 32)}
        ]
        
        # 创建一些演示连接
        demo_connections = [
            {"source": "node1", "target": "node2", "type": "QUANTUM"},
            {"source": "node2", "target": "node3", "type": "QUANTUM"},
            {"source": "node1", "target": "node4", "type": "CLASSICAL"},
            {"source": "node4", "target": "node5", "type": "QUANTUM"},
            {"source": "node2", "target": "node5", "type": "QUANTUM"}
        ]
        
        # 添加节点到网络用于演示
        for node in demo_nodes:
            if node["id"] not in self.network.nodes:
                self.network.create_node(node_id=node["id"], name=node["name"])
        
        # 连接节点
        for conn in demo_connections:
            channel_type = ChannelType.QUANTUM if conn["type"] == "QUANTUM" else ChannelType.CLASSICAL
            self.network.connect_nodes(conn["source"], conn["target"], channel_type)
            
            # 打开一些连接
            if random.random() > 0.3:
                self.network.open_connection(conn["source"], conn["target"])
        
        # 主显示循环
        while self.running:
            try:
                self.screen.clear()
                height, width = self.screen.getmaxyx()
                
                # 绘制标题
                title = "QEntL 量子网络监控"
                self.screen.addstr(1, (width - len(title)) // 2, title, curses.color_pair(4) | curses.A_BOLD)
                
                # 绘制节点
                for node in demo_nodes:
                    y, x = node["pos"]
                    node_id = node["id"]
                    is_active = node_id in self.network.nodes
                    self._draw_node(y, x, node_id, node["name"], is_active)
                
                # 绘制连接
                for conn in demo_connections:
                    source_id = conn["source"]
                    target_id = conn["target"]
                    
                    # 查找连接状态
                    conn_key = None
                    active = False
                    entangled = False
                    
                    for key, status in self.connection_status.items():
                        if (status["source"] == source_id and status["target"] == target_id) or \
                           (status["source"] == target_id and status["target"] == source_id):
                            conn_key = key
                            active = status["activity"] > 0 or status["state"] == "OPEN"
                            entangled = status["entangled"]
                            break
                    
                    self._draw_connection(source_id, target_id, active, entangled, conn["type"])
                
                # 绘制状态框
                status_y = 22
                self.screen.addstr(status_y, 2, "状态:", curses.color_pair(6) | curses.A_BOLD)
                
                # 绘制事件日志
                log_y = status_y + 2
                self.screen.addstr(log_y - 1, 2, "事件日志:", curses.color_pair(6) | curses.A_BOLD)
                
                for i, log_entry in enumerate(self.event_log):
                    if log_y + i < height - 2:
                        # 根据日志内容设置颜色
                        if "错误" in log_entry.lower():
                            color = curses.color_pair(2)
                        elif "纠缠" in log_entry.lower():
                            color = curses.color_pair(5)
                        elif "测量" in log_entry.lower():
                            color = curses.color_pair(3)
                        else:
                            color = curses.color_pair(4)
                        
                        self.screen.addstr(log_y + i, 4, log_entry[:width-6], color)
                
                # 绘制帮助文本
                help_text = "按 'q' 退出, 'e' 随机节点纠缠, 'm' 测量"
                if height > 35:
                    self.screen.addstr(height-2, (width - len(help_text)) // 2, help_text, curses.color_pair(6))
                
                self.screen.refresh()
                
                # 检查用户输入(非阻塞)
                self.screen.timeout(100)  # 100毫秒超时用于getch()
                key = self.screen.getch()
                
                if key == ord('q'):
                    self.running = False
                elif key == ord('e'):
                    # 触发随机纠缠
                    if self.connection_status:
                        conn_key = random.choice(list(self.connection_status.keys()))
                        self.connection_status[conn_key]["entangled"] = True
                        self._add_event_log(f"手动触发了 {self.connection_status[conn_key]['source']} 和 {self.connection_status[conn_key]['target']} 之间的纠缠")
                elif key == ord('m'):
                    # 触发随机测量
                    entangled_conns = [k for k, v in self.connection_status.items() if v.get("entangled")]
                    if entangled_conns:
                        conn_key = random.choice(entangled_conns)
                        result = random.choice(["0", "1"])
                        self._add_event_log(f"手动测量 {self.connection_status[conn_key]['source']}: {result}")
                        self.connection_status[conn_key]["entangled"] = False
                        self._add_event_log(f"由于测量，纠缠被破坏")
                
            except Exception as e:
                logger.error(f"UI渲染错误: {e}")
                time.sleep(1)
        
        # 清理
        self._cleanup()

def main():
    monitor = QuantumNetworkMonitor()
    try:
        monitor.start()
    except KeyboardInterrupt:
        pass
    finally:
        monitor._cleanup()
    
    print("量子网络监控已关闭")

if __name__ == "__main__":
    main() 

"""
"""
量子基因编码: QE-NET-BD811BAE3432
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
""""""

// 开发团队：中华 ZhoHo ，Claude 
