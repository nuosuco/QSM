#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
将旧文件移动到参考目录的脚本
设置30天后自动删除
"""

import os
import time
import shutil
from pathlib import Path
import json
from datetime import datetime, timedelta

# 量子基因编码
QG_CODE = "QG-UTIL-REF-MOVE-A1B2"

# 量子纠缠信道
QE_CHANNEL = "QE-UTIL-REF-" + str(int(time.time()))

# 设置项目根目录
ROOT_DIR = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 参考文件目录
REF_DIR = ROOT_DIR / "reference_files"

# 需要移动的旧文件列表
MOVE_FILES = [
    # 旧的HTML模板文件
    "world/templates/base.html",
    "world/templates/components/nav.html",
    "world/templates/components/footer.html",
    "world/templates/components/quantum_ui/loader.html",
    
    # 旧的JavaScript文件
    "world/static/js/quantum_entanglement/core.js",
    "world/static/js/quantum_entanglement/client.js",
    "world/static/js/global.js",
    
    # 旧的CSS文件
    "world/static/css/normalize.css",
    "world/static/css/global.css",
    
    # 旧的Python文件
    "world/api/qsm_api.py",
    "world/api/weq_api.py",
    "world/api/som_api.py",
    "world/utils/model_utils.py",
    "world/utils/data_utils.py",
    "scripts/services/WeQ_start_services.py",
    
    # 旧的文档文件
    "docs/components/README.md",
    "docs/api/README.md",
    "docs/architecture/architecture.md",
    "docs/architecture/template.md",
    
    # 旧的配置文件
    "config/default.json",
    "config/development.json",
    "config/production.json",
    
    # 旧的测试文件
    "tests/unit/test_qsm.py",
    "tests/integration/test_weq.py"
]

# 需要保留的新文件列表(不会被移动)
KEEP_FILES = [
    # 新的QENTL模板文件
    "world/templates/base.qentl",
    "world/templates/components/quantum_ui/*.qentl",
    "world/templates/test/*.qentl",
    "docs/architecture/*.qentl",
    
    # 新的QCSS样式文件
    "world/static/css/*.qcss",
    
    # 新的QJS脚本文件
    "world/static/js/quantum_entanglement/*.qjs",
    
    # 新的QPY文件
    "world/api/*.qpy",
    "world/utils/*.qpy",
    "scripts/services/*.qpy"
]

def should_move_file(file_path):
    """判断文件是否需要移动到参考目录"""
    rel_path = str(file_path.relative_to(ROOT_DIR)).replace('\\', '/')
    
    # 如果文件在保留列表中,不移动
    for keep_pattern in KEEP_FILES:
        if Path(rel_path).match(keep_pattern):
            return False
        
    # 如果文件在移动列表中,或者是旧的文件类型,则移动
    return (rel_path in MOVE_FILES or
            file_path.suffix in ['.html', '.js', '.css', '.py', '.md', '.json'] and
            not file_path.suffix in ['.qentl', '.qcss', '.qjs', '.qpy'])

def create_reference_info():
    """创建参考文件信息"""
    return {
        "created_date": datetime.now().isoformat(),
        "delete_date": (datetime.now() + timedelta(days=30)).isoformat(),
        "quantum_gene": QG_CODE,
        "quantum_channel": QE_CHANNEL
    }

def move_to_reference():
    """移动文件到参考目录"""
    print(f"开始移动文件到参考目录: {REF_DIR}")
    
    # 创建参考目录
    REF_DIR.mkdir(exist_ok=True)
    
    # 创建参考信息文件
    ref_info = create_reference_info()
    with open(REF_DIR / "reference_info.json", "w", encoding="utf-8") as f:
        json.dump(ref_info, f, indent=2, ensure_ascii=False)
    
    # 移动文件
    for file_path in MOVE_FILES:
        src = ROOT_DIR / file_path
        if not src.exists():
            print(f"文件不存在,跳过: {file_path}")
            continue
            
        # 创建目标目录
        dst_dir = REF_DIR / src.parent.relative_to(ROOT_DIR)
        dst_dir.mkdir(parents=True, exist_ok=True)
        
        # 移动文件
        dst = dst_dir / src.name
        shutil.copy2(src, dst)
        print(f"已复制文件: {file_path} -> {dst.relative_to(ROOT_DIR)}")

if __name__ == "__main__":
    move_to_reference() 