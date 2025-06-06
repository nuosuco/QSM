#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
量子水印模块
负责在输出内容中嵌入量子基因编码，实现物理介质量子纠缠
"""

import os
import sys
import numpy as np
import uuid
import hashlib
import base64
import time
import logging
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("量子水印")

class QuantumWatermark:
    """量子水印处理器，为物理介质嵌入量子基因编码"""
    
    def __init__(self, watermark_strength=0.05, pattern_density=0.8):
        """初始化量子水印处理器
        
        参数:
            watermark_strength: 水印强度，越小越不可见
            pattern_density: 水印密度，越大编码越冗余
        """
        self.watermark_strength = watermark_strength
        self.pattern_density = pattern_density
        self.quantum_gene = None
        self.content_hash = None
        logger.info("初始化量子水印处理器")
    
    def generate_content_quantum_gene(self, content, content_type="TEXT"):
        """为内容生成量子基因编码
        
        参数:
            content: 要处理的内容（文本、图像等）
            content_type: 内容类型（TEXT, IMAGE, CODE, OUT等）
            
        返回:
            量子基因编码字符串
        """
        # 生成内容哈希
        if isinstance(content, str):
            content_bytes = content.encode('utf-8')
        elif isinstance(content, bytes):
            content_bytes = content
        else:
            content_bytes = str(content).encode('utf-8')
            
        self.content_hash = hashlib.sha256(content_bytes).hexdigest()[:6]
        
        # 生成纠缠值（基于当前状态和随机性）
        entanglement_value = hashlib.md5(
            (self.content_hash + str(time.time()) + str(uuid.uuid4())).encode()
        ).hexdigest()[:6]
        
        # 生成时间戳
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        
        # 构建量子基因编码
        self.quantum_gene = f"QG-QSM01-{content_type}-{timestamp}-{self.content_hash}-ENT{entanglement_value}"
        
        logger.info(f"生成内容量子基因编码: {self.quantum_gene}")
        return self.quantum_gene
    
    def apply_text_watermark(self, text_content):
        """为文本内容应用量子水印
        
        参数:
            text_content: 文本内容
            
        返回:
            带有量子水印的文本内容
        """
        if not self.quantum_gene:
            self.generate_content_quantum_gene(text_content, "TEXT")
        
        # 文本量子水印策略：
        # 1. 使用零宽字符嵌入量子基因编码
        # 2. 调整空格和换行的微小间距
        # 3. 在段落间插入不可见字符
        
        # 简化版：仅使用零宽空格和零宽连接符嵌入信息
        gene_binary = ''.join(format(ord(c), '08b') for c in self.quantum_gene)
        
        # 零宽字符集
        zwsp = '\u200b'  # 零宽空格
        zwj = '\u200d'   # 零宽连接符
        
        # 嵌入二进制量子基因编码
        result = ''
        current_pos = 0
        
        for i, char in enumerate(text_content):
            result += char
            
            # 在单词间和段落结束处嵌入水印
            if char in ' \n' and current_pos < len(gene_binary):
                # 根据基因位添加对应的零宽字符
                if gene_binary[current_pos] == '0':
                    result += zwsp
                else:
                    result += zwj
                current_pos += 1
                
                # 如果已嵌入所有基因位，再次从头开始（冗余）
                if current_pos >= len(gene_binary) and i < len(text_content) - 1:
                    current_pos = 0
        
        # 确保完整嵌入至少一次
        if current_pos < len(gene_binary):
            # 在文本末尾添加剩余编码
            for bit in gene_binary[current_pos:]:
                result += zwsp if bit == '0' else zwj
        
        logger.info(f"应用文本量子水印完成，内容长度: {len(text_content)} -> {len(result)}")
        return result
    
    def apply_image_watermark(self, image):
        """为图像应用量子水印
        
        参数:
            image: PIL图像对象或图像文件路径
            
        返回:
            带有量子水印的PIL图像对象
        """
        # 如果输入是路径，加载图像
        if isinstance(image, str):
            try:
                image = Image.open(image)
            except Exception as e:
                logger.error(f"无法加载图像: {e}")
                return None
        
        # 确保有量子基因编码
        if not self.quantum_gene:
            self.generate_content_quantum_gene(image.tobytes(), "IMAGE")
        
        # 复制图像以避免修改原图
        watermarked = image.copy()
        
        # 获取图像尺寸
        width, height = watermarked.size
        
        # 图像量子水印策略:
        # 1. 在图像最低有效位嵌入量子基因编码
        # 2. 在视觉上不明显的区域创建微小的编码模式
        
        # 转换为numpy数组以便处理
        try:
            img_array = np.array(watermarked)
            
            # 生成编码位图
            gene_binary = ''.join(format(ord(c), '08b') for c in self.quantum_gene)
            
            # 计算嵌入点
            points_count = min(len(gene_binary) * 3, width * height // 100)  # 使用不超过1%的像素
            
            # 使用量子基因创建伪随机种子
            seed = int(hashlib.md5(self.quantum_gene.encode()).hexdigest(), 16) % 1000000
            np.random.seed(seed)
            
            # 随机选择嵌入点
            x_coords = np.random.randint(0, width, points_count)
            y_coords = np.random.randint(0, height, points_count)
            
            # 嵌入量子基因编码位
            for i in range(len(gene_binary)):
                # 每个基因位在三个通道上各嵌入一次（冗余）
                for c in range(min(3, img_array.shape[2])):
                    if i * 3 + c < len(x_coords):
                        x, y = x_coords[i * 3 + c], y_coords[i * 3 + c]
                        
                        # 修改最低有效位
                        if gene_binary[i] == '1':
                            img_array[y, x, c] = img_array[y, x, c] | 1  # 设置最低位为1
                        else:
                            img_array[y, x, c] = img_array[y, x, c] & ~1  # 设置最低位为0
            
            # 转回PIL图像
            watermarked = Image.fromarray(img_array)
            
            logger.info(f"应用图像量子水印完成，尺寸: {width}x{height}，嵌入点: {points_count}")
            return watermarked
            
        except Exception as e:
            logger.error(f"应用图像水印失败: {e}")
            return image  # 返回原图
    
    def apply_document_watermark(self, document, output_format="pdf"):
        """为文档应用量子水印（适用于PDF等格式）
        
        参数:
            document: 文档内容或文件路径
            output_format: 输出格式
            
        返回:
            带有量子水印的文档字节流
        """
        # 此功能需要根据具体文档格式实现
        # 这里仅提供一个示例框架
        
        logger.info(f"文档水印功能尚未完全实现: {output_format}")
        
        # 生成量子基因编码
        if not self.quantum_gene:
            self.generate_content_quantum_gene(document, "DOC")
            
        # 对于PDF文档，可以通过添加不可见图层或元数据
        # 对于其他格式，需要特定的处理方法
        
        return document
    
    def apply_code_watermark(self, code):
        """为代码内容应用量子水印
        
        参数:
            code: 代码内容
            
        返回:
            带有量子水印的代码
        """
        if not self.quantum_gene:
            self.generate_content_quantum_gene(code, "CODE")
        
        # 代码量子水印策略:
        # 1. 在注释中嵌入不可见字符
        # 2. 微调空格和缩进
        # 3. 在代码块之间添加带编码的空行
        
        # 简化版：作为特殊注释嵌入
        watermarked_code = code
        
        # 检测代码语言以使用正确的注释格式
        lang_comment = {
            'py': '#',
            'js': '//',
            'java': '//',
            'c': '//',
            'cpp': '//',
            'html': '<!--',
            'css': '/*',
            'php': '//',
            'rb': '#',
            'go': '//',
            'rust': '//',
            'ts': '//'
        }
        
        # 尝试猜测语言
        lang = 'py'  # 默认Python
        for ext, comment in lang_comment.items():
            if f'.{ext}' in code.lower()[:100] or f'language="{ext}"' in code.lower()[:100]:
                lang = ext
                break
        
        # 创建带有零宽字符的量子注释
        comment_char = lang_comment.get(lang, '#')
        invisible_comment = f"{comment_char} "
        
        # 为每个量子基因字符添加一个零宽空格
        for c in self.quantum_gene:
            invisible_comment += c + '\u200b'
            
        # 根据语言添加注释结束符
        if lang in ['html']:
            invisible_comment += ' -->'
        elif lang in ['css']:
            invisible_comment += ' */'
        
        # 在合适的位置插入注释（尝试在文件开头或现有注释后）
        lines = watermarked_code.split('\n')
        
        # 找到适合插入的位置
        insert_pos = 0
        for i, line in enumerate(lines):
            if i == 0 and ('coding' in line or 'xml' in line or '<!DOCTYPE' in line):
                insert_pos = 1  # 跳过编码声明或XML声明
            elif not line.strip() or line.strip().startswith(comment_char):
                insert_pos = i + 1
        
        # 插入不可见注释
        lines.insert(insert_pos, invisible_comment)
        watermarked_code = '\n'.join(lines)
        
        logger.info(f"应用代码量子水印完成，代码行数: {len(lines)}，检测语言: {lang}")
        return watermarked_code
    
    def detect_watermark(self, content, content_type="AUTO"):
        """从内容中检测量子水印
        
        参数:
            content: 要检测的内容
            content_type: 内容类型，AUTO将自动检测
            
        返回:
            检测到的量子基因编码，如果没有则返回None
        """
        # 自动检测内容类型
        if content_type == "AUTO":
            if isinstance(content, str):
                if '<html' in content.lower()[:1000]:
                    content_type = "HTML"
                elif '<?xml' in content.lower()[:100]:
                    content_type = "XML"
                elif any(keyword in content.lower()[:1000] for keyword in ['function', 'class', 'def', 'var', 'import', 'package']):
                    content_type = "CODE"
                else:
                    content_type = "TEXT"
            elif isinstance(content, Image.Image) or (isinstance(content, str) and content.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp'))):
                content_type = "IMAGE"
            else:
                content_type = "BINARY"
        
        logger.info(f"开始检测量子水印，内容类型: {content_type}")
        
        # 根据内容类型执行不同的检测逻辑
        if content_type in ["TEXT", "HTML", "XML", "CODE"]:
            return self._detect_text_watermark(content)
        elif content_type == "IMAGE":
            return self._detect_image_watermark(content)
        else:
            logger.warning(f"不支持的内容类型: {content_type}")
            return None
    
    def _detect_text_watermark(self, text):
        """从文本内容中检测量子水印"""
        # 查找零宽字符编码
        zwsp = '\u200b'  # 零宽空格
        zwj = '\u200d'   # 零宽连接符
        
        # 提取零宽字符序列
        binary = ''
        for char in text:
            if char == zwsp:
                binary += '0'
            elif char == zwj:
                binary += '1'
        
        # 如果没有足够的零宽字符，返回None
        if len(binary) < 32:  # 至少需要几个字符才能形成有效的量子基因编码
            return None
        
        # 尝试从二进制序列中解码量子基因编码
        try:
            # 将二进制转换为字节
            byte_length = len(binary) // 8
            bytes_list = []
            
            for i in range(byte_length):
                byte = binary[i*8:(i+1)*8]
                if len(byte) == 8:  # 确保是完整的字节
                    bytes_list.append(int(byte, 2))
            
            # 尝试解码为字符串
            decoded = bytes(bytes_list).decode('utf-8', errors='ignore')
            
            # 查找量子基因编码模式
            import re
            pattern = r'QG-QSM01-[A-Z]+-\d{14}-[0-9a-f]{6}-ENT[0-9a-f]{6}'
            matches = re.findall(pattern, decoded)
            
            if matches:
                logger.info(f"检测到量子水印: {matches[0]}")
                return matches[0]
        except Exception as e:
            logger.error(f"解析文本水印失败: {e}")
        
        return None
    
    def _detect_image_watermark(self, image):
        """从图像中检测量子水印"""
        # 如果输入是路径，加载图像
        if isinstance(image, str):
            try:
                image = Image.open(image)
            except Exception as e:
                logger.error(f"无法加载图像: {e}")
                return None
        
        try:
            # 转换为numpy数组
            img_array = np.array(image)
            width, height = image.size
            
            # 尝试不同的种子值来寻找水印
            # 这是一种简化的方法，实际应用中可能需要更复杂的检测算法
            for seed_offset in range(10):  # 尝试几个种子值
                try:
                    # 设置随机种子
                    np.random.seed(1000000 + seed_offset)
                    
                    # 随机选择与嵌入时相同的点
                    points_count = min(1000, width * height // 100)  # 检查足够多的点
                    x_coords = np.random.randint(0, width, points_count)
                    y_coords = np.random.randint(0, height, points_count)
                    
                    # 提取最低有效位
                    binary = ''
                    for i in range(min(points_count // 3, 500)):  # 提取足够的数据
                        for c in range(min(3, img_array.shape[2])):
                            if i * 3 + c < len(x_coords):
                                x, y = x_coords[i * 3 + c], y_coords[i * 3 + c]
                                # 获取最低有效位
                                bit = img_array[y, x, c] & 1
                                binary += str(bit)
                    
                    # 同样尝试解码
                    byte_length = len(binary) // 8
                    bytes_list = []
                    
                    for i in range(byte_length):
                        byte = binary[i*8:(i+1)*8]
                        if len(byte) == 8:
                            bytes_list.append(int(byte, 2))
                    
                    # 尝试解码为字符串
                    decoded = bytes(bytes_list).decode('utf-8', errors='ignore')
                    
                    # 查找量子基因编码模式
                    import re
                    pattern = r'QG-QSM01-[A-Z]+-\d{14}-[0-9a-f]{6}-ENT[0-9a-f]{6}'
                    matches = re.findall(pattern, decoded)
                    
                    if matches:
                        logger.info(f"检测到图像量子水印: {matches[0]}")
                        return matches[0]
                except:
                    continue
        except Exception as e:
            logger.error(f"检测图像水印失败: {e}")
        
        return None
    
    def verify_quantum_gene(self, quantum_gene):
        """验证量子基因编码的有效性
        
        参数:
            quantum_gene: 要验证的量子基因编码
            
        返回:
            是否有效
        """
        import re
        pattern = r'^QG-QSM01-[A-Z]+-\d{14}-[0-9a-f]{6}-ENT[0-9a-f]{6}$'
        valid = bool(re.match(pattern, quantum_gene))
        
        logger.info(f"验证量子基因编码: {quantum_gene}, 结果: {'有效' if valid else '无效'}")
        return valid
    
    def create_scannable_watermark(self, content, include_qr=True):
        """创建可扫描的量子水印图像
        
        参数:
            content: 要处理的内容
            include_qr: 是否包含QR码
            
        返回:
            带有量子水印的图像对象
        """
        # 确保有量子基因编码
        if not self.quantum_gene:
            self.generate_content_quantum_gene(content)
        
        # 创建空白图像
        width, height = 600, 200
        if include_qr:
            width += 200  # 为QR码留出空间
            
        watermark = Image.new('RGB', (width, height), (255, 255, 255))
        draw = ImageDraw.Draw(watermark)
        
        try:
            # 加载字体，使用默认字体
            font = ImageFont.load_default()
            
            # 绘制量子基因编码
            draw.text((20, 20), "量子基因编码:", fill=(0, 0, 0), font=font)
            draw.text((20, 50), self.quantum_gene, fill=(0, 0, 128), font=font)
            
            # 绘制创建时间
            timestamp = self.quantum_gene.split('-')[3]
            year = timestamp[0:4]
            month = timestamp[4:6]
            day = timestamp[6:8]
            hour = timestamp[8:10]
            minute = timestamp[10:12]
            second = timestamp[12:14]
            
            time_str = f"创建时间: {year}年{month}月{day}日 {hour}:{minute}:{second}"
            draw.text((20, 80), time_str, fill=(0, 0, 0), font=font)
            
            # 绘制内容类型
            content_type = self.quantum_gene.split('-')[2]
            draw.text((20, 110), f"内容类型: {content_type}", fill=(0, 0, 0), font=font)
            
            # 绘制微小的量子模式（随机点阵）
            seed = int(hashlib.md5(self.quantum_gene.encode()).hexdigest(), 16) % 1000000
            np.random.seed(seed)
            
            for _ in range(1000):
                x = np.random.randint(0, width)
                y = np.random.randint(0, height)
                size = np.random.randint(1, 3)
                opacity = np.random.randint(10, 30)
                draw.point((x, y), fill=(0, 0, 200, opacity))
            
            # 添加QR码
            if include_qr:
                try:
                    import qrcode
                    qr = qrcode.QRCode(
                        version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_M,
                        box_size=5,
                        border=4,
                    )
                    qr.add_data(self.quantum_gene)
                    qr.make(fit=True)
                    
                    qr_img = qr.make_image(fill_color="black", back_color="white")
                    qr_img = qr_img.resize((180, 180))
                    
                    # 将QR码粘贴到右侧
                    watermark.paste(qr_img, (width - 190, 10))
                    
                except ImportError:
                    logger.warning("未安装qrcode模块，跳过QR码生成")
            
            return watermark
            
        except Exception as e:
            logger.error(f"创建可扫描水印失败: {e}")
            # 返回带有错误信息的图像
            draw.text((20, 150), f"Error: {str(e)}", fill=(255, 0, 0), font=font)
            return watermark
    
    def register_to_entanglement_network(self, quantum_gene, source_info=None):
        """将检测到的量子基因注册到量子纠缠网络
        
        参数:
            quantum_gene: 检测到的量子基因编码
            source_info: 源内容信息（可选）
            
        返回:
            是否成功注册
        """
        # 在实际实现中，这里会发送请求到量子纠缠注册中心
        # 此处为模拟实现
        
        logger.info(f"注册量子基因到纠缠网络: {quantum_gene}")
        
        # 验证量子基因编码的有效性
        if not self.verify_quantum_gene(quantum_gene):
            logger.error("无效的量子基因编码")
            return False
        
        # 模拟成功注册
        logger.info("成功注册到量子纠缠网络")
        return True


if __name__ == "__main__":
    # 简单的测试代码
    watermarker = QuantumWatermark()
    
    # 测试文本水印
    text = "这是一个测试文本，用于演示量子水印技术。量子叠加态模型的输出内容会自动嵌入量子基因编码。"
    watermarked_text = watermarker.apply_text_watermark(text)
    print(f"原始文本长度: {len(text)}, 水印后长度: {len(watermarked_text)}")
    
    # 检测水印
    detected_gene = watermarker.detect_watermark(watermarked_text, "TEXT")
    print(f"检测到的量子基因编码: {detected_gene}")
    
    # 创建可视化水印
    watermark_image = watermarker.create_scannable_watermark(text)
    watermark_image.save("quantum_watermark_example.png")
    print("已创建可扫描水印图像: quantum_watermark_example.png") 
"""
量子基因编码: QE-QUA-0C7F29389C04
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
"""