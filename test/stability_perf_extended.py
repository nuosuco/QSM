#!/usr/bin/env python3
"""
八阶段扩展测试：大工作量编译/执行 + 内存精确测量
"""
import subprocess, time, os, sys

BASE = '/root/QSM'
RUNS = 5

def bench_cmd(cmd, args, n=RUNS):
    """perf_counter精确计时"""
    times = []
    for _ in range(n):
        t0 = time.perf_counter()
        p = subprocess.run(cmd + args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=BASE)
        t1 = time.perf_counter()
        times.append((t1 - t0) * 1000)
    return times

def rss_from_vmstat(pid_file='/tmp/rss_capture.txt'):
    """通过/proc或ps测量子进程RSS峰值"""
    pass

def measure_rss_v2(cmd, args):
    """测量RSS (KB) 通过ps抓取进程运行时的RSS"""
    import resource
    p = subprocess.Popen(cmd + args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=BASE)
    p.wait()
    r = resource.getrusage(resource.RUSAGE_CHILDREN)
    return r.ru_maxrss  # KB

def stress_compile(compiler, test_file):
    """对大工作量文件编译+执行并计时"""
    fpath = os.path.join(BASE, test_file)
    if not os.path.exists(fpath):
        return None, None, "NOT_FOUND"
    qbc = '/tmp/stress_bench.qbc'
    # 编译计时
    t0 = time.perf_counter()
    p1 = subprocess.run([compiler, fpath, qbc], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=BASE, timeout=30)
    t1 = time.perf_counter()
    compile_ms = (t1 - t0) * 1000
    if p1.returncode != 0:
        return compile_ms, None, f"compile_fail(rc={p1.returncode})"
    # 执行计时
    t0 = time.perf_counter()
    p2 = subprocess.run([compiler.replace('qcl_bootstrap', 'qvm_bootstrap') if 'qcl' in compiler else '', qbc],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=BASE, timeout=60)
    # 正确方式：找对应vm
    vm = os.path.join(BASE, 'bin/qvm_bootstrap') if 'qcl_orig' not in str(compiler) else os.path.join(BASE, 'bin/qvm_bootstrap')
    t1 = time.perf_counter()
    exec_ms = (t1 - t0) * 1000
    return compile_ms, exec_ms, "OK"

def main():
    qcl_orig = os.path.join(BASE, 'bin/qcl_bootstrap')
    qvm_orig = os.path.join(BASE, 'bin/qvm_bootstrap')
    qcl_opt = os.path.join(BASE, 'bin/qcl_bootstrap_opt')
    qvm_opt = os.path.join(BASE, 'bin/qvm_bootstrap_opt')
    
    # 1. 大工作量：stress_1000ops
    print("=" * 60)
    print("  大工作量测试: stress_1000ops.qentl")
    print("=" * 60)
    
    stress_file = 'test/stability/stress_1000ops.qentl'
    for label, compiler, vm in [('原始', qcl_orig, qvm_orig), ('优化', qcl_opt, qvm_opt)]:
        times_c = bench_cmd([compiler], [os.path.join(BASE, stress_file), '/tmp/stress_1000_opt.qbc'], RUNS)
        avg_c = sum(times_c) / len(times_c)
        # 先编译一次
        subprocess.run([compiler, os.path.join(BASE, stress_file), '/tmp/stress_1000_exec.qbc'],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=BASE)
        times_e = bench_cmd([vm], ['/tmp/stress_1000_exec.qbc'], RUNS)
        avg_e = sum(times_e) / len(times_e)
        rss = measure_rss_v2([vm], ['/tmp/stress_1000_exec.qbc'])
        print(f"  {label}版本: 编译={avg_c:.2f}ms  执行={avg_e:.2f}ms  RSS={rss/1024:.2f}MB")
    
    # 2. 大工作量：stress_72qubits
    print("\n" + "=" * 60)
    print("  大工作量测试: stress_72qubits.qentl (72量子比特, 简化模式)")
    print("=" * 60)
    
    stress_file2 = 'test/stability/stress_72qubits.qentl'
    for label, compiler, vm in [('原始', qcl_orig, qvm_orig), ('优化', qcl_opt, qvm_opt)]:
        times_c = bench_cmd([compiler], [os.path.join(BASE, stress_file2), '/tmp/stress_72_opt.qbc'], RUNS)
        avg_c = sum(times_c) / len(times_c)
        subprocess.run([compiler, os.path.join(BASE, stress_file2), '/tmp/stress_72_exec.qbc'],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=BASE)
        times_e = bench_cmd([vm], ['/tmp/stress_72_exec.qbc'], RUNS)
        avg_e = sum(times_e) / len(times_e)
        rss = measure_rss_v2([vm], ['/tmp/stress_72_exec.qbc'])
        print(f"  {label}版本: 编译={avg_c:.2f}ms  执行={avg_e:.2f}ms  RSS={rss/1024:.2f}MB")
    
    # 3. 完整自举链：QCL编译→QVM执行  全链路计时
    print("\n" + "=" * 60)
    print("  完整自举链全链路计时 (bell_state: QCL编译 → QVM执行)")
    print("=" * 60)
    
    bell = os.path.join(BASE, 'test/bell_state.qentl')
    for label, compiler, vm in [('原始', qcl_orig, qvm_orig), ('优化', qcl_opt, qvm_opt)]:
        total_times = []
        for _ in range(RUNS):
            t0 = time.perf_counter()
            # 编译
            subprocess.run([compiler, bell, '/tmp/full_chain.qbc'],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=BASE)
            # 执行
            subprocess.run([vm, '/tmp/full_chain.qbc'],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=BASE)
            t1 = time.perf_counter()
            total_times.append((t1 - t0) * 1000)
        avg = sum(total_times) / len(total_times)
        rss = measure_rss_v2([compiler], [bell])
        print(f"  {label}版本: 全链路={avg:.2f}ms  RSS={rss/1024:.2f}MB")
    
    # 4. 大量指令全链路 (stress_1000ops)
    print("\n" + "=" * 60)
    print("  大量指令全链路 (stress_1000ops: QCL编译 → QVM执行)")
    print("=" * 60)
    
    stress_f = os.path.join(BASE, 'test/stability/stress_1000ops.qentl')
    for label, compiler, vm in [('原始', qcl_orig, qvm_orig), ('优化', qcl_opt, qvm_opt)]:
        total_times = []
        for _ in range(3):  # 大工作量只测3次
            t0 = time.perf_counter()
            subprocess.run([compiler, stress_f, '/tmp/full_chain_stress.qbc'],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=BASE)
            subprocess.run([vm, '/tmp/full_chain_stress.qbc'],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=BASE)
            t1 = time.perf_counter()
            total_times.append((t1 - t0) * 1000)
        avg = sum(total_times) / len(total_times)
        print(f"  {label}版本: 全链路={avg:.2f}ms")
    
    # 5. CPU时间 vs 真实时间比
    print("\n" + "=" * 60)
    print("  CPU使用分析 (user+sys vs real)")
    print("=" * 60)
    
    import resource as res_module
    for label, compiler in [('QCL原始', qcl_orig), ('QCL优化', qcl_opt)]:
        p = subprocess.Popen([compiler, bell, '/tmp/cpu_test.qbc'],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=BASE)
        p.wait()
        r = res_module.getrusage(res_module.RUSAGE_CHILDREN)
        user_sec = r.ru_utime
        sys_sec = r.ru_stime
        print(f"  {label:10s}: user={user_sec*1000:.1f}ms  sys={sys_sec*1000:.1f}ms  "
              f"total_cpu={(user_sec+sys_sec)*1000:.1f}ms")
    
    for label, vm in [('QVM原始', qvm_orig), ('QVM优化', qvm_opt)]:
        subprocess.run([qcl_orig, bell, '/tmp/cpu_test.qbc'],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=BASE)
        p = subprocess.Popen([vm, '/tmp/cpu_test.qbc'],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=BASE)
        p.wait()
        r = res_module.getrusage(res_module.RUSAGE_CHILDREN)
        user_sec = r.ru_utime
        sys_sec = r.ru_stime
        print(f"  {label:10s}: user={user_sec*1000:.1f}ms  sys={sys_sec*1000:.1f}ms  "
              f"total_cpu={(user_sec+sys_sec)*1000:.1f}ms")
    
    print("\n" + "=" * 60)
    print("  CPU使用分析完成")
    print("=" * 60)

if __name__ == '__main__':
    main()
