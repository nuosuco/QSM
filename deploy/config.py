"""
QNT 部署配置和脚本
"""
import os
import json

# 项目配置
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
LOG_DIR = os.path.join(PROJECT_ROOT, 'logs')

# 系统配置
CONFIG = {
    'blockchain': {
        'difficulty': 2,
        'chain_name': 'QNT Chain'
    },
    'exchange': {
        'pair': 'QNT/USDT',
        'fee_rate': 0.001,
        'min_order_size': 1.0
    },
    'nstate': {
        'num_states': 4,
        'weight_dim': 10,
        'collapse_interval': 100
    },
    'api': {
        'host': '0.0.0.0',
        'port': 5000,
        'debug': False
    },
    'market': {
        'tick_interval': 0.1,
        'initial_price': 100.0,
        'volatility': 0.02
    }
}


def ensure_dirs():
    """确保目录存在"""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)
    os.makedirs(os.path.join(PROJECT_ROOT, 'backups'), exist_ok=True)


def get_config():
    """获取配置"""
    return CONFIG


def save_backup():
    """创建项目备份"""
    import shutil
    from datetime import datetime
    
    backup_dir = os.path.join(PROJECT_ROOT, 'backups')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f'QNT_v{CONFIG["blockchain"]["difficulty"]}_{timestamp}'
    
    # 备份数据
    data_backup = os.path.join(backup_dir, f'{backup_name}_data.tar.gz')
    if os.path.exists(DATA_DIR):
        shutil.make_archive(data_backup.replace('.tar.gz', ''), 'gztar', PROJECT_ROOT, 'data')
    
    return data_backup


if __name__ == '__main__':
    ensure_dirs()
    print(json.dumps(CONFIG, indent=2))
