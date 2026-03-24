#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QSM系统健康监控脚本
"""

import os
import json
import subprocess
from datetime import datetime

def check_memory():
    """检查内存"""
    try:
        with open('/proc/meminfo', 'r') as f:
            lines = f.readlines()
            mem = {}
            for line in lines:
                parts = line.split()
                if len(parts) >= 2:
                    key = parts[0].rstrip(':')
                    val = int(parts[1])
                    mem[key] = val

            total = mem.get('MemTotal', 0) // 1024
            available = mem.get('MemAvailable', 0) // 1024
            used = total - available
            percent = (used / total * 100) if total > 0 else 0

            return {
                'total_mb': total,
                'available_mb': available,
                'used_mb': used,
                'percent_used': round(percent, 1)
            }
    except Exception as e:
        return {'error': str(e)}

def check_disk():
    """检查磁盘"""
    try:
        result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True)
        lines = result.stdout.strip().split('\n')
        if len(lines) >= 2:
            parts = lines[1].split()
            if len(parts) >= 5:
                return {
                    'total': parts[1],
                    'used': parts[2],
                    'available': parts[3],
                    'percent': parts[4]
                }
    except Exception as e:
        return {'error': str(e)}
    return {}

def check_nginx():
    """检查Nginx"""
    try:
        result = subprocess.run(['systemctl', 'is-active', 'nginx'], capture_output=True, text=True)
        return {
            'status': result.stdout.strip(),
            'running': result.stdout.strip() == 'active'
        }
    except Exception as e:
        return {'error': str(e)}

def check_qsm_models():
    """检查QSM模型"""
    model_dir = '/root/QSM/Models/QSM/bin'
    models = []
    try:
        if os.path.exists(model_dir):
            for f in os.listdir(model_dir):
                if f.endswith(('.pth', '.json')):
                    path = os.path.join(model_dir, f)
                    size = os.path.getsize(path)
                    models.append({
                        'name': f,
                        'size_mb': round(size / 1024 / 1024, 2)
                    })
    except Exception as e:
        return {'error': str(e)}
    return {'count': len(models), 'files': models[:10]}

def check_web_service():
    """检查Web服务"""
    try:
        result = subprocess.run(['curl', '-sI', 'https://som.top/'], capture_output=True, text=True)
        status = 'unknown'
        for line in result.stdout.split('\n'):
            if 'HTTP' in line:
                parts = line.split()
                if len(parts) >= 2:
                    status = parts[1]
                break
        return {
            'status': status,
            'healthy': status in ['200', '301', '302']
        }
    except Exception as e:
        return {'error': str(e)}

def generate_report():
    """生成健康报告"""
    report = {
        'timestamp': datetime.now().isoformat(),
        'uptime': subprocess.run(['uptime', '-p'], capture_output=True, text=True).stdout.strip(),
        'memory': check_memory(),
        'disk': check_disk(),
        'nginx': check_nginx(),
        'qsm_models': check_qsm_models(),
        'web': check_web_service()
    }
    return report

def main():
    print("=" * 60)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] QSM系统健康检查")
    print("=" * 60)

    report = generate_report()

    print(f"\n📊 内存状态:")
    mem = report['memory']
    if 'error' not in mem:
        print(f"  总计: {mem['total_mb']} MB")
        print(f"  可用: {mem['available_mb']} MB")
        print(f"  使用: {mem['percent_used']}%")
    else:
        print(f"  错误: {mem['error']}")

    print(f"\n💿 磁盘状态:")
    disk = report['disk']
    if 'error' not in disk:
        print(f"  总计: {disk['total']}")
        print(f"  使用: {disk['percent']}")
    else:
        print(f"  错误: {disk['error']}")

    print(f"\n🌐 Nginx状态:")
    nginx = report['nginx']
    if 'error' not in nginx:
        print(f"  状态: {nginx['status']}")
    else:
        print(f"  错误: {nginx['error']}")

    print(f"\n🤖 QSM模型:")
    models = report['qsm_models']
    if 'error' not in models:
        print(f"  模型数: {models['count']}")
    else:
        print(f"  错误: {models['error']}")

    print(f"\n🌍 Web服务:")
    web = report['web']
    if 'error' not in web:
        print(f"  状态: HTTP {web['status']}")
    else:
        print(f"  错误: {web['error']}")

    # 保存报告
    report_path = '/root/QSM/logs/health_report.json'
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"\n📄 报告已保存: {report_path}")

    print("\n" + "=" * 60)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 健康检查完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
