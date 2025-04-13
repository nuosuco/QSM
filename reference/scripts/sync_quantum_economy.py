#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
import sys
import logging
from pathlib import Path
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("quantum_economy_sync.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# 定义模型列表
MODELS = ["QSM", "WeQ", "SOM", "Ref"]

def create_quantum_wallet(model_name):
    """
    创建量子钱包目录结构
    
    Args:
        model_name: 模型名称
    """
    wallet_dir = f"{model_name}/quantum_economy/wallet"
    os.makedirs(wallet_dir, exist_ok=True)
    
    # 创建钱包相关文件
    files_to_create = {
        "__init__.py": f"# {model_name} Quantum Wallet Module\n",
        "wallet.py": f"""# {model_name} Quantum Wallet Core
from typing import Dict, List
import hashlib
import json

class QuantumWallet:
    def __init__(self):
        self.balance = 0
        self.transactions = []
        self.quantum_state = {{}}
    
    def add_funds(self, amount: float):
        self.balance += amount
        self._update_quantum_state()
    
    def spend_funds(self, amount: float) -> bool:
        if self.balance >= amount:
            self.balance -= amount
            self._update_quantum_state()
            return True
        return False
    
    def _update_quantum_state(self):
        # 更新量子态
        state_hash = hashlib.sha256(str(self.balance).encode()).hexdigest()
        self.quantum_state = {{"balance_hash": state_hash}}
""",
        "transaction.py": f"""# {model_name} Transaction Module
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any

@dataclass
class Transaction:
    sender: str
    receiver: str
    amount: float
    timestamp: datetime
    metadata: Dict[str, Any]
    
    def to_dict(self) -> dict:
        return {{
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": self.amount,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }}
"""
    }
    
    for filename, content in files_to_create.items():
        file_path = os.path.join(wallet_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"已创建钱包文件: {file_path}")

def create_som_coin(model_name):
    """
    创建松麦币系统
    
    Args:
        model_name: 模型名称
    """
    coin_dir = f"{model_name}/quantum_economy/coin"
    os.makedirs(coin_dir, exist_ok=True)
    
    # 创建松麦币相关文件
    files_to_create = {
        "__init__.py": f"# {model_name} SOM Coin Module\n",
        "som_coin.py": f"""# {model_name} SOM Coin Core
from typing import Dict, List
import hashlib
import json
from datetime import datetime

class SOMCoin:
    def __init__(self):
        self.total_supply = 0
        self.block_reward = 1.0
        self.transactions = []
    
    def mine_block(self, miner_address: str) -> float:
        # 挖矿奖励
        reward = self.block_reward
        self.total_supply += reward
        self._record_transaction("system", miner_address, reward)
        return reward
    
    def _record_transaction(self, sender: str, receiver: str, amount: float):
        transaction = {{
            "sender": sender,
            "receiver": receiver,
            "amount": amount,
            "timestamp": datetime.now().isoformat()
        }}
        self.transactions.append(transaction)
""",
        "blockchain.py": f"""# {model_name} Blockchain Module
from typing import Dict, List
import hashlib
import json
from datetime import datetime

class Blockchain:
    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        self.difficulty = 4
    
    def add_block(self, transactions: List[Dict]):
        block = {{
            "index": len(self.chain),
            "timestamp": datetime.now().isoformat(),
            "transactions": transactions,
            "previous_hash": self.chain[-1]["hash"] if self.chain else "0" * 64
        }}
        
        block["hash"] = self._calculate_hash(block)
        self.chain.append(block)
        return block
    
    def _calculate_hash(self, block: Dict) -> str:
        block_string = json.dumps(block, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
"""
    }
    
    for filename, content in files_to_create.items():
        file_path = os.path.join(coin_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"已创建松麦币文件: {file_path}")

def copy_directory(src, dst, model_name):
    """
    复制目录，并将som目录改为相应的模型名
    
    Args:
        src: 源目录
        dst: 目标目录
        model_name: 模型名称
    """
    if not os.path.exists(src):
        logger.error(f"源目录不存在: {src}")
        return False
    
    # 确保目标目录存在
    os.makedirs(dst, exist_ok=True)
    
    # 复制quantum_economy目录
    quantum_economy_src = os.path.join(src, "quantum_economy")
    quantum_economy_dst = os.path.join(dst, "quantum_economy")
    
    if os.path.exists(quantum_economy_dst):
        logger.info(f"目标目录已存在，将被覆盖: {quantum_economy_dst}")
        shutil.rmtree(quantum_economy_dst)
    
    # 复制整个quantum_economy目录
    shutil.copytree(quantum_economy_src, quantum_economy_dst)
    logger.info(f"已复制quantum_economy目录到: {quantum_economy_dst}")
    
    # 创建量子钱包和松麦币系统
    create_quantum_wallet(model_name)
    create_som_coin(model_name)
    
    # 重命名som目录
    som_src = os.path.join(quantum_economy_dst, "som")
    model_dir = os.path.join(quantum_economy_dst, model_name.lower())
    
    # 特殊处理SOM模型
    if model_name == "SOM":
        # 如果som目录不存在，创建它
        if not os.path.exists(som_src):
            logger.info(f"SOM模型特殊处理: 创建som目录")
            os.makedirs(som_src)
            
            # 从源quantum_economy/som目录复制内容
            src_som_dir = os.path.join(src, "quantum_economy", "som")
            if os.path.exists(src_som_dir):
                for item in os.listdir(src_som_dir):
                    s = os.path.join(src_som_dir, item)
                    d = os.path.join(som_src, item)
                    if os.path.isdir(s):
                        shutil.copytree(s, d)
                    else:
                        shutil.copy2(s, d)
                logger.info(f"已从源目录复制som内容")
            else:
                logger.warning(f"源som目录不存在: {src_som_dir}")
                # 创建基本目录结构
                for dir_name in ["blockchain", "coin", "marketplace", "traceability", "user", "wallet"]:
                    os.makedirs(os.path.join(som_src, dir_name))
                logger.info(f"已创建基本目录结构")
                
                # 创建基本文件
                files_to_create = {
                    "__init__.py": "# SOM Economy Module\n",
                    "som_economy.py": "# SOM Economy Core\n",
                    "som_ecommerce.py": "# SOM E-commerce System\n"
                }
                for filename, content in files_to_create.items():
                    with open(os.path.join(som_src, filename), 'w', encoding='utf-8') as f:
                        f.write(content)
                logger.info(f"已创建基本文件")
    
    if os.path.exists(som_src):
        if os.path.exists(model_dir) and model_dir != som_src:
            logger.info(f"目标模型目录已存在，将被覆盖: {model_dir}")
            shutil.rmtree(model_dir)
        
        # 重命名som目录为模型名（对于SOM模型，保持som名称）
        if model_name.lower() != "som":
            try:
                os.rename(som_src, model_dir)
                logger.info(f"已将som目录重命名为: {model_dir}")
            except FileNotFoundError:
                logger.warning(f"源目录不存在，可能是已经被重命名: {som_src}")
                # 检查是否已经存在模型目录
                if not os.path.exists(model_dir):
                    logger.error(f"模型目录不存在: {model_dir}")
                    return False
            except Exception as e:
                logger.error(f"重命名目录时出错: {e}")
                return False
        
        # 更新文件中的引用
        target_dir = model_dir if model_name.lower() != "som" else som_src
        update_files_in_directory(target_dir, model_name)
    
    return True

def update_files_in_directory(directory, model_name):
    """
    更新目录中所有Python文件中的引用
    
    Args:
        directory: 目录路径
        model_name: 模型名称
    """
    # 如果是SOM模型，不需要替换引用
    if model_name.lower() == "som":
        return
    
    # 更新__init__.py文件中的引用
    init_file = os.path.join(directory, "__init__.py")
    if os.path.exists(init_file):
        with open(init_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替换som为模型名
        updated_content = content.replace("som", model_name.lower())
        
        with open(init_file, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        logger.info(f"已更新{init_file}中的引用")
    
    # 更新其他文件中的引用
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 替换som为模型名
                updated_content = content.replace("som", model_name.lower())
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                
                logger.info(f"已更新{file_path}中的引用")

def main():
    """主函数"""
    # 获取当前工作目录
    current_dir = os.getcwd()
    logger.info(f"当前工作目录: {current_dir}")
    
    # 检查quantum_economy目录是否存在
    quantum_economy_dir = os.path.join(current_dir, "quantum_economy")
    if not os.path.exists(quantum_economy_dir):
        logger.error(f"quantum_economy目录不存在: {quantum_economy_dir}")
        return
    
    # 备份原始quantum_economy目录
    backup_dir = os.path.join(current_dir, "quantum_economy_backup_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
    logger.info(f"备份quantum_economy目录到: {backup_dir}")
    shutil.copytree(quantum_economy_dir, backup_dir)
    
    # 验证SOM中是否有更新的内容需要合并到根目录
    som_quantum_dir = os.path.join(current_dir, "SOM", "quantum_economy")
    if os.path.exists(som_quantum_dir):
        logger.info("检查SOM模型中是否有更新的内容...")
        
        # 检查特定目录
        for dir_name in ["coin", "wallet", "blockchain"]:
            som_dir = os.path.join(som_quantum_dir, dir_name)
            root_dir = os.path.join(quantum_economy_dir, "som", dir_name)
            
            if os.path.exists(som_dir) and os.path.exists(root_dir):
                # 如果SOM中文件更新，复制到根目录
                for item in os.listdir(som_dir):
                    s = os.path.join(som_dir, item)
                    d = os.path.join(root_dir, item)
                    
                    if os.path.isfile(s):
                        som_time = os.path.getmtime(s)
                        if not os.path.exists(d) or som_time > os.path.getmtime(d):
                            logger.info(f"更新文件: {d}")
                            shutil.copy2(s, d)
    
    # 同步到各个模型
    for model in MODELS:
        model_dir = os.path.join(current_dir, model)
        if not os.path.exists(model_dir):
            logger.warning(f"模型目录不存在: {model_dir}")
            continue
        
        logger.info(f"开始同步quantum_economy到模型: {model}")
        success = copy_directory(current_dir, model_dir, model)
        
        if success:
            logger.info(f"成功同步quantum_economy到模型: {model}")
        else:
            logger.error(f"同步quantum_economy到模型失败: {model}")
    
    logger.info("同步完成")

if __name__ == "__main__":
    main() 

"""
"""
量子基因编码: QE-SYN-B1FC756677F8
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
""""""

// 开发团队：中华 ZhoHo ，Claude 
