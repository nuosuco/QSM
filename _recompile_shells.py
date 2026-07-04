#!/usr/bin/env python3
"""批量重新编译所有空壳.qbc文件"""
import os, glob, subprocess, shutil, time

ROOT = "/root/QSM"
COMPILER = os.path.join(ROOT, "bin", "qcl_phase2")
BACKUP_DIR = os.path.join(ROOT, ".qbc_backup_pre_recompile")

os.makedirs(BACKUP_DIR, exist_ok=True)

def is_shell(f):
    sz = os.path.getsize(f)
    if sz == 0:
        return True
    data = open(f, 'rb').read()
    return sz == 1 or data[0] == 0x0c

def count_0x14(f):
    try:
        return open(f, 'rb').read().count(0x14)
    except:
        return 0

# 扫描所有.qbc
all_qbc = sorted(glob.glob(os.path.join(ROOT, "**/*.qbc"), recursive=True))
shells = [f for f in all_qbc if is_shell(f)]

total_14_before = sum(count_0x14(f) for f in all_qbc)
total_14_shell_before = sum(count_0x14(f) for f in shells)

print(f"总.qbc文件数: {len(all_qbc)}")
print(f"空壳.qbc数量: {len(shells)}")
print(f"编译前总0x14数: {total_14_before}")
print(f"编译前空壳0x14数: {total_14_shell_before}")

# 备份所有空壳
for f in shells:
    rel = os.path.relpath(f, ROOT)
    backup = os.path.join(BACKUP_DIR, rel + ".bak")
    os.makedirs(os.path.dirname(backup), exist_ok=True)
    shutil.copy2(f, backup)

# 编译
success = []
failed = []
no_qentl = []

for f in shells:
    qentl = f.replace(".qbc", ".qentl")
    if not os.path.exists(qentl):
        no_qentl.append(f)
        continue
    
    # 先备份当前.qbc
    rel = os.path.relpath(f, ROOT)
    tmp = f + ".tmp"
    shutil.copy2(f, tmp)
    
    t0 = time.time()
    r = subprocess.run([COMPILER, qentl], capture_output=True, cwd=ROOT, timeout=30)
    stderr = r.stderr.decode("utf-8", errors="replace").strip()
    stdout = r.stdout.decode("utf-8", errors="replace").strip()
    dt = time.time() - t0
    
    if r.returncode != 0:
        # 还原
        shutil.move(tmp, f)
        failed.append((f, stderr[-200:] if stderr else stdout[-200:] or "unknown error"))
        continue
    
    # 验证输出是有效0x14
    if os.path.exists(f):
        data = open(f, 'rb').read()
        if len(data) > 0 and data[0] == 0x14:
            success.append(f)
            os.remove(tmp)
        else:
            shutil.move(tmp, f)
            failed.append((f, f"输出首字节不是0x14: 0x{data[0]:02x}"))
    else:
        shutil.move(tmp, f)
        failed.append((f, "输出文件未生成"))

# 统计
total_14_after = sum(count_0x14(f) for f in all_qbc)
shells_after = [f for f in all_qbc if is_shell(f)]
total_14_shell_after = sum(count_0x14(f) for f in shells_after)

print("\n" + "="*60)
print("编译完成统计")
print("="*60)
print(f"编译前空壳数量: {len(shells)}")
print(f"有.qentl源的空壳: {len(shells) - len(no_qentl)}")
print(f"无.qentl源的空壳: {len(no_qentl)}")
print(f"成功编译: {len(success)}")
print(f"编译失败: {len(failed)}")
print(f"编译后剩余空壳: {len(shells_after)}")
print(f"编译前总0x14数: {total_14_before}")
print(f"编译后总0x14数: {total_14_after}")
print(f"有效0x14变化: {total_14_after - total_14_before}")
print(f"  其中空壳0x14: {total_14_shell_before} -> {total_14_shell_after} (变化{total_14_shell_after - total_14_shell_before})")

print("\n--- 成功编译的文件列表 ---")
for f in success:
    sz = os.path.getsize(f)
    c = count_0x14(f)
    print(f"  {os.path.relpath(f, ROOT)}  ({sz}B, 0x14={c})")

print("\n--- 无.qentl源文件 ---")
for f in no_qentl:
    print(f"  {os.path.relpath(f, ROOT)}")

print("\n--- 失败的文件列表 ---")
for f, err in failed:
    print(f"  {os.path.relpath(f, ROOT)}  [{err[:120]}]")

# 写结果到文件
with open(os.path.join(ROOT, ".recompile_result.txt"), "w") as out:
    out.write(f"编译前空壳数量: {len(shells)}\n")
    out.write(f"成功编译: {len(success)}\n")
    out.write(f"失败: {len(failed)}\n")
    out.write(f"无源文件: {len(no_qentl)}\n")
    out.write(f"编译后剩余空壳: {len(shells_after)}\n")
    out.write(f"有效0x14: {total_14_before} -> {total_14_after} (变化{total_14_after - total_14_before})\n")
    out.write("\n成功列表:\n")
    for f in success: out.write(f"  {os.path.relpath(f, ROOT)}\n")
    out.write("\n失败列表:\n")
    for f, err in failed: out.write(f"  {os.path.relpath(f, ROOT)} [{err[:100]}]\n")
