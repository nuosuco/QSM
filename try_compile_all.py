#!/usr/bin/env python3
"""完整编译所有 186 个缺失 .qbc 的 .qentl，区分有效编译 vs 空占位"""
import os, subprocess, glob

ROOT = "/root/QSM"
BUILD_DIR = os.path.join(ROOT, "build", "compiled")
COMPILER = os.path.join(ROOT, "bin", "qentl_compiler")

sys_qentl = sorted(glob.glob(os.path.join(ROOT, "QEntL", "System", "**", "*.qentl"), recursive=True))
cli_skip = [p for p in sys_qentl if "/bin/cli/" in p or "/bin/platform/" in p]
sys_source = [p for p in sys_qentl if p not in cli_skip]
root_scripts = sorted(glob.glob(os.path.join(ROOT, "QEntL", "scripts", "*.qentl")))

missing_files = []
for p in sys_source + root_scripts:
    name = os.path.splitext(os.path.basename(p))[0]
    if not (os.path.exists(os.path.join(BUILD_DIR, name + ".qbc"))
            or os.path.exists(os.path.join(BUILD_DIR, name + ".qentl.qbc"))):
        missing_files.append(p)

print(f"编译全部 {len(missing_files)} 个缺失文件...")
ok_real = 0      # 生成 >1 字节的 .qbc
ok_empty = 0     # 生成 1 字节空占位
fail = 0
empty_files = []

for p in missing_files:
    name = os.path.splitext(os.path.basename(p))[0]
    out_path = os.path.join(BUILD_DIR, name + ".qbc")
    # 若已有（上一轮生成的 1B）则先删掉
    if os.path.exists(out_path):
        os.remove(out_path)
    try:
        r = subprocess.run([COMPILER, p, out_path], capture_output=True, text=True, timeout=30)
        if r.returncode == 0 and os.path.exists(out_path):
            sz = os.path.getsize(out_path)
            if sz > 1:
                ok_real += 1
            else:
                ok_empty += 1
                empty_files.append(os.path.relpath(p, ROOT))
        else:
            fail += 1
    except Exception:
        fail += 1

print("=" * 55)
print(f"总编译:      {len(missing_files)}")
print(f"有效编译(>1B): {ok_real}")
print(f"空占位(=1B):   {ok_empty}")
print(f"失败/超时:     {fail}")
print("=" * 55)
if empty_files:
    print(f"\n生成空占位的文件 (前30):")
    for f in empty_files[:30]:
        print(f"  - {f}")
    if len(empty_files) > 30:
        print(f"  ... 还有 {len(empty_files)-30} 个")
