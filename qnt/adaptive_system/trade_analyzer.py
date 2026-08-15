"""
交易总结引擎 - 自动学习系统
- 模拟盘总结：分析模拟交易的盈亏模式
- 实盘总结：分析真实交易的执行效果
- 阶段性升级：根据数据自动优化策略和风控
"""
import sqlite3
import numpy as np
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import json

class TradeAnalyzer:
    """交易分析器 - 自动从历史交易中学习"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        
    def analyze_simulated_trades(self, hours: int = 24) -> Dict:
        """分析模拟盘交易，总结规律"""
        cursor = self.conn.cursor()
        
        # 获取最近N小时的模拟交易
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        cursor.execute('''
            SELECT * FROM signals 
            WHERE strategy = 'paper' 
            AND timestamp > ?
            ORDER BY timestamp DESC
        ''', (cutoff.timestamp(),))
        
        trades = cursor.fetchall()
        
        if len(trades) < 10:
            return {'status': 'insufficient_data', 'trade_count': len(trades)}
        
        # 统计分析
        profits = [t[7] for t in trades if t[7] is not None]  # actual_profit
        wins = [p for p in profits if p > 0]
        losses = [p for p in profits if p <= 0]
        
        # 按小时统计
        hourly_stats = defaultdict(lambda: {'count': 0, 'profit': 0, 'wins': 0})
        for trade in trades:
            hour = datetime.fromtimestamp(trade[1]).hour
            hourly_stats[hour]['count'] += 1
            hourly_stats[hour]['profit'] += trade[7] or 0
            if trade[7] and trade[7] > 0:
                hourly_stats[hour]['wins'] += 1
        
        # 找出最佳时段
        best_hour = max(hourly_stats.items(), key=lambda x: x[1]['profit']/max(x[1]['count'],1))
        
        return {
            'total_trades': len(trades),
            'win_rate': len(wins) / len(profits) if profits else 0,
            'avg_profit': np.mean(profits) if profits else 0,
            'max_win': max(profits) if profits else 0,
            'max_loss': min(profits) if profits else 0,
            'best_hour': best_hour[0],
            'best_hour_profit': best_hour[1]['profit'],
            'hourly_pattern': dict(hourly_stats)
        }
    
    def analyze_live_trades(self, hours: int = 24) -> Dict:
        """分析实盘交易，总结执行质量"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT * FROM qnt_trades 
            WHERE timestamp > ?
            ORDER BY timestamp DESC
        ''', ((datetime.utcnow() - timedelta(hours=hours)).timestamp(),))
        
        trades = cursor.fetchall()
        
        if len(trades) < 5:
            return {'status': 'insufficient_data', 'trade_count': len(trades)}
        
        # 计算执行质量
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
    
    def find_profitable_patterns(self) -> List[Dict]:
        """从历史数据中发现可盈利的模式"""
        cursor = self.conn.cursor()
        
        patterns = []
        
        # 1. 价差套利模式
        cursor.execute('''
            SELECT symbol, spread_pct, COUNT(*) as count,
                   AVG(CASE WHEN executed = 1 AND actual_profit > 0 THEN 1 ELSE 0 END) as win_rate
            FROM signals
            GROUP BY symbol
            HAVING count > 10
        ''')
        
        for row in cursor.fetchall():
            if row[3] > 0.5:  # 胜率>50%
                patterns.append({
                    'type': 'spread_arb',
                    'symbol': row[0],
                    'avg_spread': row[1],
                    'win_rate': row[3],
                    'sample_count': row[2]
                })
        
        # 2. 时段模式
        cursor.execute('''
            SELECT strftime('%H', datetime(timestamp, 'unixepoch')) as hour,
                   strategy, COUNT(*) as count,
                   AVG(CASE WHEN executed = 1 AND actual_profit > 0 THEN 1 ELSE 0 END) as win_rate
            FROM signals
            GROUP BY hour, strategy
            HAVING count > 5
        ''')
        
        for row in cursor.fetchall():
            patterns.append({
                'type': 'time_of_day',
                'hour': int(row[0]),
                'strategy': row[1],
                'win_rate': row[3],
                'sample_count': row[2]
            })
        
        return patterns
    
    def generate_upgrade_recommendations(self) -> Dict:
        """生成策略升级建议"""
        patterns = self.find_profitable_patterns()
        sim_analysis = self.analyze_simulated_trades(24)
        live_analysis = self.analyze_live_trades(24)
        
        recommendations = {
            'strategies_to_add': [],
            'parameters_to_adjust': {},
            'risk_control_updates': {},
            'confidence_level': 'low'
        }
        
        # 基于发现的模式生成建议
        for pattern in patterns:
            if pattern['type'] == 'spread_arb' and pattern['win_rate'] > 0.6:
                recommendations['strategies_to_add'].append({
                    'name': f'spread_arb_{pattern["symbol"]}',
                    'confidence': pattern['win_rate'],
                    'reason': f'{pattern["symbol"]}价差套利胜率{pattern["win_rate"]*100:.1f}%'
                })
            
            elif pattern['type'] == 'time_of_day' and pattern['win_rate'] > 0.5:
                recommendations['parameters_to_adjust'][f'time_window_{pattern["hour"]}'] = {
                    'action': 'increase_weight',
                    'confidence': pattern['win_rate'],
                    'reason': f'{pattern["hour"]}点策略表现好'
                }
        
        # 根据数据量调整信心等级
        total_samples = sim_analysis.get('total_trades', 0) + live_analysis.get('total_trades', 0)
        if total_samples > 100:
            recommendations['confidence_level'] = 'high'
        elif total_samples > 50:
            recommendations['confidence_level'] = 'medium'
        
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
        
        # 计算波动率
        volatility = np.std(spreads)
        mean_spread = np.mean(spreads)
        
        # 判断市场状态
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
            # 平静市场：提高仓位，降低止损
            adjustments['position_size'] = 1.5  # 提高50%
            adjustments['stop_loss_pct'] = 1.5   # 放宽止损
            adjustments['max_trades_per_hour'] = 10
        elif regime['regime'] == 'normal':
            # 正常市场：标准参数
            adjustments['position_size'] = 1.0
            adjustments['stop_loss_pct'] = 2.0
            adjustments['max_trades_per_hour'] = 5
        elif regime['regime'] == 'volatile':
            # 波动市场：降低仓位，收紧止损
            adjustments['position_size'] = 0.5
            adjustments['stop_loss_pct'] = 1.0
            adjustments['max_trades_per_hour'] = 3
        else:  # extreme
            # 极端市场：暂停交易
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
        
        # 检查各阶段的指标
        checks = {
            'data_sufficient': False,
            'pattern_discovered': False,
            'strategy_validated': False,
            'profit_stable': False
        }
        
        # 数据量检查
        cursor.execute("SELECT COUNT(*) FROM market_data")
        data_count = cursor.fetchone()[0]
        checks['data_sufficient'] = data_count >= 10000
        
        # 模式发现检查
        cursor.execute("SELECT COUNT(*) FROM signals WHERE executed = 1")
        signal_count = cursor.fetchone()[0]
        checks['pattern_discovered'] = signal_count >= 50
        
        # 策略验证检查
        cursor.execute('''
            SELECT AVG(CASE WHEN actual_profit > 0 THEN 1.0 ELSE 0.0 END)
            FROM signals 
            WHERE strategy = 'paper' AND executed = 1
        ''')
        win_rate = cursor.fetchone()[0] or 0
        checks['strategy_validated'] = win_rate > 0.5 and signal_count >= 100
        
        # 盈利稳定性检查
        if signal_count >= 50:
            cursor.execute('''
                SELECT AVG(actual_profit), STDDEV(actual_profit)
                FROM signals 
                WHERE strategy = 'paper' AND executed = 1 AND actual_profit IS NOT NULL
            ''')
            result = cursor.fetchone()
            if result[1] and result[1] > 0:
                checks['profit_stable'] = result[0] > 0 and result[1] / result[0] < 2
        
        return checks
    
    def get_upgrade_recommendation(self) -> Dict:
        """获取升级建议"""
        checks = self.evaluate_phase_completion()
        
        if all(checks.values()):
            return {
                'phase': 'complete',
                'next_action': 'upgrade',
                'message': '数据充足，模式已发现，策略已验证，建议升级'
            }
        elif checks['data_sufficient'] and checks['pattern_discovered']:
            return {
                'phase': 'collecting',
                'next_action': 'continue_collection',
                'message': '数据和模式已有，继续收集更多数据验证策略'
            }
        else:
            return {
                'phase': 'initial',
                'next_action': 'collect_data',
                'message': '数据不足，继续收集市场数据'
            }
