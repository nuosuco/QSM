"""
交易总结引擎 - 自动学习系统
分析三个引擎的数据：回测(backtest)、模拟盘(paper)、实盘(live)
"""
import sqlite3
import numpy as np
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import json

class TradeAnalyzer:
    """交易分析器 - 自动从三个引擎的数据中学习"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        
    def analyze_backtest_trades(self, hours: int = 24) -> Dict:
        """分析回测引擎交易，总结历史表现"""
        cursor = self.conn.cursor()
        
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        cursor.execute('''
            SELECT * FROM engine_trades 
            WHERE mode = 'backtest' 
            AND timestamp > ?
            ORDER BY timestamp DESC
        ''', (cutoff.timestamp(),))
        
        trades = cursor.fetchall()
        
        if len(trades) < 10:
            return {'status': 'insufficient_data', 'trade_count': len(trades)}
        
        profits = [t[10] for t in trades if t[10] is not None]
        wins = [p for p in profits if p > 0]
        losses = [p for p in profits if p <= 0]
        
        return {
            'total_trades': len(trades),
            'win_rate': len(wins) / len(profits) if profits else 0,
            'avg_profit': np.mean(profits) if profits else 0,
            'max_win': max(profits) if profits else 0,
            'max_loss': min(profits) if profits else 0,
            'sharpe_ratio': np.mean(profits) / (np.std(profits) if np.std(profits) > 0 else 1)
        }
    
    def analyze_paper_trades(self, hours: int = 24) -> Dict:
        """分析模拟盘引擎交易，总结实时规律"""
        cursor = self.conn.cursor()
        
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        cursor.execute('''
            SELECT * FROM engine_trades 
            WHERE mode = 'paper' 
            AND timestamp > ?
            ORDER BY timestamp DESC
        ''', (cutoff.timestamp(),))
        
        trades = cursor.fetchall()
        
        if len(trades) < 10:
            return {'status': 'insufficient_data', 'trade_count': len(trades)}
        
        profits = [t[10] for t in trades if t[10] is not None]
        wins = [p for p in profits if p > 0]
        losses = [p for p in profits if p <= 0]
        
        # 按币种统计
        symbol_stats = defaultdict(lambda: {'count': 0, 'profit': 0, 'wins': 0})
        for trade in trades:
            symbol = trade[3]  # symbol column
            pnl = trade[10] or 0
            symbol_stats[symbol]['count'] += 1
            symbol_stats[symbol]['profit'] += pnl
            if pnl > 0:
                symbol_stats[symbol]['wins'] += 1
        
        # 找出最佳币种
        best_symbol = max(symbol_stats.items(), key=lambda x: x[1]['profit']/max(x[1]['count'],1))
        
        return {
            'total_trades': len(trades),
            'win_rate': len(wins) / len(profits) if profits else 0,
            'avg_profit': np.mean(profits) if profits else 0,
            'max_win': max(profits) if profits else 0,
            'max_loss': min(profits) if profits else 0,
            'best_symbol': best_symbol[0],
            'best_symbol_profit': best_symbol[1]['profit'],
            'symbol_stats': {k: v for k, v in symbol_stats.items()}
        }
    
    def analyze_live_trades(self, hours: int = 24) -> Dict:
        """分析实盘引擎交易，总结执行质量"""
        cursor = self.conn.cursor()
        
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        cursor.execute('''
            SELECT * FROM engine_trades 
            WHERE mode = 'live' 
            AND timestamp > ?
            ORDER BY timestamp DESC
        ''', (cutoff.timestamp(),))
        
        trades = cursor.fetchall()
        
        if len(trades) < 5:
            return {'status': 'insufficient_data', 'trade_count': len(trades)}
        
        profits = [t[10] for t in trades if t[10] is not None]
        expected_profits = [t[8] for t in trades if t[8] is not None]
        actual_profits = [t[9] for t in trades if t[9] is not None]
        
        slippage = []
        for exp, act in zip(expected_profits, actual_profits):
            if exp and act:
                slippage.append(act - exp)
        
        return {
            'total_trades': len(trades),
            'avg_slippage': np.mean(slippage) if slippage else 0,
            'slippage_std': np.std(slippage) if slippage else 0,
            'execution_quality': 'good' if np.mean(slippage) > -0.1 else 'poor'
        }
    
    def analyze_all_modes(self) -> Dict:
        """分析所有三个引擎的数据，生成综合报告"""
        backtest = self.analyze_backtest_trades(24)
        paper = self.analyze_paper_trades(24)
        live = self.analyze_live_trades(24)
        
        return {
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
        
        # 回测建议
        if backtest.get('win_rate', 0) > 0.6:
            recommendations.append("回测胜率良好，可继续模拟盘验证")
        
        # 模拟盘建议
        if paper.get('win_rate', 0) > 0.6:
            recommendations.append("模拟盘表现优秀，建议升级实盘")
        elif paper.get('total_trades', 0) < 10:
            recommendations.append(f"模拟盘数据不足({paper.get('total_trades', 0)}笔)，继续观察")
        
        # 实盘建议
        if live.get('total_trades', 0) > 0:
            recommendations.append(f"实盘已执行{live.get('total_trades', 0)}笔")
        
        if not recommendations:
            recommendations.append("数据不足，继续收集三个引擎的数据")
        
        return "; ".join(recommendations)
    
    def find_profitable_patterns(self) -> List[Dict]:
        """从三个引擎的数据中发现可盈利的模式"""
        cursor = self.conn.cursor()
        
        patterns = []
        
        # 1. 价差套利模式（从engine_signals）
        cursor.execute('''
            SELECT mode, symbol, expected_profit, COUNT(*) as count,
                   AVG(CASE WHEN actual_profit > 0 THEN 1 ELSE 0 END) as win_rate
            FROM engine_signals
            GROUP BY mode, symbol
            HAVING count > 10
        ''')
        
        for row in cursor.fetchall():
            if row[4] and row[4] > 0.5:
                patterns.append({
                    'type': 'spread_arb',
                    'mode': row[0],
                    'symbol': row[1],
                    'expected_profit': row[2],
                    'win_rate': row[4],
                    'sample_count': row[3]
                })
        
        # 2. 时段模式（从engine_signals）
        cursor.execute('''
            SELECT mode, strftime('%H', datetime(timestamp, 'unixepoch')) as hour,
                   COUNT(*) as count,
                   AVG(CASE WHEN actual_profit > 0 THEN 1 ELSE 0 END) as win_rate
            FROM engine_signals
            GROUP BY mode, hour
            HAVING count > 5
        ''')
        
        for row in cursor.fetchall():
            patterns.append({
                'type': 'time_of_day',
                'mode': row[0],
                'hour': int(row[1]),
                'win_rate': row[3],
                'sample_count': row[2]
            })
        
        return patterns
    
    def generate_upgrade_recommendations(self) -> Dict:
        """生成策略升级建议 - 基于三个引擎的数据"""
        all_analysis = self.analyze_all_modes()
        patterns = self.find_profitable_patterns()
        
        backtest = all_analysis['backtest']
        paper = all_analysis['paper']
        live = all_analysis['live']
        
        recommendations = {
            'strategies_to_add': [],
            'parameters_to_adjust': {},
            'risk_control_updates': {},
            'confidence_level': 'low',
            'next_action': 'continue_collecting'
        }
        
        # 基于回测结果
        if backtest.get('win_rate', 0) > 0.6:
            recommendations['strategies_to_add'].append({
                'name': 'fat_finger_arb',
                'confidence': backtest['win_rate'],
                'source': 'backtest',
                'reason': f'回测胜率{backtest["win_rate"]*100:.1f}%'
            })
        
        # 基于模拟盘结果
        if paper.get('win_rate', 0) > 0.6 and paper.get('total_trades', 0) > 50:
            recommendations['strategies_to_add'].append({
                'name': 'fat_finger_arb_paper',
                'confidence': paper['win_rate'],
                'source': 'paper',
                'reason': f'模拟盘胜率{paper["win_rate"]*100:.1f}%，数据充足'
            })
            
            # 推荐最佳币种
            if paper.get('best_symbol'):
                recommendations['parameters_to_adjust'][f'focus_symbol_{paper["best_symbol"]}'] = {
                    'action': 'increase_weight',
                    'confidence': paper['win_rate'],
                    'reason': f'{paper["best_symbol"]}在模拟盘表现最好'
                }
        
        # 基于实盘结果
        if live.get('total_trades', 0) > 0:
            recommendations['confidence_level'] = 'medium'
        
        # 综合数据量评估信心等级
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


class AdaptiveRiskManager:
    """自适应风控管理器 - 根据市场状态动态调整风控参数"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        
    def analyze_market_regime(self) -> Dict:
        """分析当前市场状态"""
        cursor = self.conn.cursor()
        
        # 获取最近1000条价差数据
        cursor.execute('''
            SELECT spread_pct, timestamp 
            FROM market_data 
            ORDER BY timestamp DESC 
            LIMIT 1000
        ''')
        
        rows = cursor.fetchall()
        if not rows:
            return {'regime': 'unknown', 'volatility': 0}
        
        spreads = np.array([r[0] for r in rows])
        
        volatility = np.std(spreads)
        mean_spread = np.mean(spreads)
        
        if volatility < 0.02:
            regime = 'calm'
        elif volatility < 0.05:
            regime = 'normal'
        elif volatility < 0.10:
            regime = 'volatile'
        else:
            regime = 'extreme'
        
        return {
            'regime': regime,
            'volatility': float(volatility),
            'mean_spread': float(mean_spread),
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
    
    def get_current_risk_status(self) -> Dict:
        """获取当前风控状态"""
        regime = self.analyze_market_regime()
        adjustments = self.adjust_risk_parameters(regime)
        
        return {
            'market_regime': regime,
            'risk_adjustments': adjustments,
            'suspension_recommended': adjustments.get('suspension_recommended', False)
        }


class PhaseUpgradeManager:
    """阶段性升级管理器"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        
    def evaluate_phase_completion(self) -> Dict:
        """评估当前阶段是否完成"""
        cursor = self.conn.cursor()
        
        checks = {
            'data_sufficient': False,
            'pattern_discovered': False,
            'strategy_validated': False,
            'profit_stable': False
        }
        
        # 数据量检查（三个引擎总和）
        cursor.execute("SELECT COUNT(*) FROM market_data")
        data_count = cursor.fetchone()[0]
        checks['data_sufficient'] = data_count >= 10000
        
        # 模式发现检查（engine_signals中三种模式的信号）
        cursor.execute("SELECT COUNT(*) FROM engine_signals WHERE mode = 'paper'")
        paper_signals = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM engine_signals WHERE mode = 'live'")
        live_signals = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM engine_trades WHERE mode = 'paper'")
        paper_trades = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM engine_trades WHERE mode = 'live'")
        live_trades = cursor.fetchone()[0]
        
        checks['pattern_discovered'] = (paper_trades + live_trades) >= 50
        
        # 策略验证检查（模拟盘+实盘）
        cursor.execute('''
            SELECT AVG(CASE WHEN pnl > 0 THEN 1.0 ELSE 0.0 END)
            FROM engine_trades 
            WHERE mode = 'paper' AND pnl IS NOT NULL
        ''')
        paper_win_rate = cursor.fetchone()[0] or 0
        cursor.execute('''
            SELECT AVG(CASE WHEN pnl > 0 THEN 1.0 ELSE 0.0 END)
            FROM engine_trades 
            WHERE mode = 'live' AND pnl IS NOT NULL
        ''')
        live_win_rate = cursor.fetchone()[0] or 0
        
        checks['strategy_validated'] = (
            (paper_win_rate > 0.5 and paper_trades >= 100) or
            (live_win_rate > 0.5 and live_trades >= 50)
        )
        
        # 盈利稳定性检查
        if (paper_trades + live_trades) >= 50:
            cursor.execute('''
                SELECT AVG(pnl), STDDEV(pnl)
                FROM engine_trades 
                WHERE mode IN ('paper', 'live') AND pnl IS NOT NULL
            ''')
            result = cursor.fetchone()
            if result[1] and result[1] > 0:
                checks['profit_stable'] = result[0] > 0 and result[1] / max(abs(result[0]), 0.001) < 2
        
        return {
            **checks,
            'data_points': data_count,
            'paper_trades': paper_trades,
            'live_trades': live_trades,
            'paper_win_rate': paper_win_rate,
            'live_win_rate': live_win_rate
        }
    
    def get_upgrade_recommendation(self) -> Dict:
        """获取升级建议"""
        checks = self.evaluate_phase_completion()
        
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
