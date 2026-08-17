"""
QNT CLI工具
"""
import argparse
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.chain import QNTChain
from exchange.engine import MatchingEngine
from nstate.pool import SuperpositionPool
from agents.base import ArbAgent, MarketMakerAgent, TrendAgent
from agents.strategies import create_agent
from database.persistent import PersistentStore
from utils.logger import QNTLogger

log = QNTLogger()


def cmd_blockchain(args):
    """区块链命令"""
    chain = QNTChain(difficulty=args.difficulty)
    
    if args.action == 'status':
        print(json.dumps({
            'blocks': len(chain.chain),
            'difficulty': chain.difficulty,
            'latest_hash': chain.chain[-1].hash if chain.chain else None
        }, indent=2))
    
    elif args.action == 'mine':
        chain.state_ledger['Alice'] = 1000000.0
        chain.add_transaction('Alice', 'Bob', 100.0)
        chain.mine_pending_transactions()
        print(f"✅ Mined block #{chain.chain[-1].index}")
    
    elif args.action == 'tx':
        chain.state_ledger['Alice'] = 1000000.0
        tx = chain.add_transaction('Alice', 'Bob', args.amount)
        print(json.dumps({
            'tx_hash': tx.get('tx_hash'),
            'sender': 'Alice',
            'receiver': 'Bob',
            'amount': args.amount
        }, indent=2))


def cmd_exchange(args):
    """交易所命令"""
    eng = MatchingEngine(args.pair, fee_rate=0.001)
    
    # 设置余额
    for acc in args.accounts:
        eng.set_balance(acc, 'QNT', 10000.0)
        eng.set_balance(acc, 'USDT', 100000.0)
    
    if args.action == 'status':
        print(json.dumps({
            'pair': eng.pair,
            'trades': len(eng.trades),
            'bids': len(eng.orderbook.bids),
            'asks': len(eng.orderbook.asks)
        }, indent=2))
    
    elif args.action == 'order':
        result = eng.submit_order(args.account, args.side, args.quantity, price=args.price)
        print(json.dumps(result, indent=2, default=str))
    
    elif args.action == 'trades':
        print(json.dumps([t.__dict__ for t in eng.trades[-10:]], indent=2, default=str))


def cmd_nstate(args):
    """N态训练命令"""
    pool = SuperpositionPool(num_states=args.states, weight_dim=args.dim)
    
    if args.action == 'train':
        import numpy as np
        for i in range(args.rounds):
            pool.train_step(np.random.randn(args.dim), np.random.rand())
        print(f"✅ Trained {pool.training_rounds} rounds")
    
    elif args.action == 'collapse':
        # 先训练几轮
        import numpy as np
        for _ in range(20):
            pool.train_step(np.random.randn(args.dim), np.random.rand())
        
        result = pool.collapse()
        print(json.dumps(result, indent=2, default=str))
    
    elif args.action == 'status':
        print(json.dumps({
            'num_states': pool.num_states,
            'rounds': pool.training_rounds,
            'collapses': len(pool.collapses)
        }, indent=2))


def cmd_agents(args):
    """Agent命令"""
    if args.action == 'list':
        from agents.strategies import GridTradingAgent, MomentumAgent, MeanReversionAgent, VolumeProfileAgent
        agents = [
            ('ArbAgent', ArbAgent),
            ('MarketMakerAgent', MarketMakerAgent),
            ('TrendAgent', TrendAgent),
            ('GridTradingAgent', GridTradingAgent),
            ('MomentumAgent', MomentumAgent),
            ('MeanReversionAgent', MeanReversionAgent),
            ('VolumeProfileAgent', VolumeProfileAgent)
        ]
        for name, cls in agents:
            print(f"  - {name}")


def cmd_persist(args):
    """持久化命令"""
    store = PersistentStore(args.db)
    
    if args.action == 'status':
        info = store.get_chain_info()
        print(json.dumps(info, indent=2))
    
    elif args.action == 'history':
        history = store.get_history(limit=args.limit)
        print(json.dumps({
            'blocks': len(history['blocks']),
            'transactions': len(history['transactions']),
            'trades': len(history['trades'])
        }, indent=2))


def main():
    """CLI入口"""
    parser = argparse.ArgumentParser(
        prog='qnt',
        description='QNT Quantum Superposition Network CLI'
    )
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # blockchain
    bc_parser = subparsers.add_parser('blockchain', help='Blockchain operations')
    bc_parser.add_argument('--action', choices=['status', 'mine', 'tx'], required=True)
    bc_parser.add_argument('--difficulty', type=int, default=2)
    bc_parser.add_argument('--amount', type=float, default=100.0)
    
    # exchange
    ex_parser = subparsers.add_parser('exchange', help='Exchange operations')
    ex_parser.add_argument('--action', choices=['status', 'order', 'trades'], required=True)
    ex_parser.add_argument('--pair', default='QNT/USDT')
    ex_parser.add_argument('--accounts', nargs='+', default=['Alice', 'Bob'])
    ex_parser.add_argument('--account', default='Alice')
    ex_parser.add_argument('--side', choices=['buy', 'sell'])
    ex_parser.add_argument('--quantity', type=float, default=10.0)
    ex_parser.add_argument('--price', type=float, default=100.0)
    
    # nstate
    ns_parser = subparsers.add_parser('nstate', help='N-state training operations')
    ns_parser.add_argument('--action', choices=['train', 'collapse', 'status'], required=True)
    ns_parser.add_argument('--states', type=int, default=4)
    ns_parser.add_argument('--dim', type=int, default=10)
    ns_parser.add_argument('--rounds', type=int, default=100)
    
    # agents
    ag_parser = subparsers.add_parser('agents', help='Agent operations')
    ag_parser.add_argument('--action', choices=['list'], required=True)
    
    # persist
    ps_parser = subparsers.add_parser('persist', help='Persistence operations')
    ps_parser.add_argument('--action', choices=['status', 'history'], required=True)
    ps_parser.add_argument('--db', default='data/qnt.db')
    ps_parser.add_argument('--limit', type=int, default=10)
    
    args = parser.parse_args()
    
    if args.command == 'blockchain':
        cmd_blockchain(args)
    elif args.command == 'exchange':
        cmd_exchange(args)
    elif args.command == 'nstate':
        cmd_nstate(args)
    elif args.command == 'agents':
        cmd_agents(args)
    elif args.command == 'persist':
        cmd_persist(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
