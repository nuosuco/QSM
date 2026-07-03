#!/usr/bin/env python3
"""
QCL模块一次性引导编译脚本
用 bin/qcl_bootstrap --phase2 模式编译所有QCL模块的.qentl文件
"""
import subprocess
import os
import sys

QSM_ROOT = "/root/QSM"
COMPILER = os.path.join(QSM_ROOT, "bin", "qcl_bootstrap")

FILES = [
    ("qcl_opcodes.qentl", "qcl_opcodes.qbc"),
    ("qcl_lexer.qentl", "qcl_lexer.qbc"),
    ("qcl_parser.qentl", "qcl_parser.qbc"),
    ("qcl_parser_high.qentl", "qcl_parser_high.qbc"),
    ("qcl_bootstrap_phase2.qentl", "qcl_bootstrap_phase2.qbc"),
    ("qcl_compiler_phase2.qentl", "qcl_compiler_phase2.qbc"),
]

def compile_file(in_name, out_name):
    """编译单个文件"""
    in_path = os.path.join(QSM_ROOT, "QCL模块", in_name)
    out_path = os.path.join(QSM_ROOT, "QCL模块", out_name)
    
    if not os.path.exists(in_path):
        print(f"❌ {in_name}: 源文件不存在")
        return False, 0
    
    # 删除旧的.qbc
    if os.path.exists(out_path):
        os.remove(out_path)
    
    # 用 --phase2 模式编译
    cmd = [COMPILER, "--phase2", in_path, out_path]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, cwd=QSM_ROOT)
        stdout = result.stdout
        stderr = result.stderr
    except subprocess.TimeoutExpired:
        print(f"⏱️ {in_name}: 超时")
        return False, 0
    except Exception as e:
        print(f"❌ {in_name}: 执行失败 - {e}")
        return False, 0
    
    # 验证输出文件
    if not os.path.exists(out_path):
        print(f"❌ {in_name}: 输出文件未生成 (exit={result.returncode})")
        if stderr:
            print(f"   stderr: {stderr[:200]}")
        return False, 0
    
    size = os.path.getsize(out_path)
    
    # 验证不是空壳（>1字节）
    if size <= 1:
        print(f"⚠️  {in_name} → {out_name}: {size} 字节 (空壳！)")
        if stdout:
            print(f"   stdout: {stdout[:300]}")
        if stderr:
            print(f"   stderr: {stderr[:200]}")
        return False, size
    
    # 成功
    print(f"✅ {in_name} → {out_name}: {size} 字节")
    # 打印编译器输出摘要
    lines = stdout.strip().split('\n')
    for ln in lines:
        ln = ln.strip()
        if ln and ('编译完成' in ln or '输入' in ln or '输出' in ln or '字节码' in ln or '编译行' in ln or '函数定义' in ln):
            print(f"   {ln}")
    if stderr:
        err_short = stderr.strip().split('\n')[0][:150]
        if err_short:
            print(f"   stderr: {err_short}")
    return True, size

def main():
    print("=" * 60)
    print("QCL模块一次性引导编译 — 使用 --phase2 模式")
    print(f"编译器: {COMPILER}")
    print("=" * 60)
    
    if not os.path.exists(COMPILER):
        print(f"❌ 编译器不存在: {COMPILER}")
        sys.exit(1)
    
    results = {}
    success_count = 0
    total_size = 0
    
    for in_name, out_name in FILES:
        ok, size = compile_file(in_name, out_name)
        results[in_name] = (ok, size)
        if ok:
            success_count += 1
            total_size += size
    
    print("\n" + "=" * 60)
    print("编译结果汇总")
    print("=" * 60)
    for in_name, out_name in FILES:
        ok, size = results[in_name]
        status = "✅" if ok else "❌"
        size_str = f"{size} 字节" if size > 0 else "空壳"
        print(f"  {status} {in_name:40s} → {out_name:40s} {size_str}")
    
    print(f"\n成功: {success_count}/{len(FILES)}")
    print(f"总字节码大小: {total_size} 字节")
    
    if success_count < len(FILES):
        print(f"\n⚠️ 有 {len(FILES) - success_count} 个文件未成功编译（可能是空壳）")
    
    return 0 if success_count == len(FILES) else 1

if __name__ == "__main__":
    sys.exit(main())
