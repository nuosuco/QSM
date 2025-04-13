#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
生成量子纠缠网络示意图
用于量子纠缠网络连接指南
"""

from PIL import Image, ImageDraw, ImageFont
import numpy as np
import random
import math
import os

def create_quantum_network_diagram():
    """创建量子纠缠网络示意图"""
    
    # 创建一个新图像
    width, height = 1000, 600
    image = Image.new('RGBA', (width, height), (255, 255, 255, 255))
    draw = ImageDraw.Draw(image)
    
    # 尝试加载字体
    try:
        title_font = ImageFont.truetype("arial.ttf", 24)
        node_font = ImageFont.truetype("arial.ttf", 14)
        small_font = ImageFont.truetype("arial.ttf", 12)
    except:
        title_font = ImageFont.load_default()
        node_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # 绘制标题
    draw.text((20, 20), "量子叠加态模型(QSM)全球量子纠缠网络", fill=(0, 0, 0), font=title_font)
    
    # 定义节点类型和颜色
    node_types = {
        "core": {"color": (0, 80, 180, 255), "size": 25, "name": "核心节点"},
        "software": {"color": (0, 160, 230, 255), "size": 20, "name": "软件节点"},
        "browser": {"color": (60, 180, 240, 255), "size": 15, "name": "浏览器节点"},
        "paper": {"color": (180, 220, 250, 255), "size": 12, "name": "物理介质节点"}
    }
    
    # 创建节点
    nodes = []
    
    # 1. 添加核心节点（中央）
    central_node = {
        "type": "core",
        "x": width // 2,
        "y": height // 2,
        "name": "QSM中央注册中心",
        "connections": []
    }
    nodes.append(central_node)
    
    # 2. 添加其他核心节点
    for i in range(5):
        angle = 2 * math.pi * i / 5
        distance = 150
        node = {
            "type": "core",
            "x": int(width // 2 + distance * math.cos(angle)),
            "y": int(height // 2 + distance * math.sin(angle)),
            "name": f"核心节点 {i+1}",
            "connections": [0]  # 连接到中央节点
        }
        nodes.append(node)
    
    # 3. 添加软件节点
    for i in range(15):
        angle = 2 * math.pi * i / 15 + 0.2
        distance = random.uniform(220, 280)
        node = {
            "type": "software",
            "x": int(width // 2 + distance * math.cos(angle)),
            "y": int(height // 2 + distance * math.sin(angle)),
            "name": f"软件节点 {i+1}",
            "connections": [random.randint(1, 5)]  # 连接到随机核心节点
        }
        nodes.append(node)
    
    # 4. 添加浏览器节点
    for i in range(25):
        angle = 2 * math.pi * i / 25 + 0.5
        distance = random.uniform(300, 380)
        node = {
            "type": "browser",
            "x": int(width // 2 + distance * math.cos(angle)),
            "y": int(height // 2 + distance * math.sin(angle)),
            "name": f"浏览器节点 {i+1}",
            "connections": [random.randint(6, 20)]  # 连接到随机软件节点
        }
        nodes.append(node)
    
    # 5. 添加物理介质节点
    for i in range(30):
        angle = 2 * math.pi * i / 30 + 0.8
        distance = random.uniform(360, 450)
        
        # 随机决定连接到哪类节点
        if random.random() < 0.7:
            # 70%连接到浏览器节点
            connection = random.randint(21, 45)
        else:
            # 30%连接到软件节点
            connection = random.randint(6, 20)
            
        node = {
            "type": "paper",
            "x": int(width // 2 + distance * math.cos(angle)),
            "y": int(height // 2 + distance * math.sin(angle)),
            "name": f"物理介质节点 {i+1}",
            "connections": [connection]
        }
        nodes.append(node)
    
    # 绘制连接线
    for i, node in enumerate(nodes):
        for connection in node["connections"]:
            if connection < len(nodes):
                target = nodes[connection]
                
                # 根据节点类型决定线的颜色和强度
                if node["type"] == "core" or target["type"] == "core":
                    line_color = (0, 100, 200, 180)
                    line_width = 2
                elif node["type"] == "software" or target["type"] == "software":
                    line_color = (30, 150, 220, 150)
                    line_width = 1
                elif node["type"] == "browser" or target["type"] == "browser":
                    line_color = (80, 180, 240, 120)
                    line_width = 1
                else:
                    line_color = (150, 200, 250, 100)
                    line_width = 1
                
                # 绘制线条
                draw.line(
                    [(node["x"], node["y"]), (target["x"], target["y"])],
                    fill=line_color,
                    width=line_width
                )
                
                # 添加量子纠缠效果（沿线随机点）
                line_length = math.sqrt((node["x"] - target["x"])**2 + (node["y"] - target["y"])**2)
                num_dots = int(line_length / 15)
                
                for _ in range(num_dots):
                    t = random.uniform(0.1, 0.9)
                    dot_x = int(node["x"] + t * (target["x"] - node["x"]))
                    dot_y = int(node["y"] + t * (target["y"] - node["y"]))
                    dot_size = random.randint(1, 2)
                    
                    # 根据节点类型调整点的颜色
                    if random.random() < 0.3:  # 30%的点更亮
                        dot_color = (0, 100, 255, 200)
                    else:
                        r, g, b, a = line_color
                        dot_color = (r, g, b, min(255, a + 50))
                        
                    draw.ellipse(
                        [(dot_x-dot_size, dot_y-dot_size), (dot_x+dot_size, dot_y+dot_size)],
                        fill=dot_color
                    )
    
    # 绘制节点
    for i, node in enumerate(nodes):
        node_type = node["type"]
        node_spec = node_types[node_type]
        
        # 绘制节点圆圈
        node_size = node_spec["size"]
        
        # 节点外圈光晕效果
        for s in range(4):
            glow_size = node_size + 4 - s
            r, g, b, a = node_spec["color"]
            glow_color = (r, g, b, min(120, a - 40 * s))
            
            draw.ellipse(
                [(node["x"]-glow_size, node["y"]-glow_size),
                 (node["x"]+glow_size, node["y"]+glow_size)],
                fill=glow_color
            )
        
        # 节点主体
        draw.ellipse(
            [(node["x"]-node_size, node["y"]-node_size),
             (node["x"]+node_size, node["y"]+node_size)],
            fill=node_spec["color"]
        )
        
        # 为核心节点和软件节点添加内部结构
        if node_type in ["core", "software"]:
            inner_size = node_size * 0.6
            draw.ellipse(
                [(node["x"]-inner_size, node["y"]-inner_size),
                 (node["x"]+inner_size, node["y"]+inner_size)],
                fill=(255, 255, 255, 180)
            )
            
            # 为核心节点添加量子比特符号
            if node_type == "core":
                qbit_size = inner_size * 0.7
                draw.ellipse(
                    [(node["x"]-qbit_size, node["y"]-qbit_size),
                     (node["x"]+qbit_size, node["y"]+qbit_size)],
                    fill=(0, 50, 150, 230)
                )
    
    # 添加图例
    legend_x = 30
    legend_y = height - 120
    
    draw.text((legend_x, legend_y), "节点类型", fill=(0, 0, 0), font=node_font)
    legend_y += 25
    
    for i, (type_name, type_info) in enumerate(node_types.items()):
        # 绘制图例项
        draw.ellipse(
            [(legend_x, legend_y + i*20 - type_info["size"]//2),
             (legend_x + type_info["size"], legend_y + i*20 + type_info["size"]//2)],
            fill=type_info["color"]
        )
        
        draw.text((legend_x + 40, legend_y + i*20 - 7), 
                  type_info["name"], 
                  fill=(0, 0, 0), 
                  font=small_font)
    
    # 添加说明文字
    desc_x = width - 300
    desc_y = height - 120
    
    desc_text = [
        "量子纠缠网络连接所有节点类型:",
        "• 核心节点 - 中央注册和管理",
        "• 软件节点 - 安装QSM软件的设备",
        "• 浏览器节点 - 通过浏览器访问的用户",
        "• 物理介质节点 - 打印内容和实体载体"
    ]
    
    for i, line in enumerate(desc_text):
        draw.text((desc_x, desc_y + i*20), 
                  line, 
                  fill=(0, 0, 0), 
                  font=small_font)
    
    # 保存图像
    output_path = "quantum_entanglement_network.png"
    image.save(output_path)
    print(f"已生成量子纠缠网络示意图: {output_path}")

if __name__ == "__main__":
    create_quantum_network_diagram() 

"""
"""
量子基因编码: QE-QUA-E8CD1C22DEFA
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
""""""

// 开发团队：中华 ZhoHo ，Claude 
