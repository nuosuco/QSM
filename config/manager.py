"""
QNT 配置管理
"""
import json
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class BlockchainConfig:
    """区块链配置"""
    difficulty: int = 2
    block_time: float = 10.0
    genesis_reward: float = 50.0
    max_transactions_per_block: int = 1000


@dataclass
class ExchangeConfig:
    """交易所配置"""
    fee_rate: float = 0.001
    min_order_size: float = 0.001
    max_order_size: float = 1_000_000.0
    price_tick: float = 0.01


@dataclass
class NStateConfig:
    """N态训练配置"""
    num_states: int = 4
    weight_dim: int = 5
    collapse_interval: int = 10
    learning_rate: float = 0.01


@dataclass
class AgentConfig:
    """Agent配置"""
    arb_spread_threshold: float = 0.05
    mm_spread: float = 0.02
    trend_lookback: int = 20


@dataclass
class AppConfig:
    """全局配置"""
    blockchain: BlockchainConfig = field(default_factory=BlockchainConfig)
    exchange: ExchangeConfig = field(default_factory=ExchangeConfig)
    nstate: NStateConfig = field(default_factory=NStateConfig)
    agent: AgentConfig = field(default_factory=AgentConfig)
    
    # 应用配置
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 5000
    
    # API配置
    api_prefix: str = "/api"
    rate_limit: int = 100


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or os.environ.get('QNT_CONFIG', 'config.json')
        self.config = AppConfig()
        self._load()
    
    def _load(self):
        """加载配置"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                data = json.load(f)
            self.config = self._parse_config(data)
    
    def _save(self):
        """保存配置"""
        with open(self.config_path, 'w') as f:
            json.dump(self._to_dict(), f, indent=2)
    
    def _parse_config(self, data: Dict[str, Any]) -> AppConfig:
        """解析配置"""
        config = AppConfig()
        
        if 'blockchain' in data:
            bc = data['blockchain']
            config.blockchain = BlockchainConfig(
                difficulty=bc.get('difficulty', 2),
                block_time=bc.get('block_time', 10.0),
                genesis_reward=bc.get('genesis_reward', 50.0)
            )
        
        if 'exchange' in data:
            ex = data['exchange']
            config.exchange = ExchangeConfig(
                fee_rate=ex.get('fee_rate', 0.001),
                min_order_size=ex.get('min_order_size', 0.001)
            )
        
        if 'nstate' in data:
            ns = data['nstate']
            config.nstate = NStateConfig(
                num_states=ns.get('num_states', 4),
                weight_dim=ns.get('weight_dim', 5),
                collapse_interval=ns.get('collapse_interval', 10)
            )
        
        if 'agent' in data:
            ag = data['agent']
            config.agent = AgentConfig(
                arb_spread_threshold=ag.get('arb_spread_threshold', 0.05),
                mm_spread=ag.get('mm_spread', 0.02)
            )
        
        config.debug = data.get('debug', False)
        config.host = data.get('host', '0.0.0.0')
        config.port = data.get('port', 5000)
        
        return config
    
    def _to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'blockchain': {
                'difficulty': self.config.blockchain.difficulty,
                'block_time': self.config.blockchain.block_time,
                'genesis_reward': self.config.blockchain.genesis_reward
            },
            'exchange': {
                'fee_rate': self.config.exchange.fee_rate,
                'min_order_size': self.config.exchange.min_order_size
            },
            'nstate': {
                'num_states': self.config.nstate.num_states,
                'weight_dim': self.config.nstate.weight_dim,
                'collapse_interval': self.config.nstate.collapse_interval
            },
            'agent': {
                'arb_spread_threshold': self.config.agent.arb_spread_threshold,
                'mm_spread': self.config.agent.mm_spread
            },
            'debug': self.config.debug,
            'host': self.config.host,
            'port': self.config.port
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if hasattr(value, k):
                value = getattr(value, k)
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """设置配置值"""
        keys = key.split('.')
        obj = self.config
        
        for k in keys[:-1]:
            obj = getattr(obj, k)
        
        setattr(obj, keys[-1], value)
        self._save()
    
    def save(self):
        """手动保存配置"""
        self._save()


# 全局配置实例
config_manager = ConfigManager()
config = config_manager
