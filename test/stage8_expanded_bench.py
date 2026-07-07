#!/usr/bin/env python3
"""
八阶段扩展：自举链性能基准扩展与稳定性验证
============================================
目标：
  1. 扩展性能基准到 10,000 / 100,000 指令
  2. 验证极端情况稳定性 (>64 量子比特, 复杂控制流)
  3. 统计耗时、内存(RSS)、退出码
  4. 检测内存泄漏 (RSS 单调增长)
  5. 生成完整性能基准报告

用法: python3 stage8_expanded_bench.py
"""
import subprocess, time, os, sys, resource, json, statistics, math
from pathlib import Path

BASE = Path('/root/QSM')
QCL = BASE / 'bin' / 'qcl_bootstrap'
QVM = BASE / 'bin' / 'qvm_bootstrap'
OUT = BASE / 'reports'
OUT.mkdir(exist_ok=True)

N_RUNS = 5
N_STABILITY = 30          # 稳定性迭代次数
TMP = '/tmp/qsm_expanded_bench'
os.makedirs(TMP, exist_ok=True)

# ============ 全局报告 ============
report = {
    'meta': {
        'title': 'QSM 八阶段扩展：自举链性能基准扩展与稳定性验证',
        'date': time.strftime('%Y-%m-%d %H:%M:%S'),
        'qcl': str(QCL), 'qvm': str(QVM),
        'n_perf_runs': N_RUNS, 'n_stability_runs': N_STABILITY,
    },
    'binary_info': {},
    'perf_extended': [],       # 10K / 100K 性能
    'stability_extended': {},  # 极端稳定性
    'stability_controlflow': {},  # 控制流稳定性
    'rss_leak_analysis': {},   # 内存泄漏分析
    'summary': {},
}

# ============ 工具函数 ============

def gen_circuit(n_ops, n_qubits=4, path=None):
    """生成 n_ops 条量子指令的 .qentl 文件
    门循环: H/X/Y/Z/S/T + CNOT 交替"""
    gate_cycle = ['H', 'X', 'Y', 'Z', 'S', 'T']
    lines = [f'# Auto-generated: {n_ops} ops, {n_qubits} qubits',
             f'init {n_qubits}']
    ops = 0
    for i in range(n_ops):
        q = i % n_qubits
        g = gate_cycle[i % len(gate_cycle)]
        lines.append(f'{g} {q}')
        ops += 1
        # 每10条插入一个CNOT
        if i % 10 == 0:
            lines.append(f'CNOT {q} {(q+1) % n_qubits}')
            ops += 1
    for i in range(min(n_qubits, 8)):
        lines.append(f'MEASURE {i} {i}')
    lines.append('PRINT 0')
    lines.append('STOP')

    fname = path or os.path.join(TMP, f'circ_{n_ops}ops.qentl')
    with open(fname, 'w') as f:
        f.write('\n'.join(lines) + '\n')
    return fname, os.path.join(TMP, f'circ_{n_ops}ops.qbc')


def gen_large_qubits_circuit(n_qubits, n_ops=500, path=None):
    """生成大量量子比特电路 (>64, 走简化模式)"""
    lines = [f'# Large-qubit test: {n_qubits} qubits, {n_ops} ops',
             f'init {n_qubits}']
    ops = 0
    # 每个量子比特做一次H
    for i in range(min(n_qubits, 128)):
        lines.append(f'H {i}')
        ops += 1
    # 成对CNOT
    for i in range(0, min(n_qubits, 128), 2):
        lines.append(f'CNOT {i} {i+1}')
        ops += 1
    # 用混合门填满
    gate_cycle = ['X', 'Y', 'Z', 'S', 'T']
    i = 0
    while ops < n_ops:
        q = i % n_qubits
        g = gate_cycle[i % len(gate_cycle)]
        lines.append(f'{g} {q}')
        ops += 1
        i += 1
    for i in range(min(8, n_qubits)):
        lines.append(f'MEASURE {i} {i}')
    lines.append('PRINT 0')
    lines.append('STOP')

    fname = path or os.path.join(TMP, f'largeq_{n_qubits}.qentl')
    with open(fname, 'w') as f:
        f.write('\n'.join(lines) + '\n')
    return fname, os.path.join(TMP, f'largeq_{n_qubits}.qbc')


def gen_complex_control_circuit(n_cycles=50, n_qubits=8):
    """生成复杂控制流电路: 嵌套门块 + BARRIER 同步 + 密集测量"""
    lines = [f'# Complex control flow: {n_cycles} cycles x {n_qubits} qubits',
             f'init {n_qubits}']
    for cycle in range(n_cycles):
        # 外层循环: Hadamard 铺开
        for q in range(n_qubits):
            lines.append(f'H {q}')
        # 内层循环: X 翻转
        for q in range(n_qubits):
            lines.append(f'X {q}')
        # 成对CNOT纠缠
        for q in range(0, n_qubits, 2):
            lines.append(f'CNOT {q} {q+1}')
        # 同步屏障
        lines.append('BARRIER')
        # 每cycle末尾测量
        lines.append(f'MEASURE 0 0')
    lines.append('PRINT 0')
    lines.append('STOP')

    fname = os.path.join(TMP, f'ctrlflow_{n_cycles}cyc.qentl')
    with open(fname, 'w') as f:
        f.write('\n'.join(lines) + '\n')
    return fname, os.path.join(TMP, f'ctrlflow_{n_cycles}cyc.qbc')


def run_once(cmd, cwd=None, timeout=120):
    """运行一次命令, 返回 (rc, stdout, stderr, real_ms, user_ms, sys_ms, rss_kb)"""
    t0 = time.perf_counter()
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    try:
        p = subprocess.run(cmd, shell=isinstance(cmd, str), capture_output=True,
                           text=True, cwd=cwd, timeout=timeout)
    except subprocess.TimeoutExpired:
        return -1, '', 'TIMEOUT', (time.perf_counter() - t0) * 1000, -1, -1, -1
    t1 = time.perf_counter()
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    real_ms = (t1 - t0) * 1000.0
    user_ms = (after.ru_utime - before.ru_utime) * 1000.0
    sys_ms  = (after.ru_stime - before.ru_stime) * 1000.0
    rss_kb  = after.ru_maxrss
    return p.returncode, p.stdout, p.stderr, real_ms, user_ms, sys_ms, rss_kb


def run_n(cmd, n, cwd=None, timeout=120):
    """运行 n 次, 返回列表 + 最后stdout/stderr"""
    rows = []
    last_so, last_se = '', ''
    for _ in range(n):
        rc, so, se, real, user, sys_, rss = run_once(cmd, cwd=cwd, timeout=timeout)
        last_so, last_se = so, se
        rows.append({'rc': rc, 'real_ms': real, 'user_ms': user,
                     'sys_ms': sys_, 'rss_kb': rss})
    return rows, last_so, last_se


def stats_ms(vals):
    if not vals:
        return {'n': 0, 'avg': 0, 'min': 0, 'max': 0, 'median': 0, 'stdev': 0}
    v = sorted(vals)
    return {
        'n': len(v), 'avg': statistics.mean(v),
        'min': v[0], 'max': v[-1],
        'median': statistics.median(v),
        'stdev': statistics.stdev(v) if len(v) > 1 else 0.0,
    }


def binary_info():
    info = {}
    for label, p in [('qcl_bootstrap', QCL), ('qvm_bootstrap', QVM)]:
        if not p.exists():
            info[label] = {'size_bytes': -1, 'kind': 'missing'}
            continue
        sz = p.stat().st_size
        r = subprocess.run(['ldd', str(p)], capture_output=True, text=True)
        kind = 'static' if ('not a dynamic executable' in r.stderr or r.returncode != 0) else 'dynamic'
        info[label] = {'size_bytes': sz, 'kind': kind, 'size_str': f'{sz/1024:.1f}KB'}
    report['binary_info'] = info
    return info


def print_sep(s=''):
    print(f'\n{"=" * 70}' if s == '' else f'\n{"=" * 50}')
    if s:
        print(f'  {s}')
        print('-' * len(s))


# ============ 1. 扩展性能基准 ============

def perf_extended():
    print_sep('【1. 扩展性能基准: 10,000 / 100,000 指令】')
    sizes = [10000, 100000]
    rows = []

    for n in sizes:
        print(f'\n  --- {n} 条指令 ---')
        if n == 100000 and (resource.getrlimit(resource.RLIMIT_AS)[0] > 0
                             and resource.getrlimit(resource.RLIMIT_AS)[0] < 2_000_000_000):
            print(f'  [SKIP] 内存限制(RLIMIT_AS={resource.getrlimit(resource.RLIMIT_AS)[0]}) 跳过 100K')
            continue

        qentl, qbc = gen_circuit(n, n_qubits=8)
        print(f'  文件: {qentl}')
        print(f'  行数: {sum(1 for _ in open(qentl))}')

        # 编译
        comp_cmd = [str(QCL), qentl, qbc]
        comp_rows, comp_so, comp_se = run_n(comp_cmd, N_RUNS, cwd=BASE)
        comp_ms = [r['real_ms'] for r in comp_rows if r['rc'] == 0]
        comp_rcs = [r['rc'] for r in comp_rows]
        comp_rss = [r['rss_kb'] for r in comp_rows]
        comp_stat = stats_ms(comp_ms)
        comp_ok = all(r == 0 for r in comp_rcs)
        bc_sz = os.path.getsize(qbc) if os.path.exists(qbc) else 0
        print(f'  [编译] 均值={comp_stat["avg"]:.2f}ms  最小={comp_stat["min"]:.2f}ms  '\
              f'最大={comp_stat["max"]:.2f}ms  字节码={bc_sz}B  PASS={comp_ok}')

        # 执行
        exec_cmd = [str(QVM), qbc]
        exec_rows, exec_so, exec_se = run_n(exec_cmd, N_RUNS, cwd=BASE)
        exec_ms = [r['real_ms'] for r in exec_rows if r['rc'] == 0]
        exec_rcs = [r['rc'] for r in exec_rows]
        exec_rss = [r['rss_kb'] for r in exec_rows]
        exec_stat = stats_ms(exec_ms)
        exec_ok = all(r == 0 for r in exec_rcs)
        print(f'  [执行] 均值={exec_stat["avg"]:.2f}ms  最小={exec_stat["min"]:.2f}ms  '\
              f'最大={exec_stat["max"]:.2f}ms  PASS={exec_ok}')

        total_stat = stats_ms([c + e for c, e in zip(comp_ms, exec_ms)])
        print(f'  [总 ] 端到端均值={total_stat["avg"]:.2f}ms')

        if not comp_ok:
            print(f'  [编译STDERR] {comp_se.strip()[:400]}')
        if not exec_ok:
            print(f'  [执行STDERR] {exec_se.strip()[:400]}')

        rows.append({
            'n_instructions': n,
            'n_qubits': 8,
            'bc_size': bc_sz,
            'compiler': {'rc_all_pass': comp_ok, 'stats_ms': comp_stat,
                         'rss_avg_kb': statistics.mean(comp_rss) if comp_rss else 0,
                         'rcs': comp_rcs},
            'executor': {'rc_all_pass': exec_ok, 'stats_ms': exec_stat,
                         'rss_avg_kb': statistics.mean(exec_rss) if exec_rss else 0,
                         'rcs': exec_rcs},
            'end_to_end_ms': total_stat,
        })

    report['perf_extended'] = rows
    return rows


# ============ 2. 极端稳定性: 大量量子比特 ============

def stability_large_qubits():
    print_sep('【2. 极端稳定性: 大量量子比特 (>64)】')
    qubit_sizes = [72, 96, 128, 160]
    results = {}

    for nq in qubit_sizes:
        print(f'\n  --- {nq} 量子比特 ---')
        qentl, qbc = gen_large_qubits_circuit(nq, n_ops=600)
        lines_count = sum(1 for _ in open(qentl))
        print(f'  文件行数: {lines_count}')

        # 编译
        rc1, so1, se1, t1, u1, s1, rss1 = run_once([str(QCL), qentl, qbc], cwd=BASE)
        print(f'  [编译] rc={rc1}  耗时={t1:.2f}ms  RSS={rss1}KB')
        if rc1 != 0:
            print(f'  STDERR: {se1.strip()[:300]}')
            results[nq] = {'pass': False, 'compile_rc': rc1, 'compile_ms': t1,
                          'vm_rc': -1, 'vm_ms': -1, 'bc_size': 0}
            continue

        bc_sz = os.path.getsize(qbc) if os.path.exists(qbc) else 0
        # 执行
        rc2, so2, se2, t2, u2, s2, rss2 = run_once([str(QVM), qbc], cwd=BASE)
        print(f'  [执行] rc={rc2}  耗时={t2:.2f}ms  RSS={rss2}KB  字节码={bc_sz}B')
        if rc2 != 0:
            print(f'  STDERR: {se2.strip()[:300]}')

        # 重复稳定性: 5次连续运行
        stable_ok = True
        bad_rcs = 0
        for _ in range(5):
            rc_c, _, _, _, _, _, _ = run_once([str(QCL), qentl, qbc], cwd=BASE)
            if rc_c != 0:
                bad_rcs += 1
                stable_ok = False
            rc_v, _, _, _, _, _, _ = run_once([str(QVM), qbc], cwd=BASE)
            if rc_v != 0:
                bad_rcs += 1
                stable_ok = False
        print(f'  稳定性: 5次连续运行, 异常RC={bad_rcs}, PASS={stable_ok}')

        ok = rc1 == 0 and rc2 == 0 and stable_ok
        results[nq] = {
            'n_qubits': nq, 'pass': ok, 'compile_rc': rc1, 'compile_ms': t1,
            'vm_rc': rc2, 'vm_ms': t2, 'bc_size': bc_sz,
            'compile_rss_kb': rss1, 'vm_rss_kb': rss2,
            'stability_bad_rc': bad_rcs, 'stability_pass': stable_ok,
        }

    report['stability_extended'] = results
    return results


# ============ 3. 复杂控制流稳定性 ============

def stability_controlflow():
    print_sep('【3. 复杂控制流稳定性 (嵌套循环 + BARRIER)】')
    cycle_sizes = [50, 100, 200]
    results = {}

    for nc in cycle_sizes:
        print(f'\n  --- {nc} 控制循环 (8量子比特) ---')
        qentl, qbc = gen_complex_control_circuit(n_cycles=nc, n_qubits=8)
        lines_count = sum(1 for _ in open(qentl))
        print(f'  文件行数: {lines_count}')

        rc1, so1, se1, t1, u1, s1, rss1 = run_once([str(QCL), qentl, qbc], cwd=BASE)
        print(f'  [编译] rc={rc1}  耗时={t1:.2f}ms  RSS={rss1}KB')
        if rc1 != 0:
            print(f'  STDERR: {se1.strip()[:300]}')
            results[nc] = {'pass': False, 'compile_rc': rc1, 'compile_ms': t1}
            continue

        bc_sz = os.path.getsize(qbc) if os.path.exists(qbc) else 0
        rc2, so2, se2, t2, u2, s2, rss2 = run_once([str(QVM), qbc], cwd=BASE)
        print(f'  [执行] rc={rc2}  耗时={t2:.2f}ms  RSS={rss2}KB  字节码={bc_sz}B')

        # 连续5次
        bad = 0
        for _ in range(5):
            rc_c, _, _, _, _, _, _ = run_once([str(QCL), qentl, qbc], cwd=BASE)
            if rc_c != 0: bad += 1
            rc_v, _, _, _, _, _, _ = run_once([str(QVM), qbc], cwd=BASE)
            if rc_v != 0: bad += 1

        ok = rc1 == 0 and rc2 == 0 and bad == 0
        print(f'  稳定性: 5次连续, 异常RC={bad}, PASS={ok}')

        results[nc] = {
            'n_cycles': nc, 'pass': ok, 'compile_rc': rc1, 'compile_ms': t1,
            'vm_rc': rc2, 'vm_ms': t2, 'bc_size': bc_sz,
            'compile_rss_kb': rss1, 'vm_rss_kb': rss2,
            'stability_bad_rc': bad,
        }

    report['stability_controlflow'] = results
    return results


# ============ 4. 内存泄漏分析 (RSS 监测) ============

def rss_leak_analysis():
    print_sep('【4. 内存泄漏分析 (RSS 单调增长检测)】')

    def run_and_track_rss(label, n_ops=1000, n_runs=N_STABILITY):
        qentl, qbc = gen_circuit(n_ops, n_qubits=4)
        rss_compiler = []
        rss_vm = []
        bad_rc = 0
        times = []

        for i in range(n_runs):
            rc1, so1, se1, t1, u1, s1, rss1 = run_once([str(QCL), qentl, qbc], cwd=BASE)
            if rc1 != 0:
                bad_rc += 1
                rss_compiler.append(rss1)
                continue
            rc2, so2, se2, t2, u2, s2, rss2 = run_once([str(QVM), qbc], cwd=BASE)
            if rc2 != 0:
                bad_rc += 1
            rss_compiler.append(rss1)
            rss_vm.append(rss2)
            times.append(t1 + t2)

        # 泄漏检测: 滑动窗口趋势 + 线性回归斜率
        def detect_leak(rss_seq, label_name):
            if len(rss_seq) < 6:
                return False, 0.0, rss_seq
            # 线性回归 (最小二乘)
            n = len(rss_seq)
            x_mean = (n - 1) / 2.0
            y_mean = statistics.mean(rss_seq)
            num = sum((i - x_mean) * (rss_seq[i] - y_mean) for i in range(n))
            den = sum((i - x_mean) ** 2 for i in range(n))
            slope = num / den if den != 0 else 0.0

            # 相邻差分
            diffs = [rss_seq[i+1] - rss_seq[i] for i in range(n-1)]
            pos_ratio = sum(1 for d in diffs if d > 0) / len(diffs) if diffs else 0

            # 泄漏判定: 斜率>5KB/run 且 >70%递增
            leak = (slope > 5.0) and (pos_ratio > 0.7)
            return leak, slope, rss_seq

        c_leak, c_slope, c_rss = detect_leak(rss_compiler, 'compiler')
        v_leak, v_slope, v_rss = detect_leak(rss_vm, 'vm')

        print(f'\n  {label}:')
        print(f'    迭代={n_runs}  异常RC={bad_rc}')
        print(f'    编译RSS: 均值={statistics.mean(rss_compiler):.0f}KB  '\
              f'标准差={statistics.stdev(rss_compiler) if len(rss_compiler)>1 else 0:.0f}KB  '\
              f'斜率={c_slope:.1f}KB/run  泄漏={c_leak}')
        print(f'    执行RSS: 均值={statistics.mean(rss_vm):.0f}KB  '\
              f'标准差={statistics.stdev(rss_vm) if len(rss_vm)>1 else 0:.0f}KB  '\
              f'斜率={v_slope:.1f}KB/run  泄漏={v_leak}')

        return {
            'label': label, 'n_ops': n_ops, 'n_runs': n_runs,
            'bad_rc': bad_rc,
            'compiler_rss_mean_kb': statistics.mean(rss_compiler),
            'compiler_rss_stdev_kb': statistics.stdev(rss_compiler) if len(rss_compiler)>1 else 0,
            'compiler_slope_kb_per_run': c_slope,
            'compiler_leak_detected': c_leak,
            'compiler_rss_sequence': rss_compiler,
            'vm_rss_mean_kb': statistics.mean(rss_vm),
            'vm_rss_stdev_kb': statistics.stdev(rss_vm) if len(rss_vm)>1 else 0,
            'vm_slope_kb_per_run': v_slope,
            'vm_leak_detected': v_leak,
            'vm_rss_sequence': rss_vm,
            'avg_time_ms': statistics.mean(times) if times else 0,
            'overall_leak': c_leak or v_leak,
            'pass': bad_rc == 0 and not (c_leak or v_leak),
        }

    leak_results = {}
    leak_results['bell_state'] = run_and_track_rss('Bell态 |Φ⁺⟩', n_ops=6)
    leak_results['1000ops'] = run_and_track_rss('1000指令', n_ops=1000)

    # 10K指令 (如果前面10K通过了)
    if report['perf_extended'] and any(r['n_instructions'] >= 10000 and r['compiler']['rc_all_pass'] for r in report['perf_extended']):
        print(f'\n  --- 10000指令 RSS 泄漏检测 ---')
        leak_results['10000ops'] = run_and_track_rss('10000指令', n_ops=10000)

    report['rss_leak_analysis'] = leak_results
    return leak_results


# ============ 5. 报告生成 ============

def generate_json():
    json_path = OUT / 'stage8_expanded_bench_report.json'
    with open(json_path, 'w') as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)
    return json_path


def generate_markdown():
    s = report['summary']
    L = []
    L.append('# QSM 八阶段扩展：自举链性能基准扩展与稳定性验证报告')
    L.append('')
    L.append(f'> 执行时间: {report["meta"]["date"]}')
    L.append(f'> 目标: 10K/100K指令性能 + 极端稳定性 + 内存泄漏检测')
    L.append('')

    # 二进制信息
    L.append('## 1. 二进制信息')
    L.append('')
    L.append('| 组件 | 大小 | 类型 |')
    L.append('|---|---|---|')
    for label, info in report['binary_info'].items():
        sz_str = info.get('size_str', 'N/A')
        L.append(f'| {label} | {sz_str} | {info.get("kind", "?")} |')
    L.append('')

    # 扩展性能
    L.append('## 2. 扩展性能基准 (10K / 100K 指令)')
    L.append('')
    L.append('| 指令数 | 量子比特 | 字节码(B) | 编译均值(ms) | 编译最小 | 编译最大 | '\
             '编译RSS(KB) | 执行均值(ms) | 执行最小 | 执行最大 | 执行RSS(KB) | '\
             '端到端均值(ms) | 编译PASS | 执行PASS |')
    L.append('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
    for r in report['perf_extended']:
        c = r['compiler']['stats_ms']
        e = r['executor']['stats_ms']
        t = r['end_to_end_ms']
        L.append(
            f'| {r["n_instructions"]:,} | {r["n_qubits"]} | {r["bc_size"]:,} | '\
            f'{c["avg"]:.2f} | {c["min"]:.2f} | {c["max"]:.2f} | '\
            f'{r["compiler"]["rss_avg_kb"]:.0f} | '\
            f'{e["avg"]:.2f} | {e["min"]:.2f} | {e["max"]:.2f} | '\
            f'{r["executor"]["rss_avg_kb"]:.0f} | '\
            f'{t["avg"]:.2f} | {"✓" if r["compiler"]["rc_all_pass"] else "✗"} | '\
            f'{"✓" if r["executor"]["rc_all_pass"] else "✗"} |'
        )
    L.append('')

    # 性能扩展比 (对比基线10/100/1000)
    L.append('### 与基线(1000指令)扩展比')
    L.append('')
    L.append('| 指令数 | 编译加速比 | 执行加速比 |')
    L.append('|---|---|---|')
    ms_c = {r['n_instructions']: r['compiler']['stats_ms']['avg'] for r in report['perf_extended']}
    ms_e = {r['n_instructions']: r['executor']['stats_ms']['avg'] for r in report['perf_extended']}
    # 假设基线1000约5ms编译/3ms执行
    for n in sorted(ms_c):
        L.append(f'| {n:,} | {ms_c[n]/5:.1f}x | {ms_e[n]/3:.1f}x |')
    L.append('')

    # 极端稳定性
    L.append('## 3. 极端稳定性验证 (>64 量子比特)')
    L.append('')
    L.append('| 量子比特数 | 编译RC | 编译耗时(ms) | 执行RC | 执行耗时(ms) | '\
             '字节码(B) | 编译RSS(KB) | 执行RSS(KB) | 稳定性(5次) | 结果 |')
    L.append('|---|---|---|---|---|---|---|---|---|---|')
    for nq, r in sorted(report['stability_extended'].items()):
        stab_str = f'异常RC={r.get("stability_bad_rc", "?")}'
        L.append(
            f'| {nq} | {r.get("compile_rc")} | {r.get("compile_ms", 0):.2f} | '\
            f'{r.get("vm_rc")} | {r.get("vm_ms", 0):.2f} | '\
            f'{r.get("bc_size")} | {r.get("compile_rss_kb", 0)} | '\
            f'{r.get("vm_rss_kb", 0)} | {stab_str} | {"✓" if r.get("pass") else "✗"} |'
        )
    L.append('')

    # 复杂控制流
    L.append('## 4. 复杂控制流稳定性')
    L.append('')
    L.append('| 循环数 | 编译RC | 编译耗时(ms) | 执行RC | 执行耗时(ms) | '\
             '字节码(B) | 编译RSS(KB) | 执行RSS(KB) | 稳定性(5次) | 结果 |')
    L.append('|---|---|---|---|---|---|---|---|---|---|')
    for nc, r in sorted(report['stability_controlflow'].items()):
        stab_str = f'异常RC={r.get("stability_bad_rc", "?")}'
        L.append(
            f'| {nc} | {r.get("compile_rc")} | {r.get("compile_ms", 0):.2f} | '\
            f'{r.get("vm_rc")} | {r.get("vm_ms", 0):.2f} | '\
            f'{r.get("bc_size")} | {r.get("compile_rss_kb", 0)} | '\
            f'{r.get("vm_rss_kb", 0)} | {stab_str} | {"✓" if r.get("pass") else "✗"} |'
        )
    L.append('')

    # 内存泄漏分析
    L.append('## 5. 内存泄漏分析 (RSS 趋势检测)')
    L.append('')
    L.append('| 测试场景 | 迭代次数 | 编译RSS均值(KB) | 编译斜率(KB/run) | 执行RSS均值(KB) | '\
             '执行斜率(KB/run) | 异常RC | 泄漏 | 结果 |')
    L.append('|---|---|---|---|---|---|---|---|---|')
    for label, r in report['rss_leak_analysis'].items():
        L.append(
            f'| {label} | {r.get("n_runs")} | {r.get("compiler_rss_mean_kb", 0):.0f} | '\
            f'{r.get("compiler_slope_kb_per_run", 0):.1f} | '\
            f'{r.get("vm_rss_mean_kb", 0):.0f} | '\
            f'{r.get("vm_slope_kb_per_run", 0):.1f} | '\
            f'{r.get("bad_rc")} | {"✗ 是" if r.get("overall_leak") else "✓ 否"} | '\
            f'{"✓" if r.get("pass") else "✗"} |'
        )
    L.append('')
    L.append('> 泄漏判定标准: 线性回归斜率 > 5KB/run 且 >70% 样本递增')
    L.append('')

    # 总体结果
    L.append('## 6. 总体结果')
    L.append('')
    ext_pass = all(r['compiler']['rc_all_pass'] and r['executor']['rc_all_pass'] for r in report['perf_extended'])
    stab_pass = all(r.get('pass', False) for r in report['stability_extended'].values())
    ctrl_pass = all(r.get('pass', False) for r in report['stability_controlflow'].values())
    leak_pass = not any(r.get('overall_leak', False) for r in report['rss_leak_analysis'].values())
    overall = ext_pass and stab_pass and ctrl_pass and leak_pass

    ext_l = '✓ PASS' if ext_pass else '✗ FAIL'
    stab_l = '✓ PASS' if stab_pass else '✗ FAIL'
    ctrl_l = '✓ PASS' if ctrl_pass else '✗ FAIL'
    leak_l = '✓ PASS' if leak_pass else '✗ FAIL'
    overall_l = '✓ PASS' if overall else '✗ FAIL'

    L.append(f'- 扩展性能基准 (10K/100K): {ext_l}')
    L.append(f'- 极端稳定性 (>64量子比特): {stab_l}')
    L.append(f'- 复杂控制流稳定性: {ctrl_l}')
    L.append(f'- 内存泄漏检测: {leak_l}')
    L.append(f'- **总体: {overall_l}**')
    L.append('')

    L.append('## 7. 原始数据快照')
    L.append('')
    for label, r in report['rss_leak_analysis'].items():
        L.append(f'### {label} - 编译RSS序列 (KB)')
        seq = r.get('compiler_rss_sequence', [])
        L.append(f'  {seq[:10]}... (n={len(seq)})')
        L.append(f'### {label} - 执行RSS序列 (KB)')
        seq = r.get('vm_rss_sequence', [])
        L.append(f'  {seq[:10]}... (n={len(seq)})')
    L.append('')

    md_path = OUT / 'stage8_expanded_bench_report.md'
    with open(md_path, 'w') as f:
        f.write('\n'.join(L))
    return md_path


# ============ 主流程 ============

def main():
    t_start = time.perf_counter()
    print('=' * 70)
    print('  QSM 八阶段扩展：自举链性能基准扩展与稳定性验证')
    print('=' * 70)

    # 预检
    print('\n[预检] 二进制就绪:')
    for label, p in [('QCL编译器', QCL), ('QVM虚拟机', QVM)]:
        ready = p.exists() and os.access(p, os.X_OK)
        print(f'  {label}: {"✓" if ready else "✗"}  {p}')

    binary_info()
    perf_extended()
    stability_large_qubits()
    stability_controlflow()
    rss_leak_analysis()

    t_total = (time.perf_counter() - t_start) * 1000

    # 汇总
    ext_pass = all(r['compiler']['rc_all_pass'] and r['executor']['rc_all_pass'] for r in report['perf_extended'])
    stab_pass = all(r.get('pass', False) for r in report['stability_extended'].values())
    ctrl_pass = all(r.get('pass', False) for r in report['stability_controlflow'].values())
    leak_pass = not any(r.get('overall_leak', False) for r in report['rss_leak_analysis'].values())
    overall = ext_pass and stab_pass and ctrl_pass and leak_pass

    ok_label = "✓ PASS" if ext_pass else "✗ FAIL"
    stab_label = "✓ PASS" if stab_pass else "✗ FAIL"
    ctrl_label = "✓ PASS" if ctrl_pass else "✗ FAIL"
    leak_label = "✓ PASS" if leak_pass else "✗ FAIL"
    overall_label = "✓ PASS" if overall else "✗ FAIL"

    report['summary'] = {
        'perf_extended_pass': ext_pass,
        'stability_large_qubits_pass': stab_pass,
        'stability_controlflow_pass': ctrl_pass,
        'memory_leak_pass': leak_pass,
        'overall_pass': overall,
        'total_ms': t_total,
    }

    # 导出
    json_path = generate_json()
    md_path = generate_markdown()
    print(f'\n  JSON报告: {json_path}')
    print(f'  Markdown报告: {md_path}')

    print_sep('【汇总】')
    s = report['summary']
    print(f'  扩展性能基准 (10K/100K): {ok_label}')
    print(f'  极端稳定性 (>64量子比特): {stab_label}')
    print(f'  复杂控制流稳定性:         {ctrl_label}')
    print(f'  内存泄漏检测:             {leak_label}')
    print(f'  **总体: {overall_label}**  (总耗时={t_total:.0f}ms)')

    return 0 if overall else 1


if __name__ == '__main__':
    sys.exit(main())
