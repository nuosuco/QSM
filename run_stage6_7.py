#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QEntL全栈 阶段6(关键电路验证) + 阶段7(QNS全栈训练循环)"""
import os
import sys
import subprocess
import re
import json
from collections import OrderedDict

ROOT = "/root/QSM"
QVM = os.path.join(ROOT, "bin", "qvm_bootstrap")

# ============ 阶段6 组件目录 ============
STAGE6_COMPONENTS = OrderedDict([
    ("QNS",           "QEntL/System/Kernel/neural"),
    ("QDFS",          "QEntL/System/Kernel/filesystem"),
    ("四大模型",       "QEntL/Models"),
    ("Platform",      "QEntL/System/Platform"),
    ("Deployment",    "QEntL/System/VM/src/deployment"),
])

def find_0x14_files(topdir):
    """os.walk 遍历，返回首字节 0x14 的 .qbc 相对路径列表"""
    abs_top = os.path.join(ROOT, topdir)
    if not os.path.isdir(abs_top):
        return []
    out = []
    for root, dirs, files in os.walk(abs_top):
        for fn in files:
            if not fn.endswith(".qbc"):
                continue
            fpath = os.path.join(root, fn)
            try:
                with open(fpath, "rb") as fh:
                    if fh.read(1) == b"\x14":
                        out.append(os.path.relpath(fpath, ROOT))
            except Exception:
                pass
    out.sort()
    return out

def find_all_0x14_files():
    """全仓库 0x14 头 .qbc"""
    out = []
    for root, dirs, files in os.walk(ROOT):
        for fn in files:
            if not fn.endswith(".qbc"):
                continue
            fpath = os.path.join(root, fn)
            try:
                with open(fpath, "rb") as fh:
                    if fh.read(1) == b"\x14":
                        out.append(os.path.relpath(fpath, ROOT))
            except Exception:
                pass
    out.sort()
    return out

def parse_qvm_output(stdout, stderr):
    """从 QVM 输出提取周期数和门数"""
    cycles = 0
    gates = 0
    combined = (stdout or "") + "\n" + (stderr or "")
    m = re.search(r"(\d+)\s*周期", combined)
    if m:
        cycles = int(m.group(1))
    m = re.search(r"(\d+)\s*门", combined)
    if m:
        gates = int(m.group(1))
    # 也匹配 "0 门操作" / "0 周期" 之类的变体
    m2 = re.search(r"执行完成:\s*(\d+)\s*周期\s*,\s*(\d+)\s*门", combined)
    if m2:
        cycles = int(m2.group(1))
        gates = int(m2.group(2))
    return cycles, gates

def run_qvm(fpath, timeout=30):
    """运行 qvm_bootstrap，返回 (pass, cycles, gates, error_msg)"""
    abs_path = os.path.join(ROOT, fpath)
    try:
        res = subprocess.run(
            [QVM, abs_path],
            capture_output=True, text=True, timeout=timeout,
            cwd=ROOT,
        )
        cycles, gates = parse_qvm_output(res.stdout, res.stderr)
        # 判定：执行完成即 PASS；timeout/异常即 FAIL
        if res.returncode != 0 and "执行完成" not in res.stdout:
            return False, cycles, gates, res.stderr.strip()
        return True, cycles, gates, ""
    except subprocess.TimeoutExpired as e:
        return False, 0, 0, f"超时({timeout}s)"
    except Exception as e:
        return False, 0, 0, str(e)

# ============ 阶段6 ============
def stage6():
    print("=" * 70)
    print("阶段6：关键电路验证")
    print("=" * 70)
    total_pass = total_fail = total_cycles = total_gates = 0
    failures = []
    for name, comp_dir in STAGE6_COMPONENTS.items():
        files = find_0x14_files(comp_dir)
        print(f"\n【{name}】({comp_dir}) — 共 {len(files)} 个 0x14 电路")
        if not files:
            print("  (无 0x14 头文件，跳过)")
            continue
        cp = fp = cc = cg = 0
        for f in files:
            ok, cy, ga, err = run_qvm(f)
            status = "PASS" if ok else "FAIL"
            if ok:
                cp += 1; cc += cy; cg += ga
            else:
                fp += 1; failures.append(f"  ❌ {f} — {err}")
            print(f"  [{status}] {f}  周期={cy} 门={ga}")
        print(f"  → 小计: PASS={cp} FAIL={fp} 周期={cc} 门={cg}")
        total_pass += cp; total_fail += fp
        total_cycles += cc; total_gates += cg

    print("\n" + "-" * 50)
    print("阶段6 汇总:")
    print(f"  PASS={total_pass}  FAIL={total_fail}")
    print(f"  总周期={total_cycles}  总门数={total_gates}")
    if failures:
        print("  失败列表:")
        for x in failures:
            print(x)
    return total_pass, total_fail, total_cycles, total_gates

# ============ 阶段7 ============
def stage7():
    print("\n" + "=" * 70)
    print("阶段7：QNS全栈训练循环（全仓库 0x14 头电路 × 3 epoch）")
    print("=" * 70)
    all_files = find_all_0x14_files()
    n = len(all_files)
    print(f"全仓库 0x14 头电路共 {n} 个")

    total_pass = total_fail = total_cycles = total_gates = 0
    failures = []

    for epoch in range(1, 4):
        print(f"\n  Epoch {epoch}/3")
        ep_pass = ep_fail = ep_cy = ep_ga = 0
        for idx, f in enumerate(all_files):
            ok, cy, ga, err = run_qvm(f, timeout=30)
            if ok:
                ep_pass += 1; ep_cy += cy; ep_ga += ga
            else:
                ep_fail += 1; failures.append(f"  ❌ Epoch{epoch} {f} — {err}")
        print(f"    Epoch {epoch} 完成: PASS={ep_pass} FAIL={ep_fail} 周期={ep_cy} 门={ep_ga}")
        total_pass += ep_pass; total_fail += ep_fail
        total_cycles += ep_cy; total_gates += ep_ga

    print("\n" + "-" * 50)
    print("阶段7 全栈训练汇总:")
    print(f"  电路数={n}  Epochs=3  总运行={n*3}")
    print(f"  PASS={total_pass}  FAIL={total_fail}")
    print(f"  总周期={total_cycles}  总门数={total_gates}")
    if failures:
        print("  失败列表:")
        for x in failures[:30]:
            print(x)
        if len(failures) > 30:
            print(f"  ... 还有 {len(failures)-30} 条")
    return n, total_pass, total_fail, total_cycles, total_gates

if __name__ == "__main__":
    s6_pass, s6_fail, s6_cy, s6_ga = stage6()
    n, s7_pass, s7_fail, s7_cy, s7_ga = stage7()

    print("\n" + "=" * 70)
    print("最终报告")
    print("=" * 70)
    print(f"阶段6 关键电路验证: PASS={s6_pass} FAIL={s6_fail} 周期={s6_cy} 门={s6_ga}")
    print(f"阶段7 全栈训练:     电路={n} PASS={s7_pass} FAIL={s7_fail} 周期={s7_cy} 门={s7_ga}")

    # 输出 JSON 摘要
    summary = {
        "stage6": {"PASS": s6_pass, "FAIL": s6_fail, "cycles": s6_cy, "gates": s6_ga},
        "stage7": {"circuits": n, "epochs": 3, "PASS": s7_pass, "FAIL": s7_fail,
                   "cycles": s7_cy, "gates": s7_ga},
    }
    outpath = os.path.join(ROOT, "stage6_7_summary.json")
    with open(outpath, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=2)
    print(f"\nJSON 摘要已写入: {outpath}")
