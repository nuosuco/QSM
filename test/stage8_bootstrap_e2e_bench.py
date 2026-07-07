#!/usr/bin/env python3
"""
QSM 阶段8 — 自举链端到端集成测试与性能基准
===========================================
测试链: C编译器(bin/qcl_bootstrap) → QCL引导器(编译输出.qbc) → QVM虚拟机(bin/qvm_bootstrap) → 量子程序执行

测试内容:
  1. 各环节退出码与输出验证
  2. 10 / 100 / 1000 量子指令数量下的端到端性能
  3. 每环节独立计时(编译/执行)
  4. 稳定性: 多轮迭代无崩溃、无内存泄漏(RSS单调增长检测)
  5. 生成性能基准报告(stage8_bootstrap_e2e_report.json + .md)

用法: python3 stage8_bootstrap_e2e_bench.py
"""
import subprocess, time, os, sys, resource, json, tempfile, shutil, statistics
from pathlib import Path

BASE = Path('/root/QSM')
QCL = BASE / 'bin' / 'qcl_bootstrap'          # C编译器 = QCL引导编译器
QVM = BASE / 'bin' / 'qvm_bootstrap'          # QVM虚拟机
QCL_OPT = BASE / 'bin' / 'qcl_bootstrap_opt'  # 优化版(静态+strip)
QVM_OPT = BASE / 'bin' / 'qvm_bootstrap_opt'

N_RUNS = 5          # 每次性能测试重复次数
N_STABILITY = 20    # 稳定性迭代次数

OUT = BASE / 'reports'
OUT.mkdir(exist_ok=True)

# 全局报告数据
report = {
    'meta': {
        'title': 'QSM 八阶段: 自举链端到端集成测试与性能基准',
        'qcl_compiler': str(QCL),
        'qvm_vm': str(QVM),
        'n_perf_runs': N_RUNS,
        'n_stability_runs': N_STABILITY,
    },
    'binary_info': {},
    'e2e_tests': {},
    'performance': {},
    'stability': {},
    'summary': {},
}


# =====================================================================
# 工具函数
# =====================================================================

def binary_info():
    """统计二进制文件大小、链接类型"""
    info = {}
    for label, p in [('qcl_bootstrap', QCL), ('qvm_bootstrap', QVM),
                     ('qcl_bootstrap_opt', QCL_OPT), ('qvm_bootstrap_opt', QVM_OPT)]:
        sz = p.stat().st_size if p.exists() else -1
        # 判断静态: 无动态依赖
        deps = []
        if sz > 0:
            r = subprocess.run(['ldd', str(p)], capture_output=True, text=True)
            if r.returncode != 0 or 'not a dynamic executable' in r.stderr:
                kind = 'static'
            else:
                kind = 'dynamic'
            deps = kind
        info[label] = {'size_bytes': sz, 'kind': deps}
    report['binary_info'] = info
    return info


def gen_circuit(n_ops, n_qubits=4, tmpdir='/tmp'):
    """生成包含 n_ops 量子指令的 .qentl 文件
    指令模板循环: init 4 → H/CNOT/X/Z/S/T/Y → MEASURE → PRINT → STOP
    返回 (qentl_path, bc_path)"""
    # 构造指令模板(除去 init 和 STOP,中间填满)
    gate_cycle = ['H 0', 'X 1', 'Z 2', 'S 3', 'T 0', 'Y 1', 'CNOT 0 1', 'CNOT 1 2']
    lines = [f'# Auto-generated: {n_ops} quantum instructions, {n_qubits} qubits',
             f'init {n_qubits}']
    ops_written = 0
    idx = 0
    while ops_written < n_ops:
        g = gate_cycle[idx % len(gate_cycle)]
        lines.append(g)
        ops_written += 1
        idx += 1
    # 结尾测量+输出+停止
    for i in range(n_qubits):
        lines.append(f'MEASURE {i} {i}')
    lines.append('PRINT 0')
    lines.append('STOP')

    qentl = os.path.join(tmpdir, f'bench_{n_ops}ops.qentl')
    qbc = os.path.join(tmpdir, f'bench_{n_ops}ops.qbc')
    with open(qentl, 'w') as f:
        f.write('\n'.join(lines) + '\n')
    return qentl, qbc


def run_once(cmd, cwd=None, env_extra=None):
    """运行一次命令，返回 (rc, stdout, stderr, real_ms, user_ms, sys_ms)"""
    t0 = time.perf_counter()
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    p = subprocess.run(cmd, shell=isinstance(cmd, str), capture_output=True,
                       text=True, cwd=cwd, env=env_extra)
    t1 = time.perf_counter()
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    real_ms = (t1 - t0) * 1000.0
    user_ms = (after.ru_utime - before.ru_utime) * 1000.0
    sys_ms  = (after.ru_stime - before.ru_stime) * 1000.0
    rss_kb  = after.ru_maxrss  # Linux: KB
    return p.returncode, p.stdout, p.stderr, real_ms, user_ms, sys_ms, rss_kb


def run_n(cmd, n, cwd=None):
    """运行 n 次, 返回列表 [(rc, real_ms, user_ms, sys_ms, rss_kb), ...]"""
    rows = []
    last_stdout, last_stderr = '', ''
    for _ in range(n):
        rc, so, se, real, user, sys_, rss = run_once(cmd, cwd=cwd)
        last_stdout, last_stderr = so, se
        rows.append({'rc': rc, 'real_ms': real, 'user_ms': user,
                     'sys_ms': sys_, 'rss_kb': rss})
    return rows, last_stdout, last_stderr


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


def print_sep(s=''):
    print(('=' * 70) if s == '' else f'\n{""*50}', end='\n')
    if s:
        print(s)
        print('-' * len(s))


# =====================================================================
# 1. 端到端整合测试 — bell_state 基线
# =====================================================================
def e2e_baseline():
    print_sep('【1. 端到端基线测试: Bell态 |Φ⁺⟩】')
    bell = BASE / 'test' / 'bell_state.qentl'
    if not bell.exists():
        print('  [SKIP] bell_state.qentl not found')
        return
    tmpbc = '/tmp/bench_e2e_bell.qbc'

    # 环节1: C编译器编译
    rc1, so1, se1, t1, u1, s1, rss1 = run_once([str(QCL), str(bell), tmpbc], cwd=BASE)
    print(f'  环节1 [C编译器]: rc={rc1}  耗时={t1:.2f}ms  RSS={rss1}KB')
    if rc1 != 0:
        print(f'    STDERR: {se1.strip()[:300]}')

    # 环节2: QVM虚拟机执行
    bc_exists = os.path.exists(tmpbc)
    rc2, so2, se2, t2, u2, s2, rss2 = run_once([str(QVM), tmpbc], cwd=BASE)
    print(f'  环节2 [QVM]:     rc={rc2}  耗时={t2:.2f}ms  RSS={rss2}KB  字节码={bc_exists}')

    ok = rc1 == 0 and rc2 == 0
    report['e2e_tests']['bell_state'] = {
        'compiler_rc': rc1, 'compiler_ms': t1, 'compiler_rss_kb': rss1,
        'vm_rc': rc2, 'vm_ms': t2, 'vm_rss_kb': rss2,
        'total_ms': t1 + t2, 'bc_size': os.path.getsize(tmpbc) if bc_exists else 0,
        'pass': ok,
        'stdout_compiler': so1.strip()[:500],
        'stdout_vm': so2.strip()[:500],
    }
    print(f'  端到端结果: {"PASS ✓" if ok else "FAIL ✗"}  总耗时={t1+t2:.2f}ms')
    if not ok:
        print(f'  [COMPILER STDOUT] {so1[:400]}')
        print(f'  [VM STDOUT]       {so2[:400]}')


# =====================================================================
# 2. 性能基准: 10/100/1000 指令
# =====================================================================
def perf_bench():
    print_sep('【2. 性能基准: 10 / 100 / 1000 指令数量对比】')
    sizes = [10, 100, 1000]
    rows = []  # 用于表格展示

    for n in sizes:
        qentl, qbc = gen_circuit(n, n_qubits=4)
        print(f'\n  --- 电路: {n} 条指令 ---')

        # 编译性能 (N_RUNS次)
        comp_cmd = [str(QCL), qentl, qbc]
        comp_rows, comp_so, comp_se = run_n(comp_cmd, N_RUNS, cwd=BASE)
        comp_ms = [r['real_ms'] for r in comp_rows]
        comp_rcs = [r['rc'] for r in comp_rows]
        comp_rss = [r['rss_kb'] for r in comp_rows]
        comp_stat = stats_ms(comp_ms)
        comp_ok = all(r == 0 for r in comp_rcs)

        bc_sz = os.path.getsize(qbc) if os.path.exists(qbc) else 0
        print(f'  [编译] {comp_stat["n"]}次 均值={comp_stat["avg"]:.2f}ms  '
              f'最小={comp_stat["min"]:.2f}ms  最大={comp_stat["max"]:.2f}ms  '
              f'RC={comp_rcs}  字节码={bc_sz}B')

        # 执行性能
        exec_cmd = [str(QVM), qbc]
        exec_rows, exec_so, exec_se = run_n(exec_cmd, N_RUNS, cwd=BASE)
        exec_ms = [r['real_ms'] for r in exec_rows]
        exec_rcs = [r['rc'] for r in exec_rows]
        exec_rss = [r['rss_kb'] for r in exec_rows]
        exec_stat = stats_ms(exec_ms)
        exec_ok = all(r == 0 for r in exec_rcs)

        total_stat = stats_ms([c + e for c, e in zip(comp_ms, exec_ms)])
        print(f'  [执行] {exec_stat["n"]}次 均值={exec_stat["avg"]:.2f}ms  '
              f'最小={exec_stat["min"]:.2f}ms  最大={exec_stat["max"]:.2f}ms  '
              f'RC={exec_rcs}')
        print(f'  [总 ] 端到端均值={total_stat["avg"]:.2f}ms')

        rows.append({
            'n_instructions': n,
            'n_qubits': 4,
            'bc_size': bc_sz,
            'compiler': {'rc_all_pass': comp_ok, 'stats_ms': comp_stat,
                         'rss_avg_kb': statistics.mean(comp_rss)},
            'executor': {'rc_all_pass': exec_ok, 'stats_ms': exec_stat,
                         'rss_avg_kb': statistics.mean(exec_rss)},
            'end_to_end_ms': total_stat,
            'compiler_stdout_sample': comp_so.strip()[:200],
        })

    report['performance'] = rows
    return rows


# =====================================================================
# 3. 稳定性测试: 多轮迭代, 崩溃/内存泄漏检测
# =====================================================================
def stability_test():
    print_sep('【3. 稳定性测试: 多轮迭代无崩溃/无内存泄漏】')
    bell = BASE / 'test' / 'bell_state.qentl'
    tmpbc = '/tmp/bench_stability.qbc'

    # 3a. 连续 N_STABILITY 轮 C编译+QVM执行
    print(f'\n  3a. bell_state 连续 {N_STABILITY} 轮迭代 (RC + RSS 跟踪)')
    rss_history = []
    crashes = 0
    bad_rc = 0
    times = []
    for i in range(N_STABILITY):
        rc1, so1, se1, t1, u1, s1, rss1 = run_once([str(QCL), str(bell), tmpbc], cwd=BASE)
        if rc1 != 0:
            bad_rc += 1
            rss_history.append(rss1)
            times.append(t1)
            continue
        rc2, so2, se2, t2, u2, s2, rss2 = run_once([str(QVM), tmpbc], cwd=BASE)
        if rc2 != 0:
            bad_rc += 1
        rss_history.append(rss2)
        times.append(t1 + t2)

    # 3b. 1000指令连续迭代(更严格)
    print(f'\n  3b. 1000指令连续 {N_STABILITY} 轮迭代')
    qentl1000, qbc1000 = gen_circuit(1000, n_qubits=4)
    rss_history_1000 = []
    bad_rc_1000 = 0
    for i in range(N_STABILITY):
        rc1, so1, se1, t1, u1, s1, rss1 = run_once([str(QCL), qentl1000, qbc1000], cwd=BASE)
        if rc1 != 0:
            bad_rc_1000 += 1
            continue
        rc2, so2, se2, t2, u2, s2, rss2 = run_once([str(QVM), qbc1000], cwd=BASE)
        if rc2 != 0:
            bad_rc_1000 += 1
        rss_history_1000.append(rss2)

    # 3c. 内存泄漏判定: 检测 RSS 序列是否存在单调上升趋势
    def detect_leak(rss_seq):
        if len(rss_seq) < 4:
            return False, 0
        # 用相邻差均值: 若持续正增长则视为泄漏
        diffs = [rss_seq[i+1] - rss_seq[i] for i in range(len(rss_seq)-1)]
        pos_diffs = sum(1 for d in diffs if d > 0)
        trend = statistics.mean(diffs) if diffs else 0
        leak = (pos_diffs / len(diffs) > 0.7) and (trend > 50)  # >70%递增且每轮增>50KB
        return leak, trend

    bell_leak, bell_trend = detect_leak(rss_history)
    k1000_leak, k1000_trend = detect_leak(rss_history_1000)

    print(f'  bell_state: {N_STABILITY}轮, 异常RC={bad_rc}, '
          f'RSS均值={statistics.mean(rss_history):.0f}KB ± {statistics.stdev(rss_history) if len(rss_history)>1 else 0:.0f}KB, '
          f'RSS趋势={bell_trend:.1f}KB/run, 泄漏={bell_leak}')
    print(f'  1000ops:    {N_STABILITY}轮, 异常RC={bad_rc_1000}, '
          f'RSS均值={statistics.mean(rss_history_1000):.0f}KB ± {statistics.stdev(rss_history_1000) if len(rss_history_1000)>1 else 0:.0f}KB, '
          f'RSS趋势={k1000_trend:.1f}KB/run, 泄漏={k1000_leak}')

    stability_pass = (bad_rc == 0) and (bad_rc_1000 == 0) and (not bell_leak) and (not k1000_leak)
    report['stability'] = {
        'bell_state': {
            'n_runs': N_STABILITY, 'bad_rc': bad_rc,
            'rss_mean_kb': statistics.mean(rss_history),
            'rss_stdev_kb': statistics.stdev(rss_history) if len(rss_history)>1 else 0,
            'rss_trend_kb_per_run': bell_trend,
            'leak_detected': bell_leak,
            'pass': bad_rc == 0 and not bell_leak,
        },
        '1000ops': {
            'n_runs': N_STABILITY, 'bad_rc': bad_rc_1000,
            'rss_mean_kb': statistics.mean(rss_history_1000) if rss_history_1000 else 0,
            'rss_stdev_kb': statistics.stdev(rss_history_1000) if len(rss_history_1000)>1 else 0,
            'rss_trend_kb_per_run': k1000_trend,
            'leak_detected': k1000_leak,
            'pass': bad_rc_1000 == 0 and not k1000_leak,
        },
        'overall_pass': stability_pass,
    }
    print(f'  稳定性结果: {"PASS ✓" if stability_pass else "FAIL ✗"}')


# =====================================================================
# 4. 优化版对比(可选, 二进制存在时)
# =====================================================================
def opt_compare():
    print_sep('【4. 优化版对比 (静态+strip)】')
    if not QCL_OPT.exists() or not QVM_OPT.exists():
        print('  [SKIP] 优化版二进制不存在')
        return

    bell = BASE / 'test' / 'bell_state.qentl'
    tmpbc = '/tmp/bench_opt_compare.qbc'

    # 原始
    rc1, so1, se1, t1, u1, s1, rss1 = run_once([str(QCL), str(bell), tmpbc], cwd=BASE)
    rc2, so2, se2, t2, u2, s2, rss2 = run_once([str(QVM), tmpbc], cwd=BASE)
    orig_total = t1 + t2

    # 优化
    rc3, so3, se3, t3, u3, s3, rss3 = run_once([str(QCL_OPT), str(bell), tmpbc], cwd=BASE)
    rc4, so4, se4, t4, u4, s4, rss4 = run_once([str(QVM_OPT), tmpbc], cwd=BASE)
    opt_total = t3 + t4

    print(f'  原始版: 编译={t1:.2f}ms  执行={t2:.2f}ms  总={orig_total:.2f}ms  RSS={rss2}KB')
    print(f'  优化版: 编译={t3:.2f}ms  执行={t4:.2f}ms  总={opt_total:.2f}ms  RSS={rss4}KB')
    speedup = orig_total / opt_total if opt_total > 0 else 0
    print(f'  加速比: {speedup:.2f}x')

    report['stability']['opt_compare'] = {
        'orig_compiler_ms': t1, 'orig_vm_ms': t2, 'orig_total_ms': orig_total,
        'orig_rss_kb': rss2,
        'opt_compiler_ms': t3, 'opt_vm_ms': t4, 'opt_total_ms': opt_total,
        'opt_rss_kb': rss4,
        'speedup': speedup,
    }


# =====================================================================
# 主流程
# =====================================================================
def main():
    t_start = time.perf_counter()
    print('=' * 70)
    print('  QSM 八阶段: 自举链端到端集成测试与性能基准')
    print('=' * 70)

    # 预检二进制
    print('\n[预检] 二进制就绪:')
    for label, p in [('QCL编译器', QCL), ('QVM虚拟机', QVM)]:
        ready = p.exists() and os.access(p, os.X_OK)
        print(f'  {label}: {"✓" if ready else "✗"}  {p}')

    binary_info()
    e2e_baseline()
    rows = perf_bench()
    stability_test()
    opt_compare()

    t_total = (time.perf_counter() - t_start) * 1000
    report['meta']['total_ms'] = t_total

    # 汇总
    e2e_pass = report['e2e_tests']['bell_state']['pass']
    perf_all_pass = all(r['compiler']['rc_all_pass'] and r['executor']['rc_all_pass']
                        for r in report['performance'])
    stab_pass = report['stability']['overall_pass']
    report['summary'] = {
        'e2e_pass': e2e_pass,
        'perf_all_sizes_pass': perf_all_pass,
        'stability_pass': stab_pass,
        'overall_pass': e2e_pass and perf_all_pass and stab_pass,
    }

    # 导出 JSON
    json_path = OUT / 'stage8_bootstrap_e2e_report.json'
    with open(json_path, 'w') as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)
    print(f'\n  JSON报告: {json_path}')

    # 生成 Markdown
    md = generate_markdown(rows)
    md_path = OUT / 'stage8_bootstrap_e2e_report.md'
    with open(md_path, 'w') as f:
        f.write(md)
    print(f'  Markdown报告: {md_path}')

    print_sep('【汇总】')
    s = report['summary']
    print(f'  端到端基线:   {"PASS ✓" if s["e2e_pass"] else "FAIL ✗"}')
    print(f'  性能基准(3档): {"PASS ✓" if s["perf_all_sizes_pass"] else "FAIL ✗"}')
    print(f'  稳定性:       {"PASS ✓" if s["stability_pass"] else "FAIL ✗"}')
    print(f'  总体:         {"PASS ✓" if s["overall_pass"] else "FAIL ✗"}  '
          f'(耗时={t_total:.0f}ms)')


def generate_markdown(perf_rows):
    s = report['summary']
    lines = [
        '# QSM 八阶段 — 自举链端到端集成测试与性能基准报告',
        '',
        '## 测试链',
        '```',
        'C编译器 (bin/qcl_bootstrap) → QCL引导器(编译输出 .qbc) → QVM虚拟机 (bin/qvm_bootstrap) → 量子程序执行',
        '```',
        '',
        '## 1. 二进制信息',
        '',
        '| 组件 | 大小 | 类型 |',
        '|---|---|---|',
    ]
    for label, info in report['binary_info'].items():
        sz = info['size_bytes']
        sz_str = f'{sz/1024:.1f}KB' if sz > 0 else 'N/A'
        lines.append(f'| {label} | {sz_str} | {info["kind"]} |')

    lines += ['', '## 2. 端到端基线 (Bell态 |Φ⁺⟩)', '']
    e2e = report.get('e2e_tests', {}).get('bell_state', {})
    lines.append(f'- C编译器: rc={e2e.get("compiler_rc")}, 耗时={e2e.get("compiler_ms", 0):.2f}ms')
    lines.append(f'- QVM虚拟机: rc={e2e.get("vm_rc")}, 耗时={e2e.get("vm_ms", 0):.2f}ms')
    lines.append(f'- 端到端总耗时: {e2e.get("total_ms", 0):.2f}ms')
    lines.append(f'- 字节码大小: {e2e.get("bc_size")}B')
    lines.append(f'- 结果: {"PASS ✓" if e2e.get("pass") else "FAIL ✗"}')

    lines += ['', '## 3. 性能基准: 不同指令数量对比', '',
              '| 指令数 | 字节码(B) | 编译均值(ms) | 编译最小 | 编译最大 | 执行均值(ms) | 执行最小 | 执行最大 | 端到端均值(ms) | 编译PASS | 执行PASS |',
              '|---|---|---|---|---|---|---|---|---|---|---|']
    for r in perf_rows:
        c = r['compiler']['stats_ms']
        e = r['executor']['stats_ms']
        t = r['end_to_end_ms']
        lines.append(
            f'| {r["n_instructions"]} | {r["bc_size"]} | '
            f'{c["avg"]:.2f} | {c["min"]:.2f} | {c["max"]:.2f} | '
            f'{e["avg"]:.2f} | {e["min"]:.2f} | {e["max"]:.2f} | '
            f'{t["avg"]:.2f} | {"✓" if r["compiler"]["rc_all_pass"] else "✗"} | '
            f'{"✓" if r["executor"]["rc_all_pass"] else "✗"} |'
        )

    lines += ['', '### 编译性能扩展比', '']
    ms_comp = {r['n_instructions']: r['compiler']['stats_ms']['avg'] for r in perf_rows}
    for n in sorted(ms_comp):
        base = ms_comp.get(10, 1)
        ratio = ms_comp[n] / base if base > 0 else 0
        lines.append(f'- {n}指令编译: {ms_comp[n]:.2f}ms  (vs 10指令 {ratio:.1f}x)')

    lines += ['', '### 执行性能扩展比', '']
    ms_exec = {r['n_instructions']: r['executor']['stats_ms']['avg'] for r in perf_rows}
    for n in sorted(ms_exec):
        base = ms_exec.get(10, 1)
        ratio = ms_exec[n] / base if base > 0 else 0
        lines.append(f'- {n}指令执行: {ms_exec[n]:.2f}ms  (vs 10指令 {ratio:.1f}x)')

    lines += ['', '## 4. 稳定性验证', '']
    stab = report['stability']
    for label in ['bell_state', '1000ops']:
        d = stab.get(label, {})
        lines.append(f'### {label}')
        lines.append(f'- 迭代次数: {d.get("n_runs")}')
        lines.append(f'- 异常退出码: {d.get("bad_rc")}')
        lines.append(f'- RSS均值: {d.get("rss_mean_kb", 0):.0f}KB ± {d.get("rss_stdev_kb", 0):.0f}KB')
        lines.append(f'- RSS趋势: {d.get("rss_trend_kb_per_run", 0):.1f}KB/run')
        lines.append(f'- 内存泄漏: {"是 ✗" if d.get("leak_detected") else "否 ✓"}')
        lines.append(f'- 结果: {"PASS ✓" if d.get("pass") else "FAIL ✗"}')
        lines.append('')

    opt = stab.get('opt_compare', {})
    if opt:
        lines += ['', '## 5. 优化版对比 (静态编译+strip)', '']
        lines.append(f'- 原始版: 编译={opt.get("orig_compiler_ms",0):.2f}ms  执行={opt.get("orig_vm_ms",0):.2f}ms  总={opt.get("orig_total_ms",0):.2f}ms  RSS={opt.get("orig_rss_kb")}KB')
        lines.append(f'- 优化版: 编译={opt.get("opt_compiler_ms",0):.2f}ms  执行={opt.get("opt_vm_ms",0):.2f}ms  总={opt.get("opt_total_ms",0):.2f}ms  RSS={opt.get("opt_rss_kb")}KB')
        lines.append(f'- 加速比: {opt.get("speedup", 0):.2f}x')

    lines += ['', '## 6. 总体结果', '']
    lines.append(f'- 端到端基线: {"PASS ✓" if s["e2e_pass"] else "FAIL ✗"}')
    lines.append(f'- 性能基准(3档): {"PASS ✓" if s["perf_all_sizes_pass"] else "FAIL ✗"}')
    lines.append(f'- 稳定性: {"PASS ✓" if s["stability_pass"] else "FAIL ✗"}')
    lines.append(f'- **总体: {"PASS ✓" if s["overall_pass"] else "FAIL ✗"}**  (总耗时 {report["meta"].get("total_ms", 0):.0f}ms)')
    lines.append('')
    lines += ['', '## 7. 各环节输出样本', '']
    for r in perf_rows:
        lines.append(f'### {r["n_instructions"]}指令编译输出')
        lines.append('```')
        lines.append(r.get('compiler_stdout_sample', '(无)')[:300])
        lines.append('```')
        lines.append('')

    return '\n'.join(lines)


if __name__ == '__main__':
    main()
