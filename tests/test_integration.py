"""
QNT 集成测试 - 全流程验证
"""
import numpy as np
from core.chain import QNTChain
from core.contract import QNTToken, QNTGovernance, NStateContract
from exchange.engine import MatchingEngine
from nstate.pool import SuperpositionPool
from agents.base import ArbAgent, MarketMakerAgent, TrendAgent
from strategies.arbitrage import SpreadArbitrageStrategy, MarketMakingStrategy


def test_blockchain():
    print("\n=== 1. Blockchain Test ===")
    chain = QNTChain(difficulty=2)
    chain.state_ledger['Alice'] = 10000.0
    chain.state_ledger['Bob'] = 5000.0
    chain.add_transaction('Alice', 'Bob', 500.0)
    chain.mine_pending_transactions()
    assert chain.is_valid()
    assert chain.get_balance('Alice') == 9500.0
    print(f"✅ Blockchain OK - height={chain.get_chain_info()['height']}")
    return True


def test_token():
    print("\n=== 2. Token Contract Test ===")
    token = QNTToken(total_supply=1_000_000.0)
    assert token.balance_of('system') == 1_000_000.0
    result = token.call('system', 'transfer', 'Alice', 1000.0)
    assert result['success']
    assert token.balance_of('Alice') == 1000.0
    print(f"✅ Token OK - Alice={token.balance_of('Alice'):.0f}")
    return True


def test_exchange():
    print("\n=== 3. Exchange Test ===")
    eng = MatchingEngine('QNT/USDT', 0.001)
    eng.set_balance('A', 'QNT', 500.0); eng.set_balance('A', 'USDT', 10000.0)
    eng.set_balance('B', 'QNT', 500.0); eng.set_balance('B', 'USDT', 10000.0)
    eng.submit_order('A', 'sell', 100, price=100.0)
    eng.submit_order('B', 'buy', 80, price=100.0)
    assert len(eng.trades) >= 1
    assert eng.trades[0].quantity == 80.0
    print(f"✅ Exchange OK - {len(eng.trades)} trades")
    return True


def test_nstate():
    print("\n=== 4. N-State Test ===")
    pool = SuperpositionPool(num_states=4, weight_dim=5)
    for i in range(10):
        pool.train_step(np.random.randn(5), np.random.rand())
    collapse = pool.collapse()
    assert 'merged_weights' in collapse
    assert pool.num_states == 4
    print(f"✅ N-State OK - {pool.training_rounds} rounds")
    return True


def test_agents():
    print("\n=== 5. Agent Test ===")
    arb = ArbAgent(name='ArbBot')
    dec = arb.think({'spread_pct': 0.08})
    assert dec['decision']['action'] == 'arbitrage'
    trend = TrendAgent(name='TrendBot', lookback=3)
    for p in [10, 11, 12, 13, 14, 15]:
        trend.think({'price': float(p)})
    dec = trend.think({'price': 15.0})
    assert dec['decision']['action'] in ['buy', 'sell', 'hold']
    print(f"✅ Agents OK - Arb={dec['decision']['action']}")
    return True


def test_governance():
    print("\n=== 6. Governance Test ===")
    gov = QNTGovernance()
    pid = gov.call('Alice', 'propose', 'Upgrade', ['core']).get('result', 0)
    gov.vote('Alice', pid, True, weight=100.0)
    gov.vote('Bob', pid, False, weight=30.0)
    proposal = gov.state['proposals'][0]
    assert proposal['votes_for'] == 100.0
    assert proposal['votes_against'] == 30.0
    print(f"✅ Governance OK - Proposal {pid}: for=100, against=30")
    return True


def test_nstate_contract():
    print("\n=== 7. N-State Contract Test ===")
    ns = NStateContract(num_states=4)
    ns.add_state(0, [0.1, 0.2, 0.3])
    ns.add_state(1, [0.4, 0.5, 0.6])
    result = ns.collapse()
    assert 'merged_weights' in result
    assert len(ns.state['states']) == 0
    print(f"✅ N-State Contract OK - Merged 2 states")
    return True


def run_all_tests():
    print("=" * 50)
    print("🧪 QNT Integration Tests")
    print("=" * 50)
    results = []
    for test in [test_blockchain, test_token, test_exchange, test_nstate, test_agents, test_governance, test_nstate_contract]:
        try:
            results.append(test())
        except Exception as e:
            print(f"❌ {test.__name__} FAILED: {e}")
            results.append(False)
    passed = sum(results)
    total = len(results)
    print(f"\n📊 Results: {passed}/{total} passed")
    if passed == total:
        print("🎉 All tests passed!")
    return all(results)


if __name__ == '__main__':
    run_all_tests()
