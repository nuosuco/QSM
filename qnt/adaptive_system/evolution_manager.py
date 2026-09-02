"""
自适应进化交易系统 - 双模式回测进化版
负责分析交易记录，发现有效/无效规律，自动调整策略参数
"""
import sqlite3
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger('EvolutionManager')

# 进化分析的最小样本要求
MIN_SAMPLES_FOR_ANALYSIS = 50
MIN_SAMPLES_FOR_VALIDATION = 100


class EvolutionManager:
    """双模式回测策略自进化管理器"""

    def __init__(self, db_path: str, config=None):
        self.db_path = db_path
        self.config = config
        self.evolution_count = 0

    def analyze_and_evolve(self) -> Dict:
        """执行一次完整进化分析（双模式对比）"""
        logger.info("=" * 60)
        logger.info("🧬 开始双模式进化分析...")
        logger.info("=" * 60)

        report = {
            'timestamp': datetime.now().isoformat(),
            'analysis': {},
            'actions': [],
            'parameter_changes': [],
            'comparison': {},
        }

        # 1. 分析模式一：我们的真实成交历史
        hist_stats = self._analyze_historical_trades()
        report['analysis']['historical'] = hist_stats

        # 2. 分析模式二：市场成交回测
        market_stats = self._analyze_market_backtest()
        report['analysis']['market_backtest'] = market_stats

        # 3. 双模式对比
        comparison = self._compare_modes(hist_stats, market_stats)
        report['comparison'] = comparison

        # 4. 分析模拟盘表现
        paper_stats = self._analyze_paper()
        report['analysis']['paper'] = paper_stats

        # 5. 根据对比结果生成进化动作
        if comparison['consistent']:
            actions = self._generate_consistent_actions(comparison, paper_stats)
        else:
            actions = self._generate_divergent_actions(comparison)
        report['actions'] = actions

        # 6. 应用变更
        for action in report['actions']:
            if action['type'] == 'parameter_change':
                self._apply_parameter_change(action)
                report['parameter_changes'].append(action)

        self.evolution_count += 1
        logger.info(f"✅ 第{self.evolution_count}次进化完成，共{len(report['actions'])}项调整")

        # 保存报告
        self._save_report(report)

        return report

    def _analyze_historical_trades(self) -> Dict:
        """分析我们的真实成交历史（模式一）"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            cursor = conn.cursor()

            # 统计总览
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN side='buy' THEN cost ELSE 0 END) as buy_cost,
                    SUM(CASE WHEN side='sell' THEN cost ELSE 0 END) as sell_cost,
                    MIN(datetime(timestamp, 'unixepoch', '+8 hours')) as first_trade,
                    MAX(datetime(timestamp, 'unixepoch', '+8 hours')) as last_trade
                FROM historical_trades
            """)
            row = cursor.fetchone()
            
            if not row or row[0] == 0:
                conn.close()
                return {'trades': 0, 'net_pnl': 0, 'win_rate': 0}
            
            total_trades = row[0]
            buy_cost = row[1] or 0
            sell_cost = row[2] or 0
            net_pnl = sell_cost - buy_cost
            
            # 按币种统计
            cursor.execute("""
                SELECT symbol, COUNT(*) as cnt,
                       SUM(CASE WHEN side='buy' THEN cost ELSE 0 END) as buy,
                       SUM(CASE WHEN side='sell' THEN cost ELSE 0 END) as sell
                FROM historical_trades
                GROUP BY symbol
                ORDER BY cnt DESC
            """)
            symbol_stats = [{'symbol': s[0], 'trades': s[1], 'pnl': s[3]-s[2]} for s in cursor.fetchall()]
            
            # 按平台统计
            cursor.execute("""
                SELECT exchange, COUNT(*) as cnt,
                       SUM(CASE WHEN side='buy' THEN cost ELSE 0 END) as buy,
                       SUM(CASE WHEN side='sell' THEN cost ELSE 0 END) as sell
                FROM historical_trades
                GROUP BY exchange
                ORDER BY cnt DESC
            """)
            exchange_stats = [{'exchange': s[0], 'trades': s[1], 'pnl': s[3]-s[2]} for s in cursor.fetchall()]
            
            conn.close()
            
            return {
                'trades': total_trades,
                'buy_cost': buy_cost,
                'sell_cost': sell_cost,
                'net_pnl': net_pnl,
                'net_pnl_pct': net_pnl / buy_cost * 100 if buy_cost > 0 else 0,
                'symbol_stats': symbol_stats[:10],
                'exchange_stats': exchange_stats,
                'first_trade': row[3],
                'last_trade': row[4],
            }
        except Exception as e:
            logger.error(f"分析历史成交失败: {e}")
            return {'error': str(e), 'trades': 0}

    def _analyze_market_backtest(self) -> Dict:
        """分析市场成交回测（模式二）"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            cursor = conn.cursor()

            # 统计总览
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN side='buy' THEN cost ELSE 0 END) as buy_cost,
                    SUM(CASE WHEN side='sell' THEN cost ELSE 0 END) as sell_cost,
                    MIN(datetime(timestamp, 'unixepoch', '+8 hours')) as first_trade,
                    MAX(datetime(timestamp, 'unixepoch', '+8 hours')) as last_trade
                FROM market_trades
            """)
            row = cursor.fetchone()
            
            if not row or row[0] == 0:
                conn.close()
                return {'trades': 0, 'net_pnl': 0}
            
            total_trades = row[0]
            buy_cost = row[1] or 0
            sell_cost = row[2] or 0
            
            # 按币种统计
            cursor.execute("""
                SELECT symbol, COUNT(*) as cnt,
                       SUM(CASE WHEN side='buy' THEN cost ELSE 0 END) as buy,
                       SUM(CASE WHEN side='sell' THEN cost ELSE 0 END) as sell
                FROM market_trades
                GROUP BY symbol
                ORDER BY cnt DESC
                LIMIT 20
            """)
            symbol_stats = [{'symbol': s[0], 'trades': s[1], 'buy': s[2], 'sell': s[3], 'pnl': s[3]-s[2]} for s in cursor.fetchall()]
            
            # 按平台统计
            cursor.execute("""
                SELECT exchange, COUNT(*) as cnt,
                       SUM(CASE WHEN side='buy' THEN cost ELSE 0 END) as buy,
                       SUM(CASE WHEN side='sell' THEN cost ELSE 0 END) as sell
                FROM market_trades
                GROUP BY exchange
                ORDER BY cnt DESC
            """)
            exchange_stats = [{'exchange': s[0], 'trades': s[1], 'buy': s[2], 'sell': s[3], 'pnl': s[3]-s[2]} for s in cursor.fetchall()]
            
            conn.close()
            
            return {
                'trades': total_trades,
                'buy_cost': buy_cost,
                'sell_cost': sell_cost,
                'net_pnl': sell_cost - buy_cost,
                'net_pnl_pct': (sell_cost - buy_cost) / buy_cost * 100 if buy_cost > 0 else 0,
                'symbol_stats': symbol_stats,
                'exchange_stats': exchange_stats,
                'first_trade': row[3],
                'last_trade': row[4],
            }
        except Exception as e:
            logger.error(f"分析市场回测失败: {e}")
            return {'error': str(e), 'trades': 0}

    def _compare_modes(self, hist_stats: Dict, market_stats: Dict) -> Dict:
        """双模式对比分析"""
        # 检查数据量是否足够对比
        if hist_stats.get('trades', 0) < 10 or market_stats.get('trades', 0) < 100:
            return {
                'consistent': False,
                'reason': '样本不足，无法对比',
                'hist_trades': hist_stats.get('trades', 0),
                'market_trades': market_stats.get('trades', 0),
            }
        
        # 分析趋势一致性
        hist_direction = 'up' if hist_stats.get('net_pnl', 0) > 0 else 'down'
        market_direction = 'up' if market_stats.get('net_pnl', 0) > 0 else 'down'
        
        consistent = hist_direction == market_direction
        
        # 找出共同盈利/亏损币种
        hist_symbols = {s['symbol']: s['pnl'] for s in hist_stats.get('symbol_stats', [])}
        market_symbols = {s['symbol']: s['pnl'] for s in market_stats.get('symbol_stats', [])}
        
        common_profits = [s for s in hist_symbols if s in market_symbols and hist_symbols[s] > 0 and market_symbols[s] > 0]
        common_losses = [s for s in hist_symbols if s in market_symbols and hist_symbols[s] < 0 and market_symbols[s] < 0]
        
        return {
            'consistent': consistent,
            'hist_direction': hist_direction,
            'market_direction': market_direction,
            'hist_net_pnl': hist_stats.get('net_pnl', 0),
            'market_net_pnl': market_stats.get('net_pnl', 0),
            'common_profit_symbols': common_profits,
            'common_loss_symbols': common_losses,
            'hist_trades': hist_stats.get('trades', 0),
            'market_trades': market_stats.get('trades', 0),
        }

    def _generate_consistent_actions(self, comparison: Dict, paper_stats: Dict) -> List[Dict]:
        """一致性时的进化动作"""
        actions = []
        
        # 双模式都盈利 → 提升信心，可适当放宽门槛
        if comparison['hist_net_pnl'] > 0 and comparison['market_net_pnl'] > 0:
            actions.append({
                'type': 'confidence_boost',
                'message': '双模式均盈利，策略有效，可适当放宽门槛增加交易机会',
                'suggestion': 'spread_pct可从0.17%降至0.15%',
            })
            
            # 如果有模拟盘数据，尝试应用于模拟盘
            if paper_stats.get('trades', 0) > 0:
                actions.append({
                    'type': 'apply_to_paper',
                    'action': '使用当前策略继续模拟盘验证',
                    'expected': '模拟盘盈利后开启实盘',
                })
        
        # 双模式都亏损 → 收紧风控
        elif comparison['hist_net_pnl'] < 0 and comparison['market_net_pnl'] < 0:
            actions.append({
                'type': 'risk_reduction',
                'message': '双模式均亏损，策略需要优化',
                'suggestion': '提高spread_pct至0.20%，收紧风控',
            })
        
        # 共同盈利币种 → 提升优先级
        for symbol in comparison.get('common_profit_symbols', []):
            actions.append({
                'type': 'priority_adjust',
                'symbol': symbol,
                'new_priority': 1,
                'reason': f'{symbol}在双模式中均盈利，提升优先级',
            })
        
        # 共同亏损币种 → 降低优先级
        for symbol in comparison.get('common_loss_symbols', []):
            actions.append({
                'type': 'priority_adjust',
                'symbol': symbol,
                'new_priority': 99,
                'reason': f'{symbol}在双模式中均亏损，降低优先级',
            })
        
        return actions

    def _generate_divergent_actions(self, comparison: Dict) -> List[Dict]:
        """分歧时的进化动作"""
        actions = []
        
        actions.append({
            'type': 'investigate',
            'message': '双模式结果不一致，需要深入分析',
            'details': f'历史成交{comparison["hist_direction"]}，市场回测{comparison["market_direction"]}',
            'suggestion': '检查数据质量，分析差异原因',
        })
        
        return actions

    def _analyze_paper(self) -> Dict:
        """分析模拟盘交易统计"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            cursor = conn.cursor()

            # 获取最近1000笔模拟交易
            cursor.execute("""
                SELECT side, price, amount, cost, fee, pnl, pnl_pct, status
                FROM engine_trades
                WHERE mode = 'paper' AND timestamp > strftime('%s', 'now', '-7 days')
                ORDER BY timestamp DESC
                LIMIT 1000
            """)
            rows = cursor.fetchall()
            conn.close()

            if not rows:
                return {'trades': 0, 'avg_pnl_pct': 0, 'win_rate': 0, 'total_pnl': 0}

            total_trades = len(rows)
            winning_trades = sum(1 for r in rows if r[5] > 0)
            total_pnl = sum(r[5] for r in rows)
            win_rate = winning_trades / total_trades if total_trades > 0 else 0

            # 按币种统计
            cursor.execute("""
                SELECT symbol, COUNT(*) as cnt, AVG(pnl) as avg_pnl,
                       SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins
                FROM engine_trades
                WHERE mode = 'paper' AND timestamp > strftime('%s', 'now', '-7 days')
                GROUP BY symbol
                ORDER BY avg_pnl DESC
            """)
            symbol_stats = [{'symbol': s[0], 'trades': s[1], 'avg_pnl': s[2], 'wins': s[3]} for s in cursor.fetchall()]
            conn.close()

            return {
                'trades': total_trades,
                'winning_trades': winning_trades,
                'win_rate': win_rate,
                'total_pnl': total_pnl,
                'avg_pnl_pct': total_pnl / total_trades if total_trades > 0 else 0,
                'symbol_stats': symbol_stats,
            }
        except Exception as e:
            logger.error(f"分析模拟盘数据失败: {e}")
            return {'error': str(e), 'trades': 0}

    def _apply_parameter_change(self, action: Dict):
        """应用参数变更"""
        if action['type'] != 'parameter_change':
            return

        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO evolution_history (timestamp, parameter, old_value, new_value, reason, applied)
                VALUES (?, ?, ?, ?, ?, 1)
            """, (datetime.now().timestamp(), action['target'], action.get('old_value'), action['new_value'], action.get('reason', '')))

            conn.commit()
            conn.close()

            logger.info(f"📝 应用参数变更: {action['target']} {action.get('old_value')} → {action['new_value']}")

        except Exception as e:
            logger.error(f"应用参数变更失败: {e}")

    def _save_report(self, report: Dict):
        """保存进化报告"""
        report_dir = '/root/SOM/qnt/evolution_reports'
        os.makedirs(report_dir, exist_ok=True)

        filename = f"evolution_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(report_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            import json
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)

        logger.info(f"📄 进化报告已保存: {filepath}")

    def get_status(self) -> Dict:
        """获取进化管理器状态"""
        return {
            'evolution_count': self.evolution_count,
            'last_analysis': datetime.now().isoformat(),
        }
