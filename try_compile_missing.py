#!/usr/bin/env python3
"""尝试编译缺失 .qbc 的 .qentl 文件"""
import os, subprocess, glob

ROOT = "/root/QSM"
BUILD_DIR = os.path.join(ROOT, "build", "compiled")
COMPILER = os.path.join(ROOT, "bin", "qentl_compiler")

# 取缺失文件列表（System/ 下 + scripts）
sys_qentl = sorted(glob.glob(os.path.join(ROOT, "QEntL", "System", "**", "*.qentl"), recursive=True))
cli_skip = [p for p in sys_qentl if "/bin/cli/" in p or "/bin/platform/" in p]
sys_source = [p for p in sys_qentl if p not in cli_skip]
root_scripts = sorted(glob.glob(os.path.join(ROOT, "QEntL", "scripts", "*.qentl")))

missing_files = []
for p in sys_source + root_scripts:
    name = os.path.splitext(os.path.basename(p))[0]
    qbc_name = name + ".qbc"
    qbc_name2 = name + ".qentl.qbc"
    if not (os.path.exists(os.path.join(BUILD_DIR, qbc_name))
            or os.path.exists(os.path.join(BUILD_DIR, qbc_name2))):
        missing_files.append(p)

print(f"待编译文件数: {len(missing_files)}")
print(f"编译器: {COMPILER}")
print("=" * 60)

success = 0
fail = 0
errors = []

# 尝试编译前 20 个文件（演示用，全部编译时间很长）
LIMIT = min(20, len(missing_files))
for i, p in enumerate(missing_files[:LIMIT]):
    name = os.path.splitext(os.path.basename(p))[0]
    out_path = os.path.join(BUILD_DIR, name + ".qbc")
    try:
        result = subprocess.run(
            [COMPILER, p, out_path],
            capture_output=True, text=True, timeout=30
        )
        rc = result.returncode
        out_file_exists = os.path.exists(out_path)
        if rc == 0 and out_file_exists:
            size = os.path.getsize(out_path)
            print(f"[OK]   {os.path.relpath(p, ROOT)} -> {name}.qbc ({size}B)")
            success += 1
        else:
            stderr = result.stderr.strip()[:200] if result.stderr else result.stdout.strip()[:200]
            print(f"[FAIL] {os.path.relpath(p, ROOT)} (rc={rc}, out_exists={out_file_exists})")
            print(f"       msg: {stderr}")
            errors.append((p, stderr))
            fail += 1
    except subprocess.TimeoutExpired:
        print(f"[TIMEOUT] {os.path.relpath(p, ROOT)}")
        fail += 1
        errors.append((p, "timeout"))
    except Exception as e:
        print(f"[ERROR]  {os.path.relpath(p, ROOT)}: {e}")
        fail += 1
        errors.append((p, str(e)))

print("=" * 60)
print(f"结果: 成功 {success}, 失败/超时 {fail}, 跳过 {len(missing_files)-LIMIT}")
