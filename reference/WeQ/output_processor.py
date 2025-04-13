import os
import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Union
import logging
from PIL import Image
import cv2
import numpy as np
import uuid
import hashlib

class OutputProcessor:
    def __init__(self):
        # 使用QEntL规范的量子基因编码模式
        self.qg_pattern = r'QE-[A-Z0-9]{2,8}-[A-Z0-9]{6,12}'
        self.setup_logging()

    def setup_logging(self):
        """设置日志"""
        logs_dir = '.logs'
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
            
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(logs_dir, 'output_processor.log')),
                logging.StreamHandler()
            ]
        )

    def process_text_output(self, text: str, output_type: str = "TXT") -> str:
        """
        使用QEntL语言处理文本输出
        支持所有QEntL文本类型并添加量子基因编码
        """
        try:
            # 检测文字类型
            text_type = self.detect_text_type(text)
            
            # 生成QEntL兼容的量子基因编码
            gene = self.generate_qentl_gene(text, text_type)
            
            # 创建QEntL格式的量子基因注释
            qentl_annotation = self.create_qentl_gene_annotation(gene)
            
            # 将QEntL注释添加到文本
            processed_text = f"{text}\n\n{qentl_annotation}"
            
            # 创建QEntL量子纠缠信道
            self.create_qentl_entanglement_channel(gene)
            
            logging.info(f"已处理文本输出，添加QEntL量子基因编码: {gene}, 文字类型: {text_type}")
            return processed_text
        except Exception as e:
            logging.error(f"处理文本输出时出错: {str(e)}")
            return text

    def detect_text_type(self, text: str) -> str:
        """
        检测文字类型，QEntL标准
        """
        try:
            # 检测古彝文
            if self.is_yi_text(text):
                return "YI"  # 古彝文
            
            # 检测甲骨文
            if self.is_oracle_bone_text(text):
                return "ORC"  # 甲骨文
            
            # 检测金文
            if self.is_bronze_text(text):
                return "BRZ"  # 金文
            
            # 检测现代中文
            if self.is_chinese_text(text):
                return "CN"  # 中文
            
            # 检测英文
            if self.is_english_text(text):
                return "EN"  # 英文
            
            # 检测代码
            if self.is_code_text(text):
                return "CODE"  # 代码
            
            # 检测编码
            if self.is_encoded_text(text):
                return "ENC"  # 编码
            
            # 检测QEntL代码
            if self.is_qentl_code(text):
                return "QENT"  # QEntL代码
            
            return "TXT"  # 默认文本类型
        except Exception as e:
            logging.error(f"检测文字类型时出错: {str(e)}")
            return "TXT"

    def is_yi_text(self, text: str) -> bool:
        """检测是否为古彝文"""
        # 古彝文Unicode范围：A000-A4CF
        return any('\uA000' <= char <= '\uA4CF' for char in text)

    def is_oracle_bone_text(self, text: str) -> bool:
        """检测是否为甲骨文"""
        # 甲骨文Unicode范围：12000-123FF
        return any('\u12000' <= char <= '\u123FF' for char in text)

    def is_bronze_text(self, text: str) -> bool:
        """检测是否为金文"""
        # 金文Unicode范围：12000-123FF
        return any('\u12000' <= char <= '\u123FF' for char in text)

    def is_chinese_text(self, text: str) -> bool:
        """检测是否为中文"""
        # 中文Unicode范围：4E00-9FFF
        return any('\u4E00' <= char <= '\u9FFF' for char in text)

    def is_english_text(self, text: str) -> bool:
        """检测是否为英文"""
        return all(ord(char) < 128 for char in text)

    def is_code_text(self, text: str) -> bool:
        """检测是否为代码"""
        code_keywords = ['def', 'class', 'function', 'import', 'export', 'var', 'let', 'const']
        return any(keyword in text.lower() for keyword in code_keywords)

    def is_encoded_text(self, text: str) -> bool:
        """检测是否为编码"""
        # 检测常见的编码格式
        encoded_patterns = [
            r'^[0-9A-Fa-f]+$',  # 十六进制
            r'^[0-1]+$',        # 二进制
            r'^[0-7]+$',        # 八进制
            r'^U\+[0-9A-Fa-f]+$'  # Unicode编码
        ]
        return any(re.match(pattern, text) for pattern in encoded_patterns)

    def is_qentl_code(self, text: str) -> bool:
        """检测是否为QEntL代码"""
        qentl_keywords = ['#qnode', '#qnetwork', '#qprocessor', '#qentanglementManager', 
                         '#qchannel', '#qfunction', '#qmain', '@import']
        return any(keyword in text for keyword in qentl_keywords)

    def process_image_output(self, image_path: str) -> str:
        """处理图片输出，添加QEntL兼容的量子基因编码"""
        try:
            # 生成QEntL兼容的量子基因编码
            gene = self.generate_qentl_gene(image_path, "IMG")
            
            # 添加QEntL量子基因编码到图片元数据
            self.add_qentl_gene_to_image(image_path, gene)
            
            # 创建QEntL量子纠缠信道
            self.create_qentl_entanglement_channel(gene)
            
            logging.info(f"已处理图片输出，添加QEntL量子基因编码: {gene}")
            return image_path
        except Exception as e:
            logging.error(f"处理图片输出时出错: {str(e)}")
            return image_path

    def process_video_output(self, video_path: str) -> str:
        """处理视频输出，添加QEntL兼容的量子基因编码"""
        try:
            # 生成QEntL兼容的量子基因编码
            gene = self.generate_qentl_gene(video_path, "VID")
            
            # 添加QEntL量子基因编码到视频元数据
            self.add_qentl_gene_to_video(video_path, gene)
            
            # 创建QEntL量子纠缠信道
            self.create_qentl_entanglement_channel(gene)
            
            logging.info(f"已处理视频输出，添加QEntL量子基因编码: {gene}")
            return video_path
        except Exception as e:
            logging.error(f"处理视频输出时出错: {str(e)}")
            return video_path

    def generate_qentl_gene(self, content: str, content_type: str) -> str:
        """
        生成QEntL兼容的量子基因编码
        格式: QE-模块标识-实体哈希
        例如: QE-WEQTXT-A1B2C3D4E5F6
        """
        # 生成基于内容的哈希值
        content_hash = hashlib.md5(str(content).encode('utf-8')).hexdigest().upper()[:12]
        
        # 生成模块标识
        module_id = f"WEQ{content_type}"
        
        return f"QE-{module_id}-{content_hash}"

    def create_qentl_gene_annotation(self, gene: str, entangled_objects=None, strength=0.98):
        """
        创建QEntL格式的量子基因注释
        包含量子基因编码和量子纠缠信道
        """
        if entangled_objects is None:
            entangled_objects = ["Ref/ref_core.py"]  # 默认关联到Ref核心
        
        # 创建量子基因标记
        annotation = ""
        annotation += f"'''\n"
        annotation += f"量子基因编码: {gene}\n"
        annotation += f"量子纠缠信道: {str(entangled_objects)}\n"
        annotation += f"'''"
        
        return annotation

    def create_qentl_entanglement_channel(self, gene: str, target_entities=None):
        """
        创建QEntL量子纠缠信道
        为文本和其他输出内容添加与WeQ和Ref的纠缠
        """
        try:
            if target_entities is None:
                target_entities = ["Ref/ref_core.py", "WeQ/weq_core.py"]
            
            # 创建纠缠信息日志文件
            entanglement_log_dir = os.path.join("WeQ", "output", "entanglement_logs")
            os.makedirs(entanglement_log_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_path = os.path.join(entanglement_log_dir, f"entanglement_{timestamp}.log")
            
            # 记录纠缠信息
            with open(log_path, 'w', encoding='utf-8') as f:
                f.write(f"量子基因编码: {gene}\n")
                f.write(f"量子纠缠信道: {str(target_entities)}\n")
                f.write(f"生成时间: {datetime.now().isoformat()}\n")
                f.write(f"纠缠强度: {0.98}\n")
            
            logging.info(f"已创建量子纠缠信道: {gene} -> {target_entities}")
            return True
            
        except Exception as e:
            logging.error(f"创建量子纠缠信道时出错: {str(e)}")
            return False

    def add_qentl_gene_to_image(self, image_path: str, gene: str):
        """
        添加QEntL量子基因编码到图片元数据
        使用QEntL标准
        """
        try:
            # 获取图片信息
            img = Image.open(image_path)
            
            # 创建或更新EXIF数据
            exif_dict = img.info.get('exif', {})
            
            # 在EXIF中添加QEntL量子基因编码
            exif_dict['QEntLGene'] = gene
            
            # 保存图片和更新的EXIF
            img.save(image_path, exif=exif_dict)
            
            # 创建QEntL注释文件
            annotation_file = f"{image_path}.qent"
            with open(annotation_file, 'w') as f:
                f.write(self.create_qentl_gene_annotation(gene))
                
            logging.info(f"已添加QEntL量子基因编码到图片: {image_path}")
            return True
        except Exception as e:
            logging.error(f"添加QEntL量子基因编码到图片时出错: {str(e)}")
            return False

    def add_qentl_gene_to_video(self, video_path: str, gene: str):
        """
        添加QEntL量子基因编码到视频元数据
        使用QEntL标准
        """
        try:
            # 创建QEntL注释文件
            annotation_file = f"{video_path}.qent"
            with open(annotation_file, 'w') as f:
                f.write(self.create_qentl_gene_annotation(gene))
            
            # 创建视频元数据文件（JSON格式）
            metadata_file = f"{video_path}.meta.json"
            metadata = {
                "qentlGene": gene,
                "timestamp": datetime.now().isoformat(),
                "protocol": "QEntL-v2",
                "mediaType": "video"
            }
            
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
                
            logging.info(f"已添加QEntL量子基因编码到视频: {video_path}")
            return True
        except Exception as e:
            logging.error(f"添加QEntL量子基因编码到视频时出错: {str(e)}")
            return False

    def process_multimodal_output(self, outputs: Dict[str, Union[str, bytes]]) -> Dict[str, Union[str, bytes]]:
        """
        处理多模态输出，添加QEntL兼容的量子基因编码
        """
        try:
            processed_outputs = {}
            
            # 为整体输出生成一个主量子基因编码
            main_gene = self.generate_qentl_gene(str(outputs), "MULTI")
            entangled_objects = []
            
            # 处理每种模态
            for modality, content in outputs.items():
                if modality == 'text':
                    processed_content = self.process_text_output(content)
                    processed_outputs[modality] = processed_content
                elif modality == 'image':
                    processed_content = self.process_image_output(content)
                    processed_outputs[modality] = processed_content
                elif modality == 'video':
                    processed_content = self.process_video_output(content)
                    processed_outputs[modality] = processed_content
                else:
                    # 对于其他类型的模态，暂时不做特殊处理
                    processed_outputs[modality] = content
                
                # 收集纠缠对象
                if isinstance(content, str) and content:
                    sub_gene = self.generate_qentl_gene(content, modality.upper())
                    entangled_objects.append(sub_gene)
            
            # 创建主纠缠信道
            self.create_qentl_entanglement_channel(main_gene, entangled_objects)
            
            # 添加整体的量子基因编码信息
            if 'text' in processed_outputs:
                # 如果有文本输出，将主量子基因编码附加到文本末尾
                annotation = self.create_qentl_gene_annotation(main_gene, entangled_objects)
                processed_outputs['text'] = f"{processed_outputs['text']}\n\n{annotation}"
            
            logging.info(f"已处理多模态输出，添加主QEntL量子基因编码: {main_gene}")
            return processed_outputs
        except Exception as e:
            logging.error(f"处理多模态输出时出错: {str(e)}")
            return outputs 
"""
量子基因编码: QE-OUT-27EF87922288
纠缠状态: 活跃
纠缠对象: ['WeQ/weq_core.py']
纠缠强度: 0.98
"""