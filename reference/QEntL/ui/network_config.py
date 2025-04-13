#!/usr/bin/env python3
import os
import sys
import json
import time
import curses
import logging
from typing import Dict, List, Any, Optional, Tuple

# 添加父目录到路径以导入QEntL模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.quantum_network import QuantumNetwork, ChannelType

# 配置日志
logging.basicConfig(
    filename='qentl_network_config.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("QEntL.NetworkConfig")

class MenuOption:
    """表示菜单选项"""
    def __init__(self, key: str, text: str, action=None):
        self.key = key
        self.text = text
        self.action = action

class NetworkConfigUI:
    """用于创建和编辑量子网络配置的文本界面"""
    
    def __init__(self):
        self.network = QuantumNetwork()
        self.config_file = "quantum_network.json"
        self.current_menu = "main"
        self.selected_node = None
        self.selected_channel = None
        self.running = False
        self.status_message = ""
        self.error_message = ""
        
        # 标准屏幕尺寸
        self.max_y = 24
        self.max_x = 80
    
    def start(self):
        """启动配置UI"""
        self.running = True
        
        # 检查是否有配置文件可以加载
        if os.path.exists(self.config_file):
            try:
                self.network.load_network_config(self.config_file)
                self.status_message = f"从 {self.config_file} 加载了网络配置"
                logger.info(f"从 {self.config_file} 加载了网络配置")
            except Exception as e:
                self.error_message = f"加载配置失败: {str(e)}"
                logger.error(f"加载配置失败: {str(e)}")
        
        # 初始化curses
        curses.wrapper(self._run_ui)
    
    def _run_ui(self, stdscr):
        """运行主UI循环"""
        # 初始化颜色
        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)  # 标题
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)  # 选择
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)  # 成功
        curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)    # 错误
        curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_BLACK) # 警告
        curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_BLACK)   # 信息
        
        # 隐藏光标
        curses.curs_set(0)
        
        # 获取终端尺寸
        self.max_y, self.max_x = stdscr.getmaxyx()
        
        # 主UI循环
        while self.running:
            # 清屏
            stdscr.clear()
            
            # 绘制UI元素
            self._draw_title(stdscr)
            self._draw_menu(stdscr)
            self._draw_status(stdscr)
            
            # 更新屏幕
            stdscr.refresh()
            
            # 处理输入
            try:
                key = stdscr.getkey()
                self._handle_input(key)
            except Exception as e:
                self.error_message = f"错误: {str(e)}"
                logger.error(f"UI错误: {str(e)}")
    
    def _draw_title(self, stdscr):
        """绘制标题栏"""
        title = " QEntL 量子网络配置 "
        # 居中标题
        start_x = max(0, (self.max_x - len(title)) // 2)
        
        # 绘制标题栏
        stdscr.attron(curses.color_pair(1))
        stdscr.addstr(0, 0, " " * self.max_x)
        stdscr.addstr(0, start_x, title)
        stdscr.attroff(curses.color_pair(1))
        
        # 绘制网络信息
        if self.current_menu == "main":
            info = f" 网络ID: {self.network.network_id} | 节点数: {len(self.network.nodes)} "
            stdscr.addstr(1, 0, info)
    
    def _draw_menu(self, stdscr):
        """绘制当前菜单"""
        if self.current_menu == "main":
            self._draw_main_menu(stdscr)
        elif self.current_menu == "node":
            self._draw_node_menu(stdscr)
        elif self.current_menu == "add_node":
            self._draw_add_node_form(stdscr)
        elif self.current_menu == "add_connection":
            self._draw_add_connection_form(stdscr)
        elif self.current_menu == "node_detail":
            self._draw_node_detail(stdscr)
        elif self.current_menu == "connection_detail":
            self._draw_connection_detail(stdscr)
    
    def _draw_main_menu(self, stdscr):
        """绘制主菜单"""
        # 绘制节点列表
        y = 3
        stdscr.addstr(y, 0, "量子节点:")
        y += 1
        
        if not self.network.nodes:
            stdscr.addstr(y, 2, "尚未定义节点")
            y += 1
        else:
            for idx, (node_id, node) in enumerate(self.network.nodes.items()):
                display = f"{idx+1}. {node.name} ({node_id[:8]}...) - 已连接到 {len(node.get_connected_nodes())} 个节点"
                stdscr.addstr(y, 2, display)
                y += 1
        
        # 绘制菜单选项
        y += 2
        stdscr.addstr(y, 0, "菜单选项:")
        y += 1
        
        options = [
            MenuOption("a", "添加节点", self._action_add_node),
            MenuOption("c", "添加连接", self._action_add_connection),
            MenuOption("v", "查看节点详情", self._action_view_node),
            MenuOption("s", "保存配置", self._action_save_config),
            MenuOption("l", "加载配置", self._action_load_config),
            MenuOption("q", "退出", self._action_quit)
        ]
        
        for option in options:
            stdscr.addstr(y, 2, f"{option.key} - {option.text}")
            y += 1
    
    def _draw_node_menu(self, stdscr):
        """绘制节点选择菜单"""
        y = 3
        stdscr.addstr(y, 0, "选择一个节点:")
        y += 1
        
        if not self.network.nodes:
            stdscr.addstr(y, 2, "尚未定义节点")
            y += 1
        else:
            for idx, (node_id, node) in enumerate(self.network.nodes.items()):
                display = f"{idx+1}. {node.name} ({node_id[:8]}...)"
                stdscr.addstr(y, 2, display)
                y += 1
        
        y += 2
        stdscr.addstr(y, 0, "输入节点编号或输入 'b' 返回: ")
    
    def _draw_add_node_form(self, stdscr):
        """绘制添加新节点的表单"""
        y = 3
        stdscr.addstr(y, 0, "添加新量子节点")
        y += 2
        
        stdscr.addstr(y, 2, "输入节点名称(留空则自动生成): ")
        y += 2
        
        stdscr.addstr(y, 2, "按回车创建或按Esc取消")
    
    def _draw_add_connection_form(self, stdscr):
        """绘制添加新连接的表单"""
        y = 3
        stdscr.addstr(y, 0, "添加新连接")
        y += 2
        
        if len(self.network.nodes) < 2:
            stdscr.addstr(y, 2, "需要至少两个节点才能创建连接")
            y += 2
            stdscr.addstr(y, 2, "按任意键返回")
            return
        
        # 列出源节点选择
        stdscr.addstr(y, 2, "选择源节点:")
        y += 1
        
        for idx, (node_id, node) in enumerate(self.network.nodes.items()):
            display = f"{idx+1}. {node.name} ({node_id[:8]}...)"
            stdscr.addstr(y, 4, display)
            y += 1
        
        y += 1
        stdscr.addstr(y, 2, "输入源节点编号: ")
    
    def _draw_node_detail(self, stdscr):
        """绘制节点的详细信息"""
        if not self.selected_node or self.selected_node not in self.network.nodes:
            self.current_menu = "main"
            return
        
        node = self.network.nodes[self.selected_node]
        
        y = 3
        stdscr.addstr(y, 0, f"节点详情: {node.name}")
        y += 1
        stdscr.addstr(y, 2, f"ID: {node.node_id}")
        y += 1
        stdscr.addstr(y, 2, f"创建时间: {time.ctime(node.creation_time)}")
        y += 1
        stdscr.addstr(y, 2, f"最后活动: {time.ctime(node.last_activity)}")
        y += 1
        stdscr.addstr(y, 2, f"可用量子比特: {node.qubits_available}")
        y += 1
        stdscr.addstr(y, 2, f"状态: {'活跃' if node.is_active else '非活跃'}")
        y += 2
        
        # 列出连接的节点
        stdscr.addstr(y, 0, "已连接节点:")
        y += 1
        
        connected = node.get_connected_nodes()
        if not connected:
            stdscr.addstr(y, 2, "无连接")
            y += 1
        else:
            for idx, connected_id in enumerate(connected):
                if connected_id in self.network.nodes:
                    connected_node = self.network.nodes[connected_id]
                    display = f"{idx+1}. {connected_node.name}"
                    
                    # 获取通道信息
                    channel = node.get_channel_to_node(connected_id)
                    if channel:
                        display += f" ({channel.channel_type.value}, {channel.state.value})"
                    
                    stdscr.addstr(y, 2, display)
                    y += 1
        
        y += 2
        stdscr.addstr(y, 0, "选项:")
        y += 1
        stdscr.addstr(y, 2, "c - 查看连接详情")
        y += 1
        stdscr.addstr(y, 2, "d - 删除节点")
        y += 1
        stdscr.addstr(y, 2, "b - 返回主菜单")
    
    def _draw_connection_detail(self, stdscr):
        """绘制连接的详细信息"""
        if not self.selected_node or self.selected_node not in self.network.nodes:
            self.current_menu = "main"
            return
        
        if not self.selected_channel:
            self.current_menu = "node_detail"
            return
        
        node = self.network.nodes[self.selected_node]
        
        # 查找通道
        channel = None
        for c in node.channels.values():
            if c.channel_id == self.selected_channel:
                channel = c
                break
        
        if not channel:
            self.current_menu = "node_detail"
            return
        
        # 获取另一个节点
        other_node_id = channel.target_node_id if channel.source_node_id == self.selected_node else channel.source_node_id
        other_node = self.network.nodes.get(other_node_id)
        
        y = 3
        stdscr.addstr(y, 0, "连接详情")
        y += 1
        stdscr.addstr(y, 2, f"通道ID: {channel.channel_id}")
        y += 1
        stdscr.addstr(y, 2, f"连接: {node.name} 和 {other_node.name if other_node else '未知'}")
        y += 1
        stdscr.addstr(y, 2, f"类型: {channel.channel_type.value}")
        y += 1
        stdscr.addstr(y, 2, f"状态: {channel.state.value}")
        y += 1
        
        if channel.state.value == "ENTANGLED":
            stdscr.addstr(y, 2, f"纠缠保真度: {channel.entanglement_fidelity:.2f}")
            y += 1
        
        y += 1
        stdscr.addstr(y, 0, "通道指标:")
        y += 1
        for metric, value in channel.metrics.items():
            stdscr.addstr(y, 2, f"{metric}: {value}")
            y += 1
        
        y += 2
        stdscr.addstr(y, 0, "选项:")
        y += 1
        
        if channel.state.value == "CLOSED":
            stdscr.addstr(y, 2, "o - 打开通道")
        elif channel.state.value == "OPEN":
            stdscr.addstr(y, 2, "c - 关闭通道")
            y += 1
            stdscr.addstr(y, 2, "e - 创建纠缠")
        elif channel.state.value == "ENTANGLED":
            stdscr.addstr(y, 2, "m - 测量纠缠")
        
        y += 1
        stdscr.addstr(y, 2, "d - 断开节点")
        y += 1
        stdscr.addstr(y, 2, "b - 返回节点详情")
    
    def _draw_status(self, stdscr):
        """绘制状态和错误消息"""
        # 状态消息(绿色)
        if self.status_message:
            y = self.max_y - 2
            stdscr.attron(curses.color_pair(3))
            stdscr.addstr(y, 0, self.status_message[:self.max_x-1])
            stdscr.attroff(curses.color_pair(3))
        
        # 错误消息(红色)
        if self.error_message:
            y = self.max_y - 1
            stdscr.attron(curses.color_pair(4))
            stdscr.addstr(y, 0, self.error_message[:self.max_x-1])
            stdscr.attroff(curses.color_pair(4))
    
    def _handle_input(self, key):
        """根据当前菜单处理用户输入"""
        # 清除状态和错误消息
        self.status_message = ""
        self.error_message = ""
        
        if self.current_menu == "main":
            self._handle_main_menu_input(key)
        elif self.current_menu == "node":
            self._handle_node_menu_input(key)
        elif self.current_menu == "add_node":
            self._handle_add_node_input(key)
        elif self.current_menu == "add_connection":
            self._handle_add_connection_input(key)
        elif self.current_menu == "node_detail":
            self._handle_node_detail_input(key)
        elif self.current_menu == "connection_detail":
            self._handle_connection_detail_input(key)
    
    def _handle_main_menu_input(self, key):
        """处理主菜单的输入"""
        if key.lower() == 'a':
            self._action_add_node()
        elif key.lower() == 'c':
            self._action_add_connection()
        elif key.lower() == 'v':
            self._action_view_node()
        elif key.lower() == 's':
            self._action_save_config()
        elif key.lower() == 'l':
            self._action_load_config()
        elif key.lower() == 'q':
            self._action_quit()
    
    def _handle_node_menu_input(self, key):
        """处理节点选择菜单的输入"""
        if key.lower() == 'b':
            self.current_menu = "main"
        else:
            try:
                idx = int(key) - 1
                if 0 <= idx < len(self.network.nodes):
                    node_id = list(self.network.nodes.keys())[idx]
                    self.selected_node = node_id
                    self.current_menu = "node_detail"
                else:
                    self.error_message = "无效的节点编号"
            except ValueError:
                self.error_message = "无效输入"
    
    def _handle_add_node_input(self, key):
        """处理添加节点表单的输入"""
        if key == '\n':  # 回车键
            # 使用默认名称创建节点
            node_id = self.network.create_node(name=f"节点-{len(self.network.nodes)+1}")
            self.status_message = f"创建了新节点: {self.network.nodes[node_id].name}"
            self.current_menu = "main"
        elif key == '\x1b':  # Esc键
            self.current_menu = "main"
    
    def _handle_add_connection_input(self, key):
        """处理添加连接表单的输入"""
        if len(self.network.nodes) < 2:
            self.current_menu = "main"
            return
        
        if not hasattr(self, 'connection_state'):
            self.connection_state = {'step': 'source'}
        
        if self.connection_state['step'] == 'source':
            try:
                # 获取源节点
                idx = int(key) - 1
                if 0 <= idx < len(self.network.nodes):
                    node_id = list(self.network.nodes.keys())[idx]
                    self.connection_state['source_id'] = node_id
                    self.connection_state['step'] = 'target'
                    self.status_message = f"已选择源节点: {self.network.nodes[node_id].name}"
                else:
                    self.error_message = "无效的节点编号"
            except ValueError:
                if key.lower() == 'b':
                    self.current_menu = "main"
                else:
                    self.error_message = "无效输入"
        
        elif self.connection_state['step'] == 'target':
            try:
                # 获取目标节点
                idx = int(key) - 1
                if 0 <= idx < len(self.network.nodes):
                    node_id = list(self.network.nodes.keys())[idx]
                    
                    if node_id == self.connection_state['source_id']:
                        self.error_message = "不能将节点连接到自身"
                    else:
                        self.connection_state['target_id'] = node_id
                        self.connection_state['step'] = 'type'
                        self.status_message = f"已选择目标节点: {self.network.nodes[node_id].name}"
                else:
                    self.error_message = "无效的节点编号"
            except ValueError:
                if key.lower() == 'b':
                    self.connection_state['step'] = 'source'
                else:
                    self.error_message = "无效输入"
        
        elif self.connection_state['step'] == 'type':
            # 获取通道类型
            if key.lower() == 'q':
                channel_type = ChannelType.QUANTUM
            elif key.lower() == 'c':
                channel_type = ChannelType.CLASSICAL
            elif key.lower() == 'h':
                channel_type = ChannelType.HYBRID
            elif key.lower() == 'b':
                self.connection_state['step'] = 'target'
                return
            else:
                self.error_message = "无效输入"
                return
            
            # 创建连接
            source_id = self.connection_state['source_id']
            target_id = self.connection_state['target_id']
            
            channel_id = self.network.connect_nodes(source_id, target_id, channel_type)
            
            if channel_id:
                self.status_message = f"已连接 {self.network.nodes[source_id].name} 和 {self.network.nodes[target_id].name}"
            else:
                self.error_message = "创建连接失败"
            
            # 重置并返回主菜单
            delattr(self, 'connection_state')
            self.current_menu = "main"
    
    def _handle_node_detail_input(self, key):
        """处理节点详情屏幕的输入"""
        if key.lower() == 'b':
            self.selected_node = None
            self.current_menu = "main"
        elif key.lower() == 'c':
            # 查看连接详情 - 需要先选择一个连接
            node = self.network.nodes[self.selected_node]
            connected = node.get_connected_nodes()
            
            if not connected:
                self.error_message = "没有可查看的连接"
                return
            
            self.current_menu = "select_connection"
            return
        elif key.lower() == 'd':
            # 删除节点
            if self.network.remove_node(self.selected_node):
                self.status_message = "节点已删除"
                self.selected_node = None
                self.current_menu = "main"
            else:
                self.error_message = "删除节点失败"
    
    def _handle_connection_detail_input(self, key):
        """处理连接详情屏幕的输入"""
        if not self.selected_node or self.selected_node not in self.network.nodes:
            self.current_menu = "main"
            return
        
        if not self.selected_channel:
            self.current_menu = "node_detail"
            return
        
        node = self.network.nodes[self.selected_node]
        
        # 查找通道
        channel = None
        for c in node.channels.values():
            if c.channel_id == self.selected_channel:
                channel = c
                break
        
        if not channel:
            self.current_menu = "node_detail"
            return
        
        other_node_id = channel.target_node_id if channel.source_node_id == self.selected_node else channel.source_node_id
        
        if key.lower() == 'b':
            self.selected_channel = None
            self.current_menu = "node_detail"
        elif key.lower() == 'o' and channel.state.value == "CLOSED":
            # 打开通道
            if self.network.open_connection(self.selected_node, other_node_id):
                self.status_message = "通道已打开"
            else:
                self.error_message = "打开通道失败"
        elif key.lower() == 'c' and channel.state.value == "OPEN":
            # 关闭通道
            if self.network.close_connection(self.selected_node, other_node_id):
                self.status_message = "通道已关闭"
            else:
                self.error_message = "关闭通道失败"
        elif key.lower() == 'e' and channel.state.value == "OPEN":
            # 创建纠缠
            if self.network.create_entanglement(self.selected_node, other_node_id):
                self.status_message = "已创建纠缠"
            else:
                self.error_message = "创建纠缠失败"
        elif key.lower() == 'm' and channel.state.value == "ENTANGLED":
            # 测量纠缠
            results = self.network.measure_entanglement(self.selected_node, other_node_id)
            if results[0] is not None:
                self.status_message = f"测量结果: {results[0]}, {results[1]}"
            else:
                self.error_message = "测量纠缠失败"
        elif key.lower() == 'd':
            # 断开节点
            if self.network.disconnect_nodes(self.selected_node, other_node_id):
                self.status_message = "节点已断开"
                self.selected_channel = None
                self.current_menu = "node_detail"
            else:
                self.error_message = "断开节点失败"
    
    def _action_add_node(self):
        """添加新节点的操作"""
        self.current_menu = "add_node"
    
    def _action_add_connection(self):
        """添加新连接的操作"""
        if len(self.network.nodes) < 2:
            self.error_message = "至少需要两个节点才能创建连接"
            return
        
        self.current_menu = "add_connection"
    
    def _action_view_node(self):
        """查看节点详情的操作"""
        if not self.network.nodes:
            self.error_message = "没有可查看的节点"
            return
        
        self.current_menu = "node"
    
    def _action_save_config(self):
        """保存网络配置的操作"""
        if self.network.save_network_config(self.config_file):
            self.status_message = f"配置已保存到 {self.config_file}"
        else:
            self.error_message = "保存配置失败"
    
    def _action_load_config(self):
        """加载网络配置的操作"""
        if os.path.exists(self.config_file):
            if self.network.load_network_config(self.config_file):
                self.status_message = f"已从 {self.config_file} 加载配置"
            else:
                self.error_message = "加载配置失败"
        else:
            self.error_message = f"未找到配置文件 {self.config_file}"
    
    def _action_quit(self):
        """退出应用程序的操作"""
        self.running = False

def main():
    """网络配置工具的主入口点"""
    try:
        ui = NetworkConfigUI()
        ui.start()
    except Exception as e:
        logger.error(f"未处理的异常: {str(e)}")
        print(f"错误: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 

"""
"""
量子基因编码: QE-NET-349C7280E91F
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
""""""

// 开发团队：中华 ZhoHo ，Claude 
