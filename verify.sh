#!/bin/bash
# QNT 系统验证脚本

set -e

cd "$(dirname "$0")"

echo "=== QNT 系统验证 ==="
echo ""

# 1. 基础模块验证
echo "1️⃣  基础模块验证..."
python3 -c "
from core.chain import QNTChain
from exchange.engine import MatchingEngine
from nstate.pool import SuperpositionPool
from agents.base import ArbAgent
print('✅ 核心模块导入成功')
"

# 2. 区块链验证
echo ""
echo "2️⃣  区块链验证..."
python3 -c "
from core.chain import QNTChain
chain = QNTChain(difficulty=2)
chain.state_ledger['Alice'] = 10000.0
chain.add_transaction('Alice', 'Bob', 500.0)
chain.mine_pending_transactions()
assert chain.is_valid()
print(f'✅ Blockchain: {chain.get_chain_info()[\"height\"]} blocks, valid=True')
"

# 3. 交易所验证
echo ""
echo "3️⃣  交易所验证..."
python3 -c "
from exchange.engine import MatchingEngine
eng = MatchingEngine('QNT/USDT', 0.001)
eng.set_balance('A', 'QNT', 500.0)
eng.set_balance('A', 'USDT', 10000.0)
eng.set_balance('B', 'QNT', 500.0)
eng.set_balance('B', 'USDT', 10000.0)
eng.submit_order('A', 'sell', 100, price=100.0)
eng.submit_order('B', 'buy', 80, price=100.0)
assert len(eng.trades) >= 1
print(f'✅ Exchange: {len(eng.trades)} trades executed')
"

# 4. N态训练验证
echo ""
echo "4️⃣  N态训练验证..."
python3 -c "
from nstate.pool import SuperpositionPool
import numpy as np
pool = SuperpositionPool(num_states=4, weight_dim=5)
for i in range(5):
    pool.train_step(np.random.randn(5), np.random.rand())
collapse = pool.collapse()
assert 'merged_weights' in collapse or 'status' in collapse
print(f'✅ N-State: {pool.training_rounds} rounds, collapse OK')
"

# 5. Agent验证
echo ""
echo "5️⃣  Agent验证..."
python3 -c "
from agents.base import ArbAgent
arb = ArbAgent(name='Test')
dec = arb.think({'spread_pct': 0.08})
assert dec['decision']['action'] == 'arbitrage'
print(f'✅ Agent: {dec[\"decision\"][\"action\"]} signal')
"

# 6. 单元测试
echo ""
echo "6️⃣  单元测试..."
python3 -m pytest tests/test_unit.py -q

# 7. 集成测试
echo ""
echo "7️⃣  集成测试..."
python3 -m pytest tests/test_integration.py -q

echo ""
echo "🎉 所有验证通过!"
