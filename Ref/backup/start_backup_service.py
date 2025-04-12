"""
启动Ref备份服务
"""

import os
import sys
import time
import logging
from pathlib import Path

# 添加Ref目录到Python路径
ref_dir = Path(__file__).parent.parent
sys.path.append(str(ref_dir))

from Ref_core import RefCore

def main():
    """主函数"""
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('Ref/logs/backup_service.log'),
            logging.StreamHandler()
        ]
    )
    
    try:
        # 创建Ref实例
        ref = RefCore()
        
        # 启动监控服务
        ref.start_monitoring()
        logging.info("Ref备份服务已启动")
        
        # 保持服务运行
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logging.info("正在停止Ref备份服务...")
        ref.stop_monitoring()
        logging.info("Ref备份服务已停止")
    except Exception as e:
        logging.error(f"Ref备份服务出错: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 

"""

"""
量子基因编码: QE-STA-AF56B144A501
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
"""
"""

// 开发团队：中华 ZhoHo ，Claude 
