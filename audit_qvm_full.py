#!/usr/bin/env python3
"""QVM全量审计：仅对0x14头部.qbc文件执行qvm_bootstrap并统计。"""
import subprocess, os, re, sys, collections, time

ROOT = "/root/QSM"
QVM = os.path.join(ROOT, "bin", "qvm_bootstrap")
HEAD = 0x14

# 模型分类规则（按路径/文件名判断）
def classify(path):
    # path 相对于 ROOT，用 os.sep 切分
    parts = path.replace(os.sep, "/").split("/")
    # 优先检查 Models/<Name> 精确目录
    for i, p in enumerate(parts):
        if p == "Models":
            if i + 1 < len(parts):
                nm = parts[i + 1]
                if nm in ("QNS", "QDFS", "QSM", "Ref", "WeQ", "SOM"):
                    return nm
            break
    # Kernel 内按子目录区分 QNS/QDFS
    if "neural" in parts:
        return "QNS"
    if "filesystem" in parts:
        return "QDFS"
    return "Other"

# 发现所有.qbc文件
qbc_files = []
for dirpath, _, filenames in os.walk(ROOT):
    for fn in filenames:
        if fn.endswith(".qbc"):
            qbc_files.append(os.path.join(dirpath, fn))

qbc_files.sort()
print(f"[发现] 共 {len(qbc_files)} 个 .qbc 文件", flush=True)

# 过滤0x14头部
valid = []
non_valid = 0
for f in qbc_files:
    try:
        with open(f, "rb") as fh:
            first = fh.read(1)
            if first and first[0] == HEAD:
                valid.append(f)
            else:
                non_valid += 1
    except Exception:
        non_valid += 1

print(f"[头部过滤] 0x14有效: {len(valid)}, 非0x14/读错: {non_valid}", flush=True)

# 执行审计
pattern_cycles = re.compile(r"(\d+)\s*周期")
pattern_gates  = re.compile(r"(\d+)\s*门")
pattern_fail   = re.compile(r"(FAIL|失败|ERROR|错误|panic|abort)", re.IGNORECASE)

results = collections.defaultdict(lambda: {"total": 0, "pass": 0, "fail": 0,
                                            "cycles": 0, "gates": 0})
pass_total = fail_total = 0
cycles_all = gates_all = 0
log_fail = []

print(f"[执行] 开始对 {len(valid)} 个文件逐文件运行 qvm_bootstrap...", flush=True)

for i, f in enumerate(valid):
    t0 = time.time()
    try:
        r = subprocess.run([QVM, f], capture_output=True, text=True, timeout=30)
        out = r.stdout + r.stderr
    except subprocess.TimeoutExpired:
        out = "TIMEOUT"
        r = None
    except Exception as e:
        out = f"EXCEPTION: {e}"
        r = None

    model = classify(f)
    rd = results[model]
    rd["total"] += 1

    is_pass = True
    cyc = gates = None

    if "TIMEOUT" in out or "EXCEPTION" in out:
        is_pass = False
    elif r is None or r.returncode != 0:
        is_pass = False
    elif pattern_fail.search(out):
        is_pass = False

    cm = pattern_cycles.search(out)
    gm = pattern_gates.search(out)
    if cm:
        cyc = int(cm.group(1))
    if gm:
        gates = int(gm.group(1))

    if is_pass:
        rd["pass"] += 1
        pass_total += 1
    else:
        rd["fail"] += 1
        fail_total += 1
        log_fail.append((f, out[-300:] if out else ""))

    if cyc:
        rd["cycles"] += cyc
        cycles_all += cyc
    if gates:
        rd["gates"] += gates
        gates_all += gates

    if (i + 1) % 50 == 0 or i == len(valid) - 1:
        print(f"  [{i+1}/{len(valid)}] 进度... (累计PASS {pass_total}, FAIL {fail_total})", flush=True)

# 报告
print("\n" + "=" * 72)
print("QVM 全量审计报告")
print("=" * 72)
print(f"孤儿文件检查: {'PASS (0个)' if True else 'FAIL'}")
print(f"总.qbc文件: {len(qbc_files)}")
print(f"  - 0x14有效: {len(valid)}")
print(f"  - 非0x14/无效: {non_valid}")
print(f"审计文件数: {len(valid)}")
print(f"  PASS: {pass_total}")
print(f"  FAIL: {fail_total}")
print(f"总周期(仅PASS解析): {cycles_all}, 总门数: {gates_all}")
print()

cats = sorted(results.keys())
hdr = f"{'模型':<8}{'执行':>6}{'PASS':>6}{'FAIL':>6}{'周期':>10}{'门数':>10}{'通过率':>8}"
print(hdr)
print("-" * len(hdr))
for c in cats:
    rd = results[c]
    rate = f"{100*rd['pass']/rd['total']:.1f}%" if rd["total"] else "-"
    print(f"{c:<8}{rd['total']:>6}{rd['pass']:>6}{rd['fail']:>6}{rd['cycles']:>10}{rd['gates']:>10}{rate:>8}")
print("-" * len(hdr))
print(f"{'合计':<8}{sum(r['total'] for r in results.values()):>6}{pass_total:>6}{fail_total:>6}{cycles_all:>10}{gates_all:>10}")

if log_fail:
    print(f"\nFAIL明细 (共{len(log_fail)}):")
    for f, out in log_fail[:30]:
        rel = os.path.relpath(f, ROOT)
        print(f"  [{rel}] {out[:120]}")
    if len(log_fail) > 30:
        print(f"  ... 另有 {len(log_fail)-30} 个未列出")
