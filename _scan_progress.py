#!/usr/bin/env python3
"""统计 QSM 项目进度：.qentl + .qbc"""
import os, struct, glob, re

ROOT = "/root/QSM"
# 排除目录
EXCLUDE_DIRS = {'.git', '__pycache__', '.ipynb_checkpoints', 'venv', '.venv',
                'node_modules', 'dist', 'build/compiled', 'env', '.hermes'}

def walk_files(suffix):
    results = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        rel = os.path.relpath(dirpath, ROOT)
        parts = rel.replace('\\','/').split('/')
        if any(p in EXCLUDE_DIRS for p in parts):
            dirnames.clear()
            continue
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for fn in filenames:
            if fn.endswith(suffix):
                fp = os.path.join(dirpath, fn)
                sz = os.path.getsize(fp)
                if sz > 0:
                    results.append((fp, sz))
    return results

# ===== .qentl =====
qentl_files = walk_files('.qentl')
total_lines_qentl = 0
total_size_qentl = 0
def_count_qentl = 0
quantum_keywords = ['qubit','qubits','H','X','Y','Z','S','T','Sdg','Tdg','CNOT',
                    'CZ','SWAP','Toffoli','CCNOT','MCX','measure','measure_q',
                    'qreg','qalloc','qfree','entangle','teleport','superpose','gate',
                    'quantum','qcircuit','qstate','qvector','qmatrix','qop','quantum_add',
                    'qft','iqft','grover','shor','vQE','QPE','QAOA','quantum_kernel',
                    'qfeature','hadamard','phase','rotation','RX','RY','RZ','U','U1','U2','U3',
                    'CRX','CRY','CRZ','CRot','qrotate','qphase','qctrl','dcx','rxx','ryy','rzz',
                    'unitary','statevector','bloch','qchannel','qml','qnn','qsvm']
qkw_lower = set(k.lower() for k in quantum_keywords)
qkw_count_qentl = 0

for fp, sz in qentl_files:
    total_size_qentl += sz
    try:
        with open(fp, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.read().splitlines()
        total_lines_qentl += len(lines)
        for ln in lines:
            s = ln.strip().lower()
            if re.match(r'^\s*def\s+', ln):
                def_count_qentl += 1
            # count quantum keyword occurrences in code lines (skip pure comments/blanks)
            if s and not s.startswith('#'):
                for kw in qkw_lower:
                    qkw_count_qentl += s.count(kw)
    except Exception:
        pass

# ===== .qbc =====
qbc_files = walk_files('.qbc')
valid_0x14_count = 0
has_qinstr_count = 0
def_count_qbc = 0
end_count_qbc = 0
qinstr_count_qbc = 0  # 0x01-0x08 in code region
total_code_bytes = 0
total_size_qbc = 0

QUANTUM_OPS = set(range(0x01, 0x09))  # 0x01..0x08

for fp, sz in qbc_files:
    total_size_qbc += sz
    try:
        with open(fp, 'rb') as f:
            data = f.read()
    except Exception:
        continue
    if len(data) < 1:
        continue
    if data[0] == 0x14:
        valid_0x14_count += 1

    # Parse: code_bytes + sp_len(2B LE) + string_pool
    # Find code region: bytes up to the 2B LE that equals remaining length
    code = b''
    sp_len = None
    found = False
    for i in range(0, len(data) - 1):
        candidate = data[i] | (data[i+1] << 8)
        if i + 2 + candidate == len(data):
            code = data[:i]
            sp_len = candidate
            found = True
            break
    if not found:
        # fallback: whole file is code
        code = data

    total_code_bytes += len(code)
    for b in code:
        if b == 0x66:
            def_count_qbc += 1
        elif b == 0x67:
            end_count_qbc += 1
        elif 0x01 <= b <= 0x08:
            qinstr_count_qbc += 1
            has_qinstr_count_local = True

    if any(0x01 <= b <= 0x08 for b in code):
        has_qinstr_count += 1

# ===== Compute totals =====
file_total = len(qentl_files) + len(qbc_files)
func_total = def_count_qentl + def_count_qbc
qinstr_total = qkw_count_qentl + qinstr_count_qbc

pair_rate = (end_count_qbc / def_count_qbc * 100) if def_count_qbc else 0

print("=" * 55)
print("QSM 项目进度统计")
print("=" * 55)
print(f"扫描目录: {ROOT}")
print()
print("### 文件总数")
print(f".qentl 总数:        {len(qentl_files)}")
print(f".qbc 总数:          {len(qbc_files)}")
print(f"文件合计:           {file_total}")
print()
print("### .qentl 源码统计")
print(f"总代码行数:         {total_lines_qentl:,} 行")
print(f"总文件大小:         {total_size_qentl:,} 字节 ({total_size_qentl/1024/1024:.1f} MB)")
print(f"代码区函数总数(def): {def_count_qentl}")
print(f"量子指令关键词数:   {qkw_count_qentl:,}")
print()
print("### .qbc 字节码统计")
print(f"有效0x14首字节文件: {valid_0x14_count}")
print(f"含量子指令文件数:   {has_qinstr_count}")
print(f"代码区 DEF(0x66):   {def_count_qbc}")
print(f"代码区 END(0x67):   {end_count_qbc} (配对率 {pair_rate:.1f}%)")
print(f"代码区 DEF+END总数: {def_count_qbc + end_count_qbc}")
print(f"量子指令总数(0x01-0x08): {qinstr_count_qbc:,}")
print(f"代码字节量:         {total_code_bytes:,} 字节")
print(f"总文件大小:         {total_size_qbc:,} 字节 ({total_size_qbc/1024:.1f} KB)")
print()
print("### 汇总")
print(f"函数总数:           {func_total}（.qentl def {def_count_qentl} + .qbc DEF {def_count_qbc}）")
print(f"量子指令总数:       {qinstr_total:,}（.qentl门引用 {qkw_count_qentl} + .qbc 0x01-0x08 {qinstr_count_qbc:,}）")
