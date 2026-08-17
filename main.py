"""
QNT 主入口 - 系统启动器
"""
import asyncio
import signal
import sys
import os
from typing import Optional

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.chain import QNTChain
from exchange.engine import MatchingEngine
from nstate.pool import SuperpositionPool
from agents.base import ArbAgent, MarketMakerAgent, TrendAgent
from agents.strategies import GridTradingAgent, MomentumAgent, MeanReversionAgent
from database.persistent import PersistentStore
from api.app import create_app
from market.feeds import FeedManager
from utils.logger import setup_logger


class QNTSystem:
    """QNT系统集成器"""
    
    def __init__(self):
        self.logger = setup_logger('QNT')
        
        # 核心组件
        self.chain: Optional[QNTChain] = None
        self.exchange: Optional[MatchingEngine] = None
        self.nstate_pool: Optional[SuperpositionPool] = None
        self.persistent: Optional[PersistentStore] = None
        self.feed: Optional[FeedManager] = None
        
        # Agents
        self.agents = {}
        
        # Flask应用
        self.app = None
        self.app_context = None
        
        # 运行状态
        self._running = False
    
    def initialize(self):
        """初始化所有组件"""
        self.logger.info("="*50)
        self.logger.info("QNT Quantum Superposition Network Starting...")
        self.logger.info("="*50)
        
        # 1. 初始化区块链
        self.chain = QNTChain(difficulty=2)
        self.logger.info(f"✅ Blockchain initialized: {len(self.chain.chain)} blocks")
        
        # 2. 初始化交易所
        self.exchange = MatchingEngine('QNT/USDT', fee_rate=0.001)
        self._setup_exchange_balances()
        self.logger.info("✅ Exchange initialized")
        
        # 3. 初始化N态池
        self.nstate_pool = SuperpositionPool(num_states=4, weight_dim=10)
        self.logger.info(f"✅ NState Pool initialized: {self.nstate_pool.num_states} states")
        
        # 4. 初始化持久化
        self.persistent = PersistentStore()
        self.logger.info("✅ Persistent Store initialized")
        
        # 5. 初始化行情流
        self.feed = FeedManager()
        self.logger.info("✅ Market Feed initialized")
        
        # 6. 创建Agents
        self._create_agents()
        self.logger.info(f"✅ Created {len(self.agents)} agents")
        
        # 7. 初始化API
        self.app = create_app(self)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.logger.info("✅ API initialized")
        
        self.logger.info("="*50)
        self.logger.info("QNT System Ready!")
        self.logger.info("="*50)
    
    def _setup_exchange_balances(self):
        """设置交易所初始余额"""
        accounts = ['Alice', 'Bob', 'Charlie', 'Diana']
        for acc in accounts:
            self.exchange.set_balance(acc, 'QNT', 10000.0)
            self.exchange.set_balance(acc, 'USDT', 100000.0)
    
    def _create_agents(self):
        """创建Agent实例"""
        self.agents = {
            'arb': ArbAgent(name='ArbBot'),
            'mm': MarketMakerAgent(name='MMBot'),
            'trend': TrendAgent(name='TrendBot'),
            'grid': GridTradingAgent(name='GridBot'),
            'momentum': MomentumAgent(name='MomentumBot'),
            'mean_rev': MeanReversionAgent(name='MeanRevBot')
        }
    
    async def start(self, host: str = '0.0.0.0', port: int = 5000, debug: bool = False):
        """启动系统"""
        self._running = True
        
        # 启动行情流
        feed_task = asyncio.create_task(self.feed.start(tick_interval=0.1))
        
        # 启动Agent循环
        agent_task = asyncio.create_task(self._agent_loop())
        
        # 启动API
        self.logger.info(f"🌐 Starting API server on http://{host}:{port}")
        
        import uvicorn
        config = uvicorn.Config(
            self.app,
            host=host,
            port=port,
            log_level='info' if not debug else 'debug'
        )
        server = uvicorn.Server(config)
        
        # 信号处理
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda: asyncio.create_task(self.stop()))
        
        await server.serve()
    
    async def _agent_loop(self):
        """Agent决策循环"""
        while self._running:
            try:
                # 获取市场数据
                market_data = self.feed.get_market_data()
                orderbook = self.feed.get_orderbook()
                
                # 准备观察数据
                observation = {
                    'price': market_data.price if market_data else 100.0,
                    'bid': orderbook.get('best_bid'),
                    'ask': orderbook.get('best_ask'),
                    'spread': orderbook.get('spread', 0),
                    'mid_price': orderbook.get('mid_price', 100.0)
                }
                
                # 每个Agent思考
                for name, agent in self.agents.items():
                    decision = agent.think(observation)
                    self.logger.debug(f"🤖 {name}: {decision['decision']}")
                    
                    # 执行决策
                    await self._execute_decision(agent, decision)
                
                await asyncio.sleep(1)
                
            except Exception as e:
                self.logger.error(f"⚠️ Agent loop error: {e}")
                await asyncio.sleep(1)
    
    async def _execute_decision(self, agent, decision: dict):
        """执行Agent决策"""
        action = decision.get('decision', {})
        
        if isinstance(action, dict):
            action_type = action.get('action', '')
            
            if action_type in ['buy', 'sell']:
                # 执行交易
                side = 'buy' if action_type == 'buy' else 'sell'
                quantity = action.get('quantity', 10.0)
                price = action.get('price', 100.0)
                
                self.exchange.submit_order(agent.name, side, quantity, price=price)
                self.logger.info(f"💼 {agent.name} executed {action_type} {quantity}@{price}")
            
            elif action_type == 'grid_orders':
                # 网格交易
                orders = action.get('orders', [])
                for order in orders[:3]:  # 限制每轮最多3单
                    self.exchange.submit_order(agent.name, order['side'], order['quantity'], price=order['price'])
    
    async def stop(self):
        """停止系统"""
        self.logger.info("🛑 Stopping QNT System...")
        self._running = False
        
        if self.app_context:
            self.app_context.pop()
        
        self.logger.info("✅ QNT System stopped")
    
    def get_status(self) -> dict:
        """获取系统状态"""
        return {
            'status': 'running' if self._running else 'stopped',
            'chain': {
                'blocks': len(self.chain.chain) if self.chain else 0,
                'difficulty': self.chain.config.difficulty if self.chain else 0
            },
            'exchange': {
                'pair': self.exchange.pair if self.exchange else None,
                'trades': len(self.exchange.trades) if self.exchange else 0,
                'bids': len(self.exchange.orderbook.bids) if self.exchange else 0,
                'asks': len(self.exchange.orderbook.asks) if self.exchange else 0
            },
            'nstate': {
                'num_states': self.nstate_pool.num_states if self.nstate_pool else 0,
                'rounds': self.nstate_pool.training_rounds if self.nstate_pool else 0,
                'collapses': len(self.nstate_pool.collapses) if self.nstate_pool else 0
            },
            'agents': {
                name: agent.status.value 
                for name, agent in self.agents.items()
            },
            'persistent': self.persistent.get_chain_info() if self.persistent else {}
        }


def main():
    """主入口"""
    system = QNTSystem()
    system.initialize()
    
    import argparse
    parser = argparse.ArgumentParser(description='QNT Quantum Superposition Network')
    parser.add_argument('--host', default='0.0.0.0', help='API host')
    parser.add_argument('--port', type=int, default=5000, help='API port')
    parser.add_argument('--debug', action='store_true', help='Debug mode')
    args = parser.parse_args()
    
    asyncio.run(system.start(host=args.host, port=args.port, debug=args.debug))


if __name__ == '__main__':
    main()
