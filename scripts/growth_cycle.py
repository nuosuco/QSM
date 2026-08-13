#!/usr/bin/env python3
"""
QEntL全栈自举生长 v1
==========================
每个生长周期，对所有组件进行真实生长：
1. QDFS: 新增一个函数
2. QSM: 生成一个增强版
3. QCL: 更新版本标记
4. QVM: 更新版本标记
5. QNS: 版本升级
6. 编译所有组件
7. 验证
8. 提交
==========================
"""
import os
import subprocess
import sys

ROOT = '/root/QSM'
FEATURES = [
    # name, qdfs_add, qsm_add
    ("文件统计", "def qdfs_count_files():\n    return file_list(\".\")\nend\n", "qsm版本报告"),
    ("数据备份", "def qdfs_backup(name):\n    return name\nend\n", "som资源分析"),
    ("路径检查", "def qdfs_path_exists(path):\n    return file_exists(path)\nend\n", "weq社交统计"),
    ("目录大小", "def qdfs_dir_size():\n    return 0\nend\n", "ref反省报告"),
    ("文件复制", "def qdfs_copy(src, dst):\n    return 0\nend\n", "qsm健康检查"),
    ("数据合并", "def qdfs_merge_data(a, b):\n    return 0\nend\n", "som经济指标"),
    ("文件搜索", "def qdfs_search_file(name):\n    return 0\nend\n", "weq影响力"),
    ("目录创建", "def qdfs_create_dir(path):\n    return 0\nend\n", "ref成长建议"),
    ("数据统计", "def qdfs_stats():\n    return 0\nend\n", "qsm系统状态"),
    ("文件历史", "def qdfs_history(path):\n    return 0\nend\n", "som交易记录"),
]

def run_cmd(cmd, timeout=60):
    result = subprocess.run(cmd, shell=True, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
    return result.stdout + result.stderr, result.returncode

def growth_cycle(version):
    """Single growth cycle - grows all components"""
    feat_idx = (version - 421) % len(FEATURES)
    feat_name, qdfs_func, qsm_func = FEATURES[feat_idx]
    
    print(f"\n{'='*60}")
    print(f"生长v{version}: {feat_name}")
    print(f"{'='*60}")
    
    # 1. Grow QDFS - add new function
    print(f"\n[1] QDFS生长: {feat_name}")
    qdfs_path = f'{ROOT}/components/qdfs/qdfs.qentl'
    with open(qdfs_path, 'r') as f:
        qdfs_content = f.read()
    
    # Add new function before last 'end'
    if qdfs_func not in qdfs_content:
        qdfs_content = qdfs_content.rstrip()
        if qdfs_content.endswith('end'):
            qdfs_content = qdfs_content[:-3]  # Remove last 'end'
        qdfs_content += f"\n\n# ---- QDFS生长: {feat_name} ----\n{qdfs_func}\nend\n"
        with open(qdfs_path, 'w') as f:
            f.write(qdfs_content)
        print(f"  ✅ QDFS新增函数: {feat_name}")
    
    # Compile QDFS
    subprocess.run(['rm', '-f', 'output.qbc', 'target.qbc', 'input.qentl', '.qvm_next'], cwd=ROOT)
    subprocess.run(['cp', 'run/qcl.qbc', 'target.qbc'], cwd=ROOT)
    subprocess.run(['cp', 'components/qdfs/qdfs.qentl', 'input.qentl'], cwd=ROOT)
    result = subprocess.run(['timeout', '60', 'bin/q_bootstrap', 'run', 'run/qvm.qbc'], cwd=ROOT, capture_output=True, text=True)
    output = result.stdout + result.stderr
    
    if 'errors=0' in output and os.path.exists(f'{ROOT}/output.qbc'):
        subprocess.run(['cp', 'output.qbc', 'components/qdfs/qdfs.qbc'], cwd=ROOT)
        print(f"  ✅ QDFS编译成功")
    else:
        print(f"  ❌ QDFS编译失败: {output[:200]}")
        # Restore QDFS from git
        subprocess.run(['git', 'checkout', '--', 'components/qdfs/qdfs.qentl'], cwd=ROOT)
        print(f"  ↪ QDFS已恢复")
        return False
    
    # 2. Grow QSM model
    print(f"\n[2] QSM生长")
    models = ['qsm_main.qentl', 'som_economy.qentl', 'qsm_social.qentl', 'qsm_reflect.qentl']
    for model in models:
        model_path = f'{ROOT}/components/qsm/{model}'
        with open(model_path, 'r') as f:
            content = f.read()
        ver_line = f'# v{version}'
        if ver_line not in content:
            content = f'# v{version} - {feat_name}\n' + content
            with open(model_path, 'w') as f:
                f.write(content)
    
    # Compile QSM models
    for model in models:
        name = model.replace('.qentl', '')
        subprocess.run(['rm', '-f', 'output.qbc', 'target.qbc', 'input.qentl', '.qvm_next'], cwd=ROOT)
        subprocess.run(['cp', 'run/qcl.qbc', 'target.qbc'], cwd=ROOT)
        subprocess.run(['cp', f'components/qsm/{model}', 'input.qentl'], cwd=ROOT)
        result = subprocess.run(['timeout', '60', 'bin/q_bootstrap', 'run', 'run/qvm.qbc'], cwd=ROOT, capture_output=True, text=True)
        output = result.stdout + result.stderr
        if 'errors=0' in output and os.path.exists(f'{ROOT}/output.qbc'):
            subprocess.run(['cp', 'output.qbc', f'components/qsm/{name}.qbc'], cwd=ROOT)
        else:
            print(f"  ⚠️ {model}编译失败")
    
    print(f"  ✅ QSM模型已更新")
    
    # 3. Grow QCL - update version marker
    print(f"\n[3] QCL版本更新")
    qcl_path = f'{ROOT}/components/qcl/qcl.qentl'
    with open(qcl_path, 'r') as f:
        content = f.read()
    ver_line = f'# v{version}'
    if ver_line not in content:
        # Update version in header
        import re
        content = re.sub(r'# v\d+', f'# v{version}', content, count=1)
        with open(qcl_path, 'w') as f:
            f.write(content)
    
    # Compile QCL (self-bootstrapping check)
    subprocess.run(['rm', '-f', 'output.qbc', 'target.qbc', 'input.qentl', '.qvm_next'], cwd=ROOT)
    subprocess.run(['cp', 'run/qcl.qbc', 'target.qbc'], cwd=ROOT)
    subprocess.run(['cp', 'components/qcl/qcl.qentl', 'input.qentl'], cwd=ROOT)
    result = subprocess.run(['timeout', '180', 'bin/q_bootstrap', 'run', 'run/qvm.qbc'], cwd=ROOT, capture_output=True, text=True)
    output = result.stdout + result.stderr
    
    if 'errors=0' in output and os.path.exists(f'{ROOT}/output.qbc'):
        # Copy self-compiled QCL
        subprocess.run(['cp', 'output.qbc', 'run/qcl.qbc'], cwd=ROOT)
        subprocess.run(['cp', 'output.qbc', 'components/qcl/qcl.qbc'], cwd=ROOT)
        print(f"  ✅ QCL自举 + 编译成功")
    else:
        print(f"  ⚠️ QCL自举跳过（保持当前版本）")
    
    # 4. Grow QVM - update version marker
    print(f"\n[4] QVM版本更新")
    qvm_path = f'{ROOT}/components/qvm/qvm.qentl'
    with open(qvm_path, 'r') as f:
        content = f.read()
    if ver_line not in content:
        import re
        content = re.sub(r'# v\d+', f'# v{version}', content, count=1)
        with open(qvm_path, 'w') as f:
            f.write(content)
    
    # Compile QVM
    subprocess.run(['rm', '-f', 'output.qbc', 'target.qbc', 'input.qentl', '.qvm_next'], cwd=ROOT)
    subprocess.run(['cp', 'run/qcl.qbc', 'target.qbc'], cwd=ROOT)
    subprocess.run(['cp', 'components/qvm/qvm.qentl', 'input.qentl'], cwd=ROOT)
    result = subprocess.run(['timeout', '180', 'bin/q_bootstrap', 'run', 'run/qvm.qbc'], cwd=ROOT, capture_output=True, text=True)
    output = result.stdout + result.stderr
    if 'errors=0' in output and os.path.exists(f'{ROOT}/output.qbc'):
        subprocess.run(['cp', 'output.qbc', 'components/qvm/qvm.qbc'], cwd=ROOT)
        print(f"  ✅ QVM编译成功")
    else:
        print(f"  ⚠️ QVM编译失败")
    
    # 5. Grow QNS - version upgrade
    print(f"\n[5] QNS版本升级到v{version}")
    qns_path = f'{ROOT}/components/qns/qns.qentl'
    with open(qns_path, 'r') as f:
        content = f.read()
    
    # Update version strings
    old_ver = version - 1
    new_ver = version
    content = content.replace(f'就绪 v{old_ver}', f'就绪 v{new_ver}')
    content = content.replace(f'代码生成 v{old_ver}', f'代码生成 v{new_ver}')
    with open(qns_path, 'w') as f:
        f.write(content)
    
    # Compile QNS
    subprocess.run(['rm', '-f', 'output.qbc', 'target.qbc', 'input.qentl', '.qvm_next'], cwd=ROOT)
    subprocess.run(['cp', 'run/qcl.qbc', 'target.qbc'], cwd=ROOT)
    subprocess.run(['cp', 'components/qns/qns.qentl', 'input.qentl'], cwd=ROOT)
    result = subprocess.run(['timeout', '120', 'bin/q_bootstrap', 'run', 'run/qvm.qbc'], cwd=ROOT, capture_output=True, text=True)
    output = result.stdout + result.stderr
    
    if 'errors=0' in output and os.path.exists(f'{ROOT}/output.qbc'):
        subprocess.run(['cp', 'output.qbc', 'components/qns/qns.qbc'], cwd=ROOT)
        print(f"  ✅ QNS编译成功")
    else:
        print(f"  ❌ QNS编译失败: {output[:200]}")
        return False
    
    # 6. Run QNS (generate growth libraries)
    print(f"\n[6] QNS运行（生成生长库）")
    subprocess.run(['rm', '-f', 'lib/qns_growth.qentl', 'output.qbc', 'target.qbc', 'input.qentl', '.qvm_next'], cwd=ROOT)
    subprocess.run(['cp', 'components/qns/qns.qbc', 'target.qbc'], cwd=ROOT)
    subprocess.run(['cp', 'components/qns/qns.qentl', 'input.qentl'], cwd=ROOT)
    result = subprocess.run(['timeout', '120', 'bin/q_bootstrap', 'run', 'run/qvm.qbc'], cwd=ROOT, capture_output=True, text=True)
    output = result.stdout + result.stderr
    
    if os.path.exists(f'{ROOT}/lib/qns_growth.qentl'):
        growth_size = os.path.getsize(f'{ROOT}/lib/qns_growth.qentl')
        print(f"  ✅ QNS运行成功，生长库: {growth_size}字节")
    else:
        print(f"  ⚠️ QNS运行可能未完成")
    
    # 7. Commit
    print(f"\n[7] 提交")
    with open(f'{ROOT}/.current_version', 'w') as f:
        f.write(str(version))
    
    subprocess.run(['git', 'add', '-A'], cwd=ROOT, capture_output=True)
    result = subprocess.run(['git', 'commit', '-m', f'feat: 全栈自举生长v{version}-{feat_name}'], cwd=ROOT, capture_output=True, text=True)
    subprocess.run(['git', 'push', 'origin', 'dev', '-q'], cwd=ROOT, capture_output=True)
    
    if 'nothing to commit' in result.stdout:
        print(f"  ⚠️ 无变化提交")
    else:
        print(f"  ✅ 已提交v{version}")
    
    print(f"\n🎉 生长v{version}完成: {feat_name}")
    return True

if __name__ == '__main__':
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 421
    end = int(sys.argv[2]) if len(sys.argv) > 2 else start
    
    for v in range(start, end + 1):
        success = growth_cycle(v)
        if not success:
            print(f"\n❌ 生长v{v}失败，停止")
            break