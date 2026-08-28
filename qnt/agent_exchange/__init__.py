"""
QNT 多平台并行 Agent 交易系统
模拟"量子叠加态并行"：每个交易所 = 独立叠加态通道
"""
from .orchestrator import QNTOrchestrator
from .agents.spread_agent import SpreadArbitrageAgent
from .agents.risk_agent import RiskAgent
from .strategies.spread import SpreadStrategy

__version__ = "0.1.0"
__all__ = ["QNTOrchchestrator", "SpreadArbitrageAgent", "RiskAgent", "SpreadStrategy"]
