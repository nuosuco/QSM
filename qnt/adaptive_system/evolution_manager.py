"""
自适应进化交易系统 - 自进化管理器
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
    """策略自进化管理器"""

    def __init__(self, db_path: str, config=None):
        self.db_path = db_path
        self.config = config
        self.evolution_count = 0

    def analyze_and_evolve(self) -> Dict:
        """执行一次完整进化分析，返回分析报告"""
        logger.info("=" * 60)
        logger.info("🧬 开始自进化分析...")
        logger.info("=" * 60)

        report = {
            'timestamp': datetime.now().isoformat(),
            'analysis': {},
            'actions': [],
            'parameter_changes': [],
        }

        # 1. 分析回测表现
        backtest_stats = self._analyze_backtest()
        report['analysis']['backtest'] = backtest_stats
        if backtest_stats['trades'] >= MIN_SAMPLES_FOR_ANALYSIS:
            actions = self._generate_backtest_actions(backtest_stats)
            report['actions'].extend(actions)

        # 2. 分析模拟表现
        paper_stats = self._analyze_paper()
        report['analysis']['paper'] = paper_stats
        if paper_stats['trades'] >= MIN_SAMPLES_FOR_ANALYSIS:
            actions = self._generate_paper_actions(paper_stats)
            report['actions'].extend(actions)

        # 3. 分析实盘表现（如果有）
        live_stats = self._analyze_live()
        report['analysis']['live'] = live_stats
        if live_stats['trades'] >= MIN_SAMPLES_FOR_ANALYSIS:
            actions = self._generate_live_actions(live_stats)
            report['actions'].extend(actions)

        # 4. 应用变更
        for action in report['actions']:
            if action['type'] == 'parameter_change':
                self._apply_parameter_change(action)
                report['parameter_changes'].append(action)

        self.evolution_count += 1
        logger.info(f"✅ 第{self.evolution_count}次进化完成，共{len(report['actions'])}项调整")

        # 保存报告
        self._save_report(report)

        return report

    def _analyze_backtest(self) -> Dict:
        """分析回测交易统计"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            cursor = conn.cursor()

            # 获取最近1000笔回测交易
            cursor.execute("""
                SELECT side, price, amount, cost, fee, pnl, pnl_pct, status
                FROM engine_trades
                WHERE mode = 'backtest' AND timestamp > strftime('%s', 'now', '-7 days')
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
            avg_pnl_pct = sum(r[6] for r in rows) / total_trades if total_trades > 0 else 0
            win_rate = winning_trades / total_trades if total_trades > 0 else 0

            return {
                'trades': total_trades,
                'winning_trades': winning_trades,
                'win_rate': win_rate,
                'total_pnl': total_pnl,
                'avg_pnl_pct': avg_pnl_pct,
                'avg_profit_when_win': sum(r[5] for r in rows if r[5] > 0) / winning_trades if winning_trades > 0 else 0,
                'avg_loss_when_lose': sum(r[5] for r in rows if r[5] <= 0) / (total_trades - winning_trades) if (total_trades - winning_trades) > 0 else 0,
            }
        except Exception as e:
            logger.error(f"分析回测数据失败: {e}")
            return {'error': str(e), 'trades': 0}

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
            avg_pnl_pct = sum(r[6] for r in rows) / total_trades if total_trades > 0 else 0
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
            symbol_stats = cursor.fetchall()
            conn.close()

            return {
                'trades': total_trades,
                'winning_trades': winning_trades,
                'win_rate': win_rate,
                'total_pnl': total_pnl,
                'avg_pnl_pct': avg_pnl_pct,
                'symbol_stats': [{'symbol': s[0], 'trades': s[1], 'avg_pnl': s[2], 'wins': s[3]} for s in symbol_stats],
            }
        except Exception as e:
            logger.error(f"分析模拟盘数据失败: {e}")
            return {'error': str(e), 'trades': 0}

    def _analyze_live(self) -> Dict:
        """分析实盘交易统计"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            cursor = conn.cursor()

            # 获取最近1000笔实盘交易
            cursor.execute("""
                SELECT side, price, amount, cost, fee, pnl, pnl_pct, status
                FROM engine_trades
                WHERE mode = 'live' AND timestamp > strftime('%s', 'now', '-7 days')
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
            avg_pnl_pct = sum(r[6] for r in rows) / total_trades if total_trades > 0 else 0
            win_rate = winning_trades / total_trades if total_trades > 0 else 0

            return {
                'trades': total_trades,
                'winning_trades': winning_trades,
                'win_rate': win_rate,
                'total_pnl': total_pnl,
                'avg_pnl_pct': avg_pnl_pct,
            }
        except Exception as e:
            logger.error(f"分析实盘数据失败: {e}")
            return {'error': str(e), 'trades': 0}

    def _generate_backtest_actions(self, stats: Dict) -> List[Dict]:
        """根据回测结果生成进化动作"""
        actions = []

        # 胜率过低 → 收紧阈值
        if stats['win_rate'] < 0.45 and stats['trades'] >= MIN_SAMPLES_FOR_VALIDATION:
            actions.append({
                'type': 'parameter_change',
                'target': 'risk_manager.MIN_NET_PROFIT_PCT',
                'old_value': 0.0001,
                'new_value': 0.0002,
                'reason': f'回测胜率过低({stats["win_rate"]*100:.1f}%)，收紧净利要求',
            })

        # 样本不足但表现好 → 可以适当放宽
        elif stats['win_rate'] > 0.55 and stats['trades'] < MIN_SAMPLES_FOR_VALIDATION:
            actions.append({
                'type': 'parameter_change',
                'target': 'execution.spread_pct',
                'old_value': 0.17,
                'new_value': 0.15,
                'reason': f'回测表现优异({stats["win_rate"]*100:.1f}%)，样本较少，适当放宽门槛',
            })

        return actions

    def _generate_paper_actions(self, stats: Dict) -> List[Dict]:
        """根据模拟盘结果生成进化动作"""
        actions = []

        # 模拟盘胜率过低 → 通知控制器暂停实盘
        if stats['win_rate'] < 0.45 and stats['trades'] >= MIN_SAMPLES_FOR_ANALYSIS:
            actions.append({
                'type': 'alert',
                'level': 'warning',
                'message': f'模拟盘胜率过低({stats["win_rate"]*100:.1f}%)，建议暂停实盘',
                'target': 'controller',
            })

        # 最佳表现币种 → 提升该币种优先级
        if stats.get('symbol_stats'):
            best_symbol = max(stats['symbol_stats'], key=lambda x: x['avg_pnl'] if x['avg_pnl'] else 0)
            if best_symbol['avg_pnl'] > 0 and best_symbol['trades'] >= 10:
                actions.append({
                    'type': 'priority_adjust',
                    'symbol': best_symbol['symbol'],
                    'new_priority': 1,
                    'reason': f'{best_symbol["symbol"]}表现最佳，提升优先级',
                })

        # 最差表现币种 → 降低优先级或暂停
        worst_symbol = min(stats['symbol_stats'], key=lambda x: x['avg_pnl'] if x['avg_pnl'] else 0)
        if worst_symbol['avg_pnl'] < -0.05 and worst_symbol['trades'] >= 10:
            actions.append({
                'type': 'priority_adjust',
                'symbol': worst_symbol['symbol'],
                'new_priority': 99,
                'reason': f'{worst_symbol["symbol"]}表现最差，降低优先级',
            })

        return actions

    def _generate_live_actions(self, stats: Dict) -> List[Dict]:
        """根据实盘结果生成进化动作"""
        actions = []

        # 实盘亏损 → 立即暂停
        if stats['total_pnl'] < 0 and stats['trades'] >= 5:
            actions.append({
                'type': 'emergency_stop',
                'level': 'critical',
                'message': f'实盘亏损{stats["total_pnl"]:.2f}U，立即暂停交易',
                'target': 'controller',
            })

        # 实盘盈利且样本足够 → 可以扩大仓位
        elif stats['total_pnl'] > 0 and stats['trades'] >= MIN_SAMPLES_FOR_VALIDATION:
            actions.append({
                'type': 'parameter_change',
                'target': 'risk_manager.MAX_POSITION_PCT',
                'old_value': 0.20,
                'new_value': 0.25,
                'reason': f'实盘盈利且样本充足，可适当扩大仓位',
            })

        return actions

    def _apply_parameter_change(self, action: Dict):
        """应用参数变更"""
        if action['type'] != 'parameter_change':
            return

        target = action['target']
        new_value = action['new_value']

        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            cursor = conn.cursor()

            # 更新config表
            cursor.execute("""
                INSERT INTO evolution_history (timestamp, parameter, old_value, new_value, reason, applied)
                VALUES (?, ?, ?, ?, ?, 1)
            """, (datetime.now().timestamp(), target, action['old_value'], new_value, action['reason']))

            conn.commit()
            conn.close()

            logger.info(f"📝 应用参数变更: {target} {action['old_value']} → {new_value}")
            logger.info(f"   原因: {action['reason']}")

            # TODO: 实际修改config.py文件（需要重新加载配置）
            # 这里只是记录，实际生效需要重启引擎

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
            json.dump(report, f, indent=2, ensure_ascii=False)

        logger.info(f"📄 进化报告已保存: {filepath}")

    def get_status(self) -> Dict:
        """获取进化管理器状态"""
        return {
            'evolution_count': self.evolution_count,
            'last_analysis': datetime.now().isoformat(),
        }
