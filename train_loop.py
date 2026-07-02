#!/usr/bin/env python3
"""QEntL全栈训练循环 — 对首字节0x14的.qbc执行3次epoch"""
import subprocess, os, sys, glob, struct

ROOT = "/root/QSM"
QBC_DIR = os.path.join(ROOT, "QEntL")
QVM = os.path.join(ROOT, "bin", "qvm_bootstrap")
EPOCHS = 3

def find_valid_qbc():
    """找首字节为0x14的.qbc文件"""
    valid = []
    for f in sorted(glob.glob(os.path.join(QBC_DIR, "**", "*.qbc"), recursive=True)):
        with open(f, "rb") as fh:
            first = fh.read(1)
            if first == b'\x14':
                valid.append(f)
    return valid

def classify_model(path):
    """根据路径分类模型"""
    rel = path.replace(ROOT, "")
    if "/Ref/" in rel or rel.startswith("/Ref"):
        return "Ref"
    if "/SOM/" in rel or rel.startswith("/SOM"):
        return "SOM"
    if "/WeQ/" in rel or rel.startswith("/WeQ"):
        return "WeQ"
    if "/QNS/" in rel or rel.startswith("/QNS"):
        return "QNS"
    if "/QDFS/" in rel or rel.startswith("/QDFS"):
        return "QDFS"
    if "/QSM/" in rel or rel.startswith("/QSM"):
        return "QSM"
    # 默认看文件名
    base = os.path.basename(path)
    for m in ["QSM","Ref","SOM","WeQ","QNS","QDFS"]:
        if m.lower() in base.lower():
            return m
    return "QSM"  # 默认

def run_circuit(path):
    """运行一次qvm_bootstrap，解析输出中的周期数和门数"""
    try:
        r = subprocess.run([QVM, path], capture_output=True, text=True, timeout=30)
        output = r.stdout + r.stderr
        cycles = 0
        gates = 0
        # 尝试解析常见输出格式
        import re
        m_cyc = re.search(r'(\d+)\s*周期', output)
        m_gate = re.search(r'(\d+)\s*门操作', output)
        if not m_cyc:
            m_cyc = re.search(r'[Cc]ycle[s]?\s*[:=]?\s*(\d+)', output)
        if not m_gate:
            m_gate = re.search(r'[Gg]ate[s]?\s*[:=]?\s*(\d+)', output)
        if m_cyc:
            cycles = int(m_cyc.group(1))
        if m_gate:
            gates = int(m_gate.group(1))
        return cycles, gates, r.returncode, output[:500]
    except subprocess.TimeoutExpired:
        return 0, 0, -1, "TIMEOUT"
    except Exception as e:
        return 0, 0, -1, str(e)

def main():
    valid = find_valid_qbc()
    print(f"有效电路数(首字节0x14): {len(valid)}")
    
    total_cycles = 0
    total_gates = 0
    failures = 0
    details = []  # (name, cycles, gates, status)
    model_stats = {}  # model -> {cycles, gates, count, fails}
    
    for i, path in enumerate(valid):
        name = os.path.basename(path)
        model = classify_model(path)
        if model not in model_stats:
            model_stats[model] = {"cycles":0,"gates":0,"count":0,"fails":0}
        
        c_sum = 0
        g_sum = 0
        circuit_fail = False
        
        for ep in range(EPOCHS):
            cyc, gat, rc, out = run_circuit(path)
            if rc != 0:
                circuit_fail = True
                failures += 1
                model_stats[model]["fails"] += 1
            c_sum += cyc
            g_sum += gat
        
        total_cycles += c_sum
        total_gates += g_sum
        model_stats[model]["cycles"] += c_sum
        model_stats[model]["gates"] += g_sum
        model_stats[model]["count"] += 1
        
        status = "FAIL" if circuit_fail else "OK"
        details.append((name, c_sum, g_sum, status))
        
        if (i+1) % 20 == 0 or i == 0:
            print(f"  [{i+1}/{len(valid)}] {name} -> cycles={c_sum} gates={g_sum} {status}")
    
    print("\n" + "="*60)
    print("【训练报告】")
    print(f"- 有效电路数: {len(valid)}个")
    print(f"- Epoch数: {EPOCHS}")
    print(f"- 总执行次数: {len(valid)}×{EPOCHS} = {len(valid)*EPOCHS}")
    print(f"- 总周期数: {total_cycles}")
    print(f"- 总门操作数: {total_gates}")
    print(f"- 失败数: {failures}/{len(valid)*EPOCHS}")
    print()
    print("Per-circuit详情表（电路名|周期|门数|状态）：")
    print(f"{'电路名':<45}{'周期':>8}{'门数':>8}{'状态':>6}")
    print("-"*70)
    for name, cyc, gat, st in details:
        print(f"{name:<45}{cyc:>8}{gat:>8}{st:>6}")
    print()
    print("按模型分类统计：")
    print(f"{'模型':<10}{'电路数':>8}{'周期':>10}{'门数':>10}{'失败':>6}")
    print("-"*50)
    for m in sorted(model_stats.keys()):
        s = model_stats[m]
        print(f"{m:<10}{s['count']:>8}{s['cycles']:>10}{s['gates']:>10}{s['fails']:>6}")
    print()
    print(f"状态: {'完成' if failures==0 else '完成(有失败)'}")

if __name__ == "__main__":
    main()
