#!/usr/bin/env python3
"""
自举链性能与稳定性测试报告生成器
- 稳定性: >1000指令, >64量子比特, 复杂控制流, buffer边界
- 性能: 原始 vs 优化 (mmap/静态编译/strip) 5次均值
- 内存: RSS/VSZ
- CPU: 运行时间
"""
import subprocess, time, os, sys, resource

BASE = '/root/QSM'
RUNS = 5

def run_n_times(cmd, n=RUNS, capture=False, env_extra=None):
    """运行n次，返回 (real_ms列表, user_ms, sys_ms, output, returncode)"""
    reals, users, syss = [], [], []
    outputs = []
    last_rc = 0
    for _ in range(n):
        p = subprocess.run(cmd, shell=True, capture_output=capture,
                           text=capture, env=env_extra or None)
        outputs.append(p.stdout if capture else '')
        last_rc = p.returncode
    return reals, users, syss, outputs, last_rc

def bench_binary(binary, arg, n=RUNS):
    """精确计时n次，返回平均毫秒"""
    times = []
    for _ in range(n):
        t0 = time.perf_counter()
        p = subprocess.run([binary] + ([arg] if arg else []),
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                           cwd=BASE)
        t1 = time.perf_counter()
        times.append((t1 - t0) * 1000)
        if p.returncode != 0:
            times[-1] = -p.returncode  # 标记失败
    return times

def peak_rss_kb(binary, arg=None):
    """测量RSS峰值(KB) — Linux RUSAGE"""
    cmd = [binary] + ([arg] if arg else [])
    try:
        p = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=BASE)
        p.wait()
        # 子进程RSS
        r = resource.getrusage(resource.RUSAGE_CHILDREN)
        return r.ru_maxrss  # Linux: KB
    except Exception:
        return -1

def file_size(path):
    try:
        return os.path.getsize(path)
    except:
        return -1

def main():
    results = {}
    
    # 二进制路径
    qcl_orig = os.path.join(BASE, 'bin/qcl_bootstrap')
    qvm_orig = os.path.join(BASE, 'bin/qvm_bootstrap')
    qcl_opt = os.path.join(BASE, 'bin/qcl_bootstrap_opt')
    qvm_opt = os.path.join(BASE, 'bin/qvm_bootstrap_opt')
    
    # 测试文件
    bell_qentl = os.path.join(BASE, 'test/bell_state.qentl')
    
    print("=" * 70)
    print("  QSM 八阶段: C语言自举链稳定性与性能优化报告")
    print("=" * 70)
    
    # ===== 1. 二进制大小对比 =====
    print("\n【1. 二进制文件大小对比】")
    sizes = {}
    for name, path in [('qcl_orig', qcl_orig), ('qvm_orig', qvm_orig),
                        ('qcl_opt', qcl_opt), ('qvm_opt', qvm_opt)]:
        sz = file_size(path)
        sizes[name] = sz
        print(f"  {name:14s}: {sz:>8d} bytes ({sz/1024:>6.1f} KB)  {'[静态+strip]' if 'opt' in name else '[动态+未strip]'}")
    
    # ===== 2. 编译性能测试 =====
    print("\n【2. 编译性能测试 (QCL, bell_state.qentl, 5次均值)】")
    
    for name, compiler in [('原始版本', qcl_orig), ('优化版本', qcl_opt)]:
        times = bench_binary(compiler, bell_qentl)
        good = [t for t in times if t > 0]
        avg = sum(good) / len(good) if good else 0
        print(f"  {name:8s}: 均值={avg:.2f}ms  min={min(good):.2f}ms  max={max(good):.2f}ms  (n={len(good)})")
        results[f'{name}_compile_avg'] = avg
    
    # ===== 3. 执行性能测试 =====
    print("\n【3. 执行性能测试 (QVM, bell_state.qbc, 5次均值)】")
    # 先用各自编译器生成qbc
    subprocess.run([qcl_orig, bell_qentl, '/tmp/bench_bell_orig.qbc'],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=BASE)
    subprocess.run([qcl_opt, bell_qentl, '/tmp/bench_bell_opt.qbc'],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=BASE)
    
    for name, vm, qbc in [('原始版本', qvm_orig, '/tmp/bench_bell_orig.qbc'),
                           ('优化版本', qvm_opt, '/tmp/bench_bell_opt.qbc')]:
        times = bench_binary(vm, qbc)
        good = [t for t in times if t > 0]
        avg = sum(good) / len(good) if good else 0
        print(f"  {name:8s}: 均值={avg:.2f}ms  min={min(good):.2f}ms  max={max(good):.2f}ms  (n={len(good)})")
        results[f'{name}_exec_avg'] = avg
    
    # ===== 4. 内存使用分析 =====
    print("\n【4. 内存使用分析 (RSS峰值, KB)】")
    for name, binary, arg in [('QCL原始', qcl_orig, bell_qentl),
                               ('QCL优化', qcl_opt, bell_qentl),
                               ('QVM原始', qvm_orig, '/tmp/bench_bell_orig.qbc'),
                               ('QVM优化', qvm_opt, '/tmp/bench_bell_opt.qbc')]:
        rss = peak_rss_kb(binary, arg)
        print(f"  {name:10s}: RSS峰值 = {rss:>6d} KB ({rss/1024:.2f} MB)")
        results[f'{name}_rss'] = rss
    
    # ===== 5. 极端稳定性测试 =====
    print("\n【5. 极端稳定性测试】")
    stress_tests = {
        '大量指令(>1000)': 'test/stability/stress_1000ops.qentl',
        '大量量子比特(>64)': 'test/stability/stress_72qubits.qentl',
        '复杂控制流': 'test/stability/stress_complex_ctrl.qentl',
        'Buffer边界': 'test/stability/stress_buffer.qentl',
    }
    
    for label, test_file in stress_tests.items():
        fpath = os.path.join(BASE, test_file)
        if not os.path.exists(fpath):
            print(f"  [SKIP] {label}: 文件不存在 {test_file}")
            continue
        
        for ver, compiler, vm in [('原始', qcl_orig, qvm_orig), ('优化', qcl_opt, qvm_opt)]:
            qbc = f'/tmp/stress_{ver}.qbc'
            p1 = subprocess.run([compiler, fpath, qbc],
                                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                cwd=BASE, timeout=30)
            if p1.returncode != 0:
                print(f"  [{label}] {ver}版本 编译失败 (rc={p1.returncode})")
                continue
            p2 = subprocess.run([vm, qbc],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                cwd=BASE, timeout=60)
            ok = (p2.returncode == 0)
            print(f"  [{label}] {ver}版本 {'PASS' if ok else 'FAIL'} (编译+执行 rc={p2.returncode})")
    
    print("\n" + "=" * 70)
    print("  总结")
    print("=" * 70)
    
    # 性能提升计算
    comp_orig = results.get('原始版本_compile_avg', 0)
    comp_opt = results.get('优化版本_compile_avg', 0)
    exec_orig = results.get('原始版本_exec_avg', 0)
    exec_opt = results.get('优化版本_exec_avg', 0)
    
    if comp_orig > 0 and comp_opt > 0:
        print(f"\n  编译性能提升: {comp_orig:.2f}ms → {comp_opt:.2f}ms  "
              f"(加速 {comp_orig/comp_opt:.1f}x, 提升 {(comp_orig-comp_opt)/comp_orig*100:.0f}%)")
    if exec_orig > 0 and exec_opt > 0:
        print(f"  执行性能提升: {exec_orig:.2f}ms → {exec_opt:.2f}ms  "
              f"(加速 {exec_orig/exec_opt:.1f}x, 提升 {(exec_orig-exec_opt)/exec_orig*100:.0f}%)")
    
    print(f"\n  二进制大小: QCL {sizes.get('qcl_orig',0)//1024}KB → {sizes.get('qcl_opt',0)//1024}KB, "
          f"QVM {sizes.get('qvm_orig',0)//1024}KB → {sizes.get('qvm_opt',0)//1024}KB")
    
    # 静态编译+strip说明
    print(f"\n  优化方案:")
    print(f"    1. mmap替代fopen — 减少I/O系统调用（零拷贝读取）")
    print(f"    2. MADV_SEQUENTIAL — 提示内核顺序预读")
    print(f"    3. MAP_POPULATE — 预先填充页表，减少缺页中断")
    print(f"    4. 静态编译(-static) — 消除动态链接器开销")
    print(f"    5. strip — 移除符号表，减少二进制大小")
    
    # 导出JSON
    import json
    report = {
        'sizes': sizes,
        'compile_performance': results,
        'execution_performance': results,
        'memory_rss_kb': {k: v for k, v in results.items() if 'rss' in k},
        'stress_tests': list(stress_tests.keys()),
    }
    out_path = os.path.join(BASE, 'reports', 'stage8_bootstrap_perf_report.json')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    print(f"\n  报告已导出: {out_path}")

if __name__ == '__main__':
    main()
