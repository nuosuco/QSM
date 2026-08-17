"""
交易总结引擎 - 自动学习系统（三平台版）
分析三个引擎的数据：回测(backtest)、模拟盘(paper)、实盘(live)
支持按平台（exchange）分别分析
"""
import sqlite3
import numpy as np
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json


class TradeAnalyzer:
    """交易分析器 - 自动从三个引擎的数据中学习，支持按平台分析"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
    
    def _exchange_filter(self, exchange: Optional[str]) -> str:
        """生成按平台过滤的SQL条件"""
        if exchange:
            return f" AND exchange = '{exchange}'"
        return ""
    
    def analyze_backtest_trades(self, hours: int = 24, exchange: Optional[str] = None) -> Dict:
        """分析回测引擎交易，总结历史表现。可指定平台"""
        cursor = self.conn.cursor()
        ex_filter = self._exchange_filter(exchange)
        
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        cursor.execute(f'''
            SELECT * FROM engine_trades 
            WHERE mode = 'backtest' 
            AND timestamp > ?
            {ex_filter}
            ORDER BY timestamp DESC
        ''', (cutoff.timestamp(),))
        
        trades = cursor.fetchall()
        
        if len(trades) < 10:
            return {'status': 'insufficient_data', 'trade_count': len(trades),
                    'exchange': exchange or 'all'}
        
        profits = [t['pnl'] for t in trades if t['pnl'] is not None]
        wins = [p for p in profits if p > 0]
        losses = [p for p in profits if p <= 0]
        
        return {
            'exchange': exchange or 'all',
            'total_trades': len(trades),
            'win_rate': len(wins) / len(profits) if profits else 0,
            'avg_profit': np.mean(profits) if profits else 0,
            'max_win': max(profits) if profits else 0,
            'max_loss': min(profits) if profits else 0,
            'sharpe_ratio': np.mean(profits) / (np.std(profits) if np.std(profits) > 0 else 1)
        }
    
    def analyze_paper_trades(self, hours: int = 24, exchange: Optional[str] = None) -> Dict:
        """分析模拟盘引擎交易，总结实时规律。可指定平台"""
        cursor = self.conn.cursor()
        ex_filter = self._exchange_filter(exchange)
        
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        cursor.execute(f'''
            SELECT * FROM engine_trades 
            WHERE mode = 'paper' 
            AND timestamp > ?
            {ex_filter}
            ORDER BY timestamp DESC
        ''', (cutoff.timestamp(),))
        
        trades = cursor.fetchall()
        
        if len(trades) < 10:
            return {'status': 'insufficient_data', 'trade_count': len(trades),
                    'exchange': exchange or 'all'}
        
        profits = [t['pnl'] for t in trades if t['pnl'] is not None]
        wins = [p for p in profits if p > 0]
        
        # 按币种统计
        symbol_stats = defaultdict(lambda: {'count': 0, 'profit': 0, 'wins': 0})
        for trade in trades:
            symbol = trade['symbol']
            pnl = trade['pnl'] or 0
            symbol_stats[symbol]['count'] += 1
            symbol_stats[symbol]['profit'] += pnl
            if pnl > 0:
                symbol_stats[symbol]['wins'] += 1
        
        # 找出最佳币种
        best = max(symbol_stats.items(), key=lambda x: x[1]['profit']/max(x[1]['count'], 1))
        
        return {
            'exchange': exchange or 'all',
            'total_trades': len(trades),
            'win_rate': len(wins) / len(profits) if profits else 0,
            'avg_profit': np.mean(profits) if profits else 0,
            'max_win': max(profits) if profits else 0,
            'max_loss': min(profits) if profits else 0,
            'best_symbol': best[0],
            'best_symbol_profit': best[1]['profit'],
            'symbol_stats': {k: dict(v) for k, v in symbol_stats.items()}
        }
    
    def analyze_live_trades(self, hours: int = 24, exchange: Optional[str] = None) -> Dict:
        """分析实盘引擎交易，总结执行质量。可指定平台"""
        cursor = self.conn.cursor()
        ex_filter = self._exchange_filter(exchange)
        
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        cursor.execute(f'''
            SELECT * FROM engine_trades 
            WHERE mode = 'live' 
            AND timestamp > ?
            {ex_filter}
            ORDER BY timestamp DESC
        ''', (cutoff.timestamp(),))
        
        trades = cursor.fetchall()
        
        if len(trades) < 5:
            return {'status': 'insufficient_data', 'trade_count': len(trades),
                    'exchange': exchange or 'all'}
        
        # 实际盈亏
        profits = [t['pnl'] for t in trades if t['pnl'] is not None]
        
        # 滑点计算（预期盈亏 vs 实际盈亏）
        slippage = []
        for t in trades:
            expected = t.get('expected_profit')
            actual = t.get('actual_profit')
            if expected is not None and actual is not None:
                slippage.append(actual - expected)
        
        return {
            'exchange': exchange or 'all',
            'total_trades': len(trades),
            'avg_slippage': np.mean(slippage) if slippage else 0,
            'slippage_std': np.std(slippage) if slippage else 0,
            'execution_quality': 'good' if (np.mean(slippage) if slippage else 0) > -0.1 else 'poor'
        }
    
    def analyze_all_modes(self, exchange: Optional[str] = None) -> Dict:
        """分析三个引擎的数据，按平台生成综合报告"""
        backtest = self.analyze_backtest_trades(24, exchange=exchange)
        paper = self.analyze_paper_trades(24, exchange=exchange)
        live = self.analyze_live_trades(24, exchange=exchange)
        
        return {
            'exchange': exchange or 'all',
            'backtest': backtest,
            'paper': paper,
            'live': live,
            'summary': {
                'total_backtest_trades': backtest.get('total_trades', 0),
                'total_paper_trades': paper.get('total_trades', 0),
                'total_live_trades': live.get('total_trades', 0),
                'paper_win_rate': paper.get('win_rate', 0),
                'backtest_win_rate': backtest.get('win_rate', 0),
                'recommendation': self._get_recommendation(backtest, paper, live)
            }
        }
    
    def _get_recommendation(self, backtest: Dict, paper: Dict, live: Dict) -> str:
        """生成综合建议"""
        recommendations = []
        
        if backtest.get('win_rate', 0) > 0.6:
            recommendations.append("回测胜率良好，可继续模拟盘验证")
        
        if paper.get('win_rate', 0) > 0.6:
            recommendations.append("模拟盘表现优秀，建议升级实盘")
        elif paper.get('total_trades', 0) < 10:
            recommendations.append(f"模拟盘数据不足({paper.get('total_trades', 0)}笔)，继续观察")
        
        if live.get('total_trades', 0) > 0:
            recommendations.append(f"实盘已执行{live.get('total_trades', 0)}笔")
        
        if not recommendations:
            recommendations.append("数据不足，继续收集三个引擎的数据")
        
        return "; ".join(recommendations)
    
    def find_profitable_patterns(self, exchange: Optional[str] = None) -> List[Dict]:
        """从三个引擎的数据中发现可盈利的模式，可指定平台"""
        cursor = self.conn.cursor()
        ex_filter = self._exchange_filter(exchange)
        
        patterns = []
        
        # 1. 价差套利模式
        cursor.execute(f'''
            SELECT exchange, mode, symbol, expected_profit, COUNT(*) as count,
                   AVG(CASE WHEN actual_profit > 0 THEN 1 ELSE 0 END) as win_rate
            FROM engine_signals
            WHERE 1=1 {ex_filter}
            GROUP BY exchange, mode, symbol
            HAVING count > 10
        ''')
        
        for row in cursor.fetchall():
            if row[5] and row[5] > 0.5:
                patterns.append({
                    'type': 'spread_arb',
                    'exchange': row[0],
                    'mode': row[1],
                    'symbol': row[2],
                    'expected_profit': row[3],
                    'win_rate': row[5],
                    'sample_count': row[4]
                })
        
        # 2. 时段模式
        cursor.execute(f'''
            SELECT exchange, mode, strftime('%%H', datetime(timestamp, 'unixepoch')) as hour,
                   COUNT(*) as count,
                   AVG(CASE WHEN actual_profit > 0 THEN 1 ELSE 0 END) as win_rate
            FROM engine_signals
            WHERE 1=1 {ex_filter}
            GROUP BY exchange, mode, hour
            HAVING count > 5
        ''')
        
        for row in cursor.fetchall():
            patterns.append({
                'type': 'time_of_day',
                'exchange': row[0],
                'mode': row[1],
                'hour': int(row[2]),
                'win_rate': row[4],
                'sample_count': row[3]
            })
        
        return patterns
    
    def generate_upgrade_recommendations(self, exchange: Optional[str] = None) -> Dict:
        """生成策略升级建议，可指定平台"""
        all_analysis = self.analyze_all_modes(exchange=exchange)
        patterns = self.find_profitable_patterns(exchange=exchange)
        
        backtest = all_analysis['backtest']
        paper = all_analysis['paper']
        live = all_analysis['live']
        
        recommendations = {
            'exchange': exchange or 'all',
            'strategies_to_add': [],
            'parameters_to_adjust': {},
            'risk_control_updates': {},
            'confidence_level': 'low',
            'next_action': 'continue_collecting'
        }
        
        if backtest.get('win_rate', 0) > 0.6:
            recommendations['strategies_to_add'].append({
                'name': 'fat_finger_arb',
                'confidence': backtest['win_rate'],
                'source': 'backtest',
                'reason': f'回测胜率{backtest["win_rate"]*100:.1f}%'
            })
        
        if paper.get('win_rate', 0) > 0.6 and paper.get('total_trades', 0) > 50:
            recommendations['strategies_to_add'].append({
                'name': 'fat_finger_arb_paper',
                'confidence': paper['win_rate'],
                'source': 'paper',
                'reason': f'模拟盘胜率{paper["win_rate"]*100:.1f}%'
            })
            if paper.get('best_symbol'):
                recommendations['parameters_to_adjust'][f'focus_symbol_{paper["best_symbol"]}'] = {
                    'action': 'increase_weight',
                    'confidence': paper['win_rate'],
                    'reason': f'{paper["best_symbol"]}在模拟盘表现最好'
                }
        
        if live.get('total_trades', 0) > 0:
            recommendations['confidence_level'] = 'medium'
        
        total_trades = (
            backtest.get('total_trades', 0) + 
            paper.get('total_trades', 0) + 
            live.get('total_trades', 0)
        )
        if total_trades > 200:
            recommendations['confidence_level'] = 'high'
            recommendations['next_action'] = 'ready_for_live'
        elif total_trades > 100:
            recommendations['confidence_level'] = 'medium'
            recommendations['next_action'] = 'continue_validation'
        
        return recommendations
    
    def close(self):
        self.conn.close()


class AdaptiveRiskManager:
    """自适应风控管理器 - 根据市场状态动态调整风控参数"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        
    def analyze_market_regime(self, exchange: Optional[str] = None) -> Dict:
        """分析当前市场状态，可指定平台"""
        cursor = self.conn.cursor()
        ex_filter = f" AND exchange = '{exchange}'" if exchange else ""
        
        cursor.execute(f'''
            SELECT spread_pct, timestamp 
            FROM market_data 
            WHERE 1=1 {ex_filter}
            ORDER BY timestamp DESC 
            LIMIT 1000
        ''')
        
        rows = cursor.fetchall()
        if not rows:
            return {'regime': 'unknown', 'volatility': 0, 'exchange': exchange or 'all'}
        
        spreads = np.array([r[0] for r in rows])
        volatility = np.std(spreads)
        
        if volatility < 0.02:
            regime = 'calm'
        elif volatility < 0.05:
            regime = 'normal'
        elif volatility < 0.10:
            regime = 'volatile'
        else:
            regime = 'extreme'
        
        return {
            'exchange': exchange or 'all',
            'regime': regime,
            'volatility': float(volatility),
            'mean_spread': float(np.mean(spreads)),
            'spread_max': float(np.max(np.abs(spreads)))
        }
    
    def adjust_risk_parameters(self, regime: Dict) -> Dict:
        """根据市场状态调整风控参数"""
        adjustments = {}
        
        if regime['regime'] == 'calm':
            adjustments['position_size'] = 1.5
            adjustments['stop_loss_pct'] = 1.5
            adjustments['max_trades_per_hour'] = 10
        elif regime['regime'] == 'normal':
            adjustments['position_size'] = 1.0
            adjustments['stop_loss_pct'] = 2.0
            adjustments['max_trades_per_hour'] = 5
        elif regime['regime'] == 'volatile':
            adjustments['position_size'] = 0.5
            adjustments['stop_loss_pct'] = 1.0
            adjustments['max_trades_per_hour'] = 3
        else:
            adjustments['position_size'] = 0
            adjustments['stop_loss_pct'] = 0.5
            adjustments['max_trades_per_hour'] = 0
            adjustments['suspension_recommended'] = True
        
        return adjustments
    
    def get_current_risk_status(self, exchange: Optional[str] = None) -> Dict:
        """获取当前风控状态，可指定平台"""
        regime = self.analyze_market_regime(exchange=exchange)
        adjustments = self.adjust_risk_parameters(regime)
        
        return {
            'market_regime': regime,
            'risk_adjustments': adjustments,
            'suspension_recommended': adjustments.get('suspension_recommended', False)
        }
    
    def close(self):
        self.conn.close()


class PhaseUpgradeManager:
    """阶段性升级管理器"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        
    def evaluate_phase_completion(self, exchange: Optional[str] = None) -> Dict:
        """评估当前阶段是否完成，可指定平台"""
        cursor = self.conn.cursor()
        ex_filter = f" AND exchange = '{exchange}'" if exchange else ""
        
        checks = {
            'data_sufficient': False,
            'pattern_discovered': False,
            'strategy_validated': False,
            'profit_stable': False
        }
        
        cursor.execute(f"SELECT COUNT(*) FROM market_data WHERE 1=1 {ex_filter}")
        data_count = cursor.fetchone()[0]
        checks['data_sufficient'] = data_count >= 10000
        
        cursor.execute(f"SELECT COUNT(*) FROM engine_signals WHERE mode = 'paper' AND 1=1 {ex_filter}")
        paper_signals = cursor.fetchone()[0]
        cursor.execute(f"SELECT COUNT(*) FROM engine_signals WHERE mode = 'live' AND 1=1 {ex_filter}")
        live_signals = cursor.fetchone()[0]
        cursor.execute(f"SELECT COUNT(*) FROM engine_trades WHERE mode = 'paper' AND 1=1 {ex_filter}")
        paper_trades = cursor.fetchone()[0]
        cursor.execute(f"SELECT COUNT(*) FROM engine_trades WHERE mode = 'live' AND 1=1 {ex_filter}")
        live_trades = cursor.fetchone()[0]
        
        checks['pattern_discovered'] = (paper_trades + live_trades) >= 50
        
        cursor.execute(f'''
            SELECT AVG(CASE WHEN pnl > 0 THEN 1.0 ELSE 0.0 END)
            FROM engine_trades 
            WHERE mode = 'paper' AND pnl IS NOT NULL
            {ex_filter}
        ''')
        paper_win_rate = cursor.fetchone()[0] or 0
        cursor.execute(f'''
            SELECT AVG(CASE WHEN pnl > 0 THEN 1.0 ELSE 0.0 END)
            FROM engine_trades 
            WHERE mode = 'live' AND pnl IS NOT NULL
            {ex_filter}
        ''')
        live_win_rate = cursor.fetchone()[0] or 0
        
        checks['strategy_validated'] = (
            (paper_win_rate > 0.5 and paper_trades >= 100) or
            (live_win_rate > 0.5 and live_trades >= 50)
        )
        
        if (paper_trades + live_trades) >= 50:
            cursor.execute(f'''
                SELECT AVG(pnl), STDDEV(pnl)
                FROM engine_trades 
                WHERE mode IN ('paper', 'live') AND pnl IS NOT NULL
                {ex_filter}
            ''')
            result = cursor.fetchone()
            if result[1] and result[1] > 0:
                checks['profit_stable'] = result[0] > 0 and result[1] / max(abs(result[0]), 0.001) < 2
        
        return {
            'exchange': exchange or 'all',
            **checks,
            'data_points': data_count,
            'paper_trades': paper_trades,
            'live_trades': live_trades,
            'paper_win_rate': paper_win_rate,
            'live_win_rate': live_win_rate
        }
    
    def get_upgrade_recommendation(self, exchange: Optional[str] = None) -> Dict:
        """获取升级建议"""
        checks = self.evaluate_phase_completion(exchange=exchange)
        
        if all([checks['data_sufficient'], checks['pattern_discovered'], 
                checks['strategy_validated'], checks['profit_stable']]):
            return {
                'phase': 'complete',
                'next_action': 'upgrade',
                'message': '三个引擎数据充足，策略已验证，建议升级实盘',
                'details': checks
            }
        elif checks['data_sufficient'] and checks['pattern_discovered']:
            return {
                'phase': 'validating',
                'next_action': 'continue_validation',
                'message': '数据和模式已有，继续验证策略稳定性',
                'details': checks
            }
        else:
            return {
                'phase': 'collecting',
                'next_action': 'collect_data',
                'message': f'数据不足({checks["data_points"]}点)，继续收集三个引擎的数据',
                'details': checks
            }
    
    def close(self):
        self.conn.close()