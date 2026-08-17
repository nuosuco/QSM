"""
QNT 配置
"""
import os
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class BlockchainConfig:
    """区块链配置"""
    difficulty: int = 4  # 挖矿难度
    block_time_target: float = 60.0  # 目标出块时间（秒）
    max_transactions_per_block: int = 100
    genesis_supply: float = 1_000_000.0  # 创世代币总量


@dataclass
class ExchangeConfig:
    """交易所配置"""
    min_order_amount: float = 0.01  # 最小订单金额
    max_order_amount: float = 1_000_000.0  # 最大订单金额
    trading_fee_rate: float = 0.001  # 交易手续费率 0.1%
    maker_fee_rate: float = 0.0005  # 挂单方手续费 0.05%
    taker_fee_rate: float = 0.001  # 吃单方手续费 0.1%


@dataclass
class NStateConfig:
    """N态并行训练配置"""
    num_states: int = 8  # 叠加态数量
    training_epochs: int = 100
    collapse_interval: int = 10  # 每10轮坍缩一次
    learning_rate: float = 0.001
    state_diversity: float = 0.3  # 态多样性因子


@dataclass
class AgentConfig:
    """Agent配置"""
    max_agents: int = 10
    agent_update_interval: int = 60  # 秒
    memory_capacity: int = 1000


@dataclass  
class QNTConfig:
    """QNT全局配置"""
    blockchain: BlockchainConfig = None
    exchange: ExchangeConfig = None
    nstate: NStateConfig = None
    agents: AgentConfig = None
    
    def __post_init__(self):
        if self.blockchain is None:
            self.blockchain = BlockchainConfig()
        if self.exchange is None:
            self.exchange = ExchangeConfig()
        if self.nstate is None:
            self.nstate = NStateConfig()
        if self.agents is None:
            self.agents = AgentConfig()


# 全局配置实例
config = QNTConfig()

# 从环境变量读取配置
def load_config_from_env():
    """从环境变量加载配置"""
    config.blockchain.difficulty = int(os.getenv("QNT_DIFFICULTY", "4"))
    config.nstate.num_states = int(os.getenv("QNT_NUM_STATES", "8"))
    config.exchange.trading_fee_rate = float(os.getenv("QNT_FEE_RATE", "0.001"))
    print(f"📋 Config loaded from environment")


# 导出
__all__ = ["config", "QNTConfig", "BlockchainConfig", "ExchangeConfig", 
           "NStateConfig", "AgentConfig", "load_config_from_env"]
