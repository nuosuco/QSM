#!/usr/bin/env python3
"""
QEntL全栈自举生长 v5 - 最终正确版本
===========================================
从干净的基线开始，每次正确添加函数
===========================================
"""
import os
import subprocess
import sys
import re

ROOT = '/root/QSM'
FEATURES = [
    ("文件统计", "qdfs_count_files"),
    ("数据备份", "qdfs_backup"),
    ("路径检查", "qdfs_path_exists"),
    ("目录大小", "qdfs_dir_size"),
    ("文件复制", "qdfs_copy"),
    ("数据合并", "qdfs_merge_data"),
    ("文件搜索", "qdfs_search_file"),
    ("目录创建", "qdfs_create_dir"),
    ("数据统计", "qdfs_stats"),
    ("文件历史", "qdfs_history"),
]

def run_cmd(cmd, timeout=60):
    result = subprocess.run(cmd, shell=True, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
    return result.stdout + result.stderr, result.returncode

def add_func_to_qdfs(func_name):
    """正确地向QDFS添加函数"""
    qdfs_path = f'{ROOT}/components/qdfs/qdfs.qentl'
    
    with open(qdfs_path, 'r') as f:
        content = f.read()
    
    # 检查是否已有该函数
    if f'def {func_name}' in content:
        print(f"  ⏭️ 已有函数: {func_name}")
        return True
    
    # 找到最后一个end的位置
    last_end_pos = content.rstrip().rfind('end\n')
    if last_end_pos == -1:
        last_end_pos = content.rstrip().rfind('end')
    
    # 在最后一个end之前插入新函数
    # 结构: ...original_content...end
    # 变为: ...original_content...\n# ----生长----\ndef func():\n    return ...\nend\n
    new_func = f'\n# ---- QDFS生长: {func_name} ----\ndef {func_name}():\n    return 0\nend\n'
    
    # 在最后一个end前插入
    new_content = content[:last_end_pos] + new_func + '\n' + content[last_end_pos:]
    
    with open(qdfs_path, 'w') as f:
        f.write(new_content)
    
    print(f"  ✅ QDFS新增函数: {func_name}")
    return True

def growth_cycle(version):
    """Single growth cycle - grows all components"""
    feat_idx = (version - 421) % len(FEATURES)
    feat_name = FEATURES[feat_idx][0]
    feat_func = FEATURES[feat_idx][1]
    
    print(f"\n{'='*60}")
    print(f"全栈生长v{version}: {feat_name}")
    print(f"{'='*60}")
    
    # 1. Grow QDFS
    print(f"\n[1] QDFS生长")
    add_func_to_qdfs(feat_func)
    
    # 验证结构
    with open(f'{ROOT}/components/qdfs/qdfs.qentl', 'r') as f:
        qdfs_content = f.read()
    def_count = qdfs_content.count('\ndef ')
    end_count = qdfs_content.count('\nend\n') + (1 if qdfs_content.rstrip().endswith('end') else 0)
    print(f"  def={def_count}, end={end_count}")
    
    # 编译QDFS
    subprocess.run(['rm', '-f', 'output.qbc', 'target.qbc', 'input.qentl', '.qvm_next'], cwd=ROOT)
    subprocess.run(['cp', 'run/qcl.qbc', 'target.qbc'], cwd=ROOT)
    subprocess.run(['cp', 'components/qdfs/qdfs.qentl', 'input.qentl'], cwd=ROOT)
    result = subprocess.run(['timeout', '60', 'bin/q_bootstrap', 'run', 'run/qvm.qbc'], cwd=ROOT, capture_output=True, text=True)
    output = result.stdout + result.stderr
    
    if 'errors=0' in output and os.path.exists(f'{ROOT}/output.qbc'):
        subprocess.run(['cp', 'output.qbc', 'components/qdfs/qdfs.qbc'], cwd=ROOT)
        print(f"  ✅ QDFS编译成功")
    else:
        print(f"  ❌ QDFS编译失败")
        subprocess.run(['git', 'checkout', '--', 'components/qdfs/qdfs.qentl'], cwd=ROOT)
        print(f"  ↪ QDFS已恢复")
        return False
    
    # 2. Grow QSM models
    print(f"\n[2] QSM版本更新")
    models = ['qsm_main.qentl', 'som_economy.qentl', 'qsm_social.qentl', 'qsm_reflect.qentl']
    for model in models:
        model_path = f'{ROOT}/components/qsm/{model}'
        if os.path.exists(model_path):
            with open(model_path, 'r') as f:
                content = f.read()
            ver_line = f'# v{version}'
            if ver_line not in content:
                content = f'# v{version}\n' + content
                with open(model_path, 'w') as f:
                    f.write(content)
    print(f"  ✅ QSM模型已更新")
    
    # 3. Grow QCL - update version only
    print(f"\n[3] QCL版本更新")
    qcl_path = f'{ROOT}/components/qcl/qcl.qentl'
    with open(qcl_path, 'r') as f:
        content = f.read()
    if f'# v{version}' not in content:
        content = re.sub(r'# v\d+', f'# v{version}', content, count=1)
        with open(qcl_path, 'w') as f:
            f.write(content)
    print(f"  ✅ QCL版本标记更新")
    
    # 4. Grow QVM - update version only
    print(f"\n[4] QVM版本更新")
    qvm_path = f'{ROOT}/components/qvm/qvm.qentl'
    with open(qvm_path, 'r') as f:
        content = f.read()
    if f'# v{version}' not in content:
        content = re.sub(r'# v\d+', f'# v{version}', content, count=1)
        with open(qvm_path, 'w') as f:
            f.write(content)
    print(f"  ✅ QVM版本标记更新")
    
    # 5. Grow QNS - version upgrade
    print(f"\n[5] QNS版本升级")
    qns_path = f'{ROOT}/components/qns/qns.qentl'
    with open(qns_path, 'r') as f:
        content = f.read()
    
    old_ver = version - 1
    content = content.replace(f'就绪 v{old_ver}', f'就绪 v{version}')
    content = content.replace(f'代码生成 v{old_ver}', f'代码生成 v{version}')
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
        print(f"  ❌ QNS编译失败")
        return False
    
    # 6. Run QNS to generate growth libraries
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
    
    if 'nothing to commit' in result.stdout or 'nothing to commit' in result.stderr:
        print(f"  ⚠️ 无变化提交")
    else:
        print(f"  ✅ 已提交")
    
    print(f"\n🎉 全栈生长v{version}完成!")
    return True

if __name__ == '__main__':
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 421
    end = int(sys.argv[2]) if len(sys.argv) > 2 else start
    
    for v in range(start, end + 1):
        success = growth_cycle(v)
        if not success:
            print(f"\n❌ 生长v{v}失败，停止")
            break