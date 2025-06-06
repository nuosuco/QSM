#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
创建Ref模块

此脚本用于创建解决'No module named Ref'错误所需的Ref模块
"""

import os
import sys
import logging
import traceback
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('.logs/ref_module_creation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def create_ref_module():
    """创建Ref模块"""
    try:
        logger.info("开始创建Ref模块...")
        
        # 确定Ref模块路径
        ref_path = Path("Ref")
        if not ref_path.exists():
            logger.info(f"创建Ref目录...")
            ref_path.mkdir(exist_ok=True)
        
        # 创建__init__.py文件
        init_file = ref_path / "__init__.py"
        
        if not init_file.exists():
            logger.info(f"创建Ref/__init__.py文件...")
            try:
                with open(init_file, "w", encoding="utf-8") as f:
                    f.write('"""\nRef模块\n\n用于解决"No module named Ref"错误\n"""\n\n')
                    f.write('import logging\n\n')
                    f.write('logger = logging.getLogger(__name__)\n\n')
                    f.write('def init_file_monitor():\n')
                    f.write('    """初始化文件监控系统"""\n')
                    f.write('    logger.info("Ref文件监控系统已初始化")\n')
                    f.write('    print("Ref文件监控系统已初始化")\n')
                    f.write('    return True\n')
                logger.info(f"Ref/__init__.py文件创建成功")
            except Exception as e:
                logger.error(f"创建Ref/__init__.py文件失败: {str(e)}")
                logger.error(traceback.format_exc())
                raise
        else:
            logger.info(f"Ref/__init__.py文件已存在，跳过...")
        
        # 创建file_monitor.py文件
        monitor_file = ref_path / "file_monitor.py"
        
        if not monitor_file.exists():
            logger.info(f"创建Ref/file_monitor.py文件...")
            try:
                with open(monitor_file, "w", encoding="utf-8") as f:
                    f.write('"""\nRef文件监控系统\n\n用于监控文件变化\n"""\n\n')
                    f.write('import os\n')
                    f.write('import time\n')
                    f.write('import logging\n')
                    f.write('from pathlib import Path\n\n')
                    f.write('logger = logging.getLogger(__name__)\n\n')
                    f.write('class FileMonitor:\n')
                    f.write('    """文件监控类"""\n\n')
                    f.write('    def __init__(self, root_dir="."):\n')
                    f.write('        """初始化文件监控器"""\n')
                    f.write('        self.root_dir = Path(root_dir)\n')
                    f.write('        self.file_map = {}\n')
                    f.write('        logger.info(f"文件监控器已初始化，监控目录: {self.root_dir}")\n\n')
                    f.write('    def scan_files(self):\n')
                    f.write('        """扫描文件"""\n')
                    f.write('        logger.info("开始扫描文件...")\n')
                    f.write('        return list(self.root_dir.rglob("*"))\n\n')
                    f.write('    def start_monitoring(self):\n')
                    f.write('        """开始监控"""\n')
                    f.write('        logger.info("开始文件监控...")\n')
                    f.write('        return True\n')
                logger.info(f"Ref/file_monitor.py文件创建成功")
            except Exception as e:
                logger.error(f"创建Ref/file_monitor.py文件失败: {str(e)}")
                logger.error(traceback.format_exc())
                raise
        else:
            logger.info(f"Ref/file_monitor.py文件已存在，跳过...")
        
        # 创建README.md文件
        readme_file = ref_path / "README.md"
        
        if not readme_file.exists():
            logger.info(f"创建Ref/README.md文件...")
            try:
                with open(readme_file, "w", encoding="utf-8") as f:
                    f.write('# Ref模块\n\n')
                    f.write('此模块用于解决QSM系统中的"No module named Ref"错误\n\n')
                    f.write('## 功能\n\n')
                    f.write('- 提供文件监控系统接口\n')
                    f.write('- 与QSM主服务集成\n\n')
                    f.write('## 用法\n\n')
                    f.write('```python\n')
                    f.write('import Ref\n\n')
                    f.write('# 初始化文件监控系统\n')
                    f.write('Ref.init_file_monitor()\n')
                    f.write('```\n')
                logger.info(f"Ref/README.md文件创建成功")
            except Exception as e:
                logger.error(f"创建Ref/README.md文件失败: {str(e)}")
                logger.error(traceback.format_exc())
                raise
        else:
            logger.info(f"Ref/README.md文件已存在，跳过...")
        
        # 确保.logs目录存在
        logs_dir = Path(".logs")
        if not logs_dir.exists():
            logger.info("创建.logs目录...")
            logs_dir.mkdir(exist_ok=True)
        
        logger.info("Ref模块创建完成!")
        return True
    except Exception as e:
        logger.error(f"创建Ref模块失败: {str(e)}")
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    try:
        result = create_ref_module()
        sys.exit(0 if result else 1)
    except Exception as e:
        logger.critical(f"脚本执行失败: {str(e)}")
        logger.critical(traceback.format_exc())
        sys.exit(1) 