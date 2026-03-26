#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建正确的QBC量子字节码文件
用于QEntL量子虚拟机
"""

import os

# QBC格式：魔数(4字节) + 源代码
MAGIC = b'QBC\x01'

# 读取.qentl源文件
qentl_path = '/root/QSM/Models/QSM/src/qsm_neural_network.qentl'
with open(qentl_path, 'r', encoding='utf-8') as f:
    source_code = f.read()

# 创建QBC文件
output_path = '/root/QSM/QEntL/dist/models/qsm_neural_network_v2.qbc'
with open(output_path, 'wb') as f:
    f.write(MAGIC)
    f.write(source_code.encode('utf-8'))

print(f'✓ QBC文件已创建: {output_path}')
print(f'  魔数: {MAGIC.hex()}')
print(f'  源代码长度: {len(source_code)} 字符')
