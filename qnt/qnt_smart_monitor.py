#!/usr/bin/env python3
"""QNT智能监控 - 只在关键事件时推送"""
import os
import sys
import time
import subprocess
import sqlite3
import ccxt
from datetime import datetime, timedelta
from pathlib import Path

THRESHOLD = 0.17
CHECK_INTERVAL = 60  # 每60秒检查一次
LOG_FILE = "/root/SOM/qnt/qnt_smart_monitor.log"
STATE_FILE = "/root/SOM/qnt/qnt_monitor_state.json"

def log(msg):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, 'a') as f:
        f.write(line + '\n')

def send_notification(msg):
    """发送QQ消息"""
    try:
        result = subprocess.run(
            ['openclaw', 'message', 'send', 
             '--target', 'qqbot:c2c:861B1B2CC9C89FC4A3E0325F10407447',
             '--message', msg],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            log(f"✅ 通知已发送")
            return True
        else:
            log(f"❌ 发送失败: {result.stderr}")
            return False
    except Exception as e:
        log(f"❌ 发送异常: {e}")
        return False

def load_state():
    """加载监控状态"""
    try:
        import json
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return {
        'last_pattern_discovery': 0,
        'last_trade_alert': 0,
        'last_daily_report': 0,
        'known_patterns': []
    }

def save_state(state):
    """保存监控状态"""
    try:
        import json
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
    except:
        pass

def check_spreads():
    """检查所有平台价差"""
    exchanges = {}
    try:
        exchanges['Bitget'] = ccxt.bitget({
            'apiKey': os.getenv('BITGET_API_KEY', ''),
            'secret': os.getenv('BITGET_API_SECRET', ''),
            'password': os.getenv('BITGET_API_PASSPHRASE', ''),
            'enableRateLimit': True
        })
    except:
        log("⚠️ Bitget连接失败")
    
    try:
        exchanges['HTX'] = ccxt.htx({
            'apiKey': os.getenv('HTX_API_KEY', ''),
            'secret': os.getenv('HTX_API_SECRET', ''),
            'enableRateLimit': True
        })
    except:
        log("⚠️ HTX连接失败")
    
    try:
        exchanges['Gate.io'] = ccxt.gate({
            'apiKey': os.getenv('GATEIO_API_KEY', ''),
            'secret': os.getenv('GATEIO_API_SECRET', ''),
            'enableRateLimit': True
        })
    except:
        log("⚠️ Gate.io连接失败")
    
    symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT', 'XRP/USDT', 'DOGE/USDT', 'AVAX/USDT', 'LINK/USDT', 'PEPE/USDT', 'WIF/USDT', 'SUI/USDT', 'SEI/USDT', 'ARB/USDT', 'OP/USDT', 'DOT/USDT', 'ATOM/USDT', 'ONDO/USDT', 'FET/USDT', 'INJ/USDT', 'TIA/USDT']
    
    all_spreads = []
    for ex_name, ex in exchanges.items():
        for sym in symbols:
            try:
                spot = ex.fetch_ticker(sym)
                spot_price = (spot['bid'] + spot['ask']) / 2
                future = ex.fetch_ticker(sym.replace('/USDT', '/USDT:USDT'))
                future_price = (future['bid'] + future['ask']) / 2
                sp = abs(future_price - spot_price) / spot_price * 100
                all_spreads.append((ex_name, sym, sp))
            except:
                pass
    
    return all_spreads

def check_trades():
    """检查是否有新交易"""
    conn = sqlite3.connect("/root/SOM/data/trading_system/adaptive.db")
    cursor = conn.cursor()
    
    # 检查最近1小时的新交易
    cursor.execute("""
        SELECT mode, symbol, expected_profit, actual_profit, timestamp
        FROM engine_signals 
        WHERE executed = 1 
        AND timestamp > strftime('%s', 'now', '-1 hour')
        ORDER BY timestamp DESC
        LIMIT 10
    """)
    
    trades = []
    for row in cursor.fetchall():
        trades.append({
            'mode': row[0],
            'symbol': row[1],
            'spread': row[2],
            'profit': row[3],
            'timestamp': row[4]
        })
    
    conn.close()
    return trades

def analyze_patterns():
    """分析交易规律"""
    conn = sqlite3.connect("/root/SOM/data/trading_system/adaptive.db")
    cursor = conn.cursor()
    
    patterns = []
    
    # 1. 检查各平台最佳交易对
    cursor.execute("""
        SELECT exchange, symbol, AVG(spread_pct) as avg_spread,
               MAX(spread_pct) as max_spread,
               COUNT(*) as samples
        FROM market_data 
        WHERE timestamp > strftime('%s', 'now', '-24 hours')
        GROUP BY exchange, symbol
        ORDER BY avg_spread DESC
        LIMIT 5
    """)
    
    best_pairs = []
    for row in cursor.fetchall():
        best_pairs.append({
            'exchange': row[0],
            'symbol': row[1],
            'avg_spread': row[2],
            'max_spread': row[3],
            'samples': row[4]
        })
    
    # 2. 检查时间规律
    cursor.execute("""
        SELECT 
            strftime('%H', datetime(timestamp, 'unixepoch')) as hour,
            AVG(spread_pct) as avg_spread,
            COUNT(*) as samples
        FROM market_data 
        WHERE timestamp > strftime('%s', 'now', '-7 days')
        GROUP BY hour
        ORDER BY avg_spread DESC
        LIMIT 3
    """)
    
    peak_hours = []
    for row in cursor.fetchall():
        peak_hours.append({
            'hour': row[0],
            'avg_spread': row[1],
            'samples': row[2]
        })
    
    # 3. 检查不同币种的波动性
    cursor.execute("""
        SELECT symbol, 
               AVG(spread_pct) as avg_spread,
               MAX(spread_pct) as max_spread,
               MIN(spread_pct) as min_spread,
               COUNT(*) as samples
        FROM market_data 
        WHERE timestamp > strftime('%s', 'now', '-24 hours')
        GROUP BY symbol
        ORDER BY max_spread DESC
    """)
    
    volatility = []
    for row in cursor.fetchall():
        volatility.append({
            'symbol': row[0],
            'avg': row[1],
            'max': row[2],
            'min': row[3],
            'samples': row[4]
        })
    
    conn.close()
    
    return {
        'best_pairs': best_pairs,
        'peak_hours': peak_hours,
        'volatility': volatility
    }

def detect_new_patterns(current_patterns, known_patterns):
    """检测新发现的规律"""
    new_patterns = []
    
    # 检查最佳交易对是否有变化
    current_best = current_patterns['best_pairs']
    known_best = [p for p in known_patterns if p.get('type') == 'best_pair']
    
    for bp in current_best:
        if bp['avg_spread'] > 0.05:  # 高于平均的才算规律
            pattern_key = f"{bp['exchange']}_{bp['symbol']}_best"
            if not any(p.get('key') == pattern_key for p in known_best):
                new_patterns.append({
                    'type': 'best_pair',
                    'key': pattern_key,
                    'exchange': bp['exchange'],
                    'symbol': bp['symbol'],
                    'avg_spread': bp['avg_spread'],
                    'description': f"{bp['exchange']}的{bp['symbol']}价差最高(平均{bp['avg_spread']:.4f}%)"
                })
    
    # 检查高峰时段
    current_peak = current_patterns['peak_hours']
    known_peak = [p for p in known_patterns if p.get('type') == 'peak_hour']
    
    for ph in current_peak:
        if float(ph['avg_spread']) > 0.05:
            pattern_key = f"hour_{ph['hour']}_peak"
            if not any(p.get('key') == pattern_key for p in known_peak):
                new_patterns.append({
                    'type': 'peak_hour',
                    'key': pattern_key,
                    'hour': ph['hour'],
                    'avg_spread': ph['avg_spread'],
                    'description': f"{ph['hour']}点是价差高峰期(平均{ph['avg_spread']:.4f}%)"
                })
    
    return new_patterns

def main():
    log("=" * 60)
    log("🚀 QNT智能监控系统启动")
    log("=" * 60)
    
    state = load_state()
    last_check_time = 0
    daily_report_time = 0
    
    while True:
        try:
            current_time = time.time()
            
            # 每分钟检查价差和交易
            if current_time - last_check_time >= CHECK_INTERVAL:
                last_check_time = current_time
                
                # 检查价差
                spreads = check_spreads()
                if spreads:
                    max_spread = max(s[2] for s in spreads)
                    max_info = next(s for s in spreads if s[2] == max_spread)
                    
                    log(f"📊 最高价差: {max_spread:.4f}% ({max_info[0]} {max_info[1]})")
                    
                    # 如果有超阈值机会，立即通知
                    if max_spread > THRESHOLD:
                        opportunities = [(ex, sym, sp) for ex, sym, sp in spreads if sp > THRESHOLD]
                        msg = f"🔥 QNT交易机会！\n\n"
                        for ex, sym, sp in sorted(opportunities, key=lambda x: x[2], reverse=True)[:5]:
                            msg += f"• {ex} {sym}: {sp:.4f}%\n"
                        msg += f"\n阈值: {THRESHOLD}%\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        send_notification(msg)
                        state['last_trade_alert'] = current_time
                
                # 检查是否有新交易
                trades = check_trades()
                if trades:
                    msg = f"📈 QNT新交易执行！\n\n"
                    for t in trades[:5]:
                        profit = t['profit'] if t['profit'] else 0
                        msg += f"• {t['mode']} {t['symbol']}: 价差{t['spread']:.4f}%, 利润${profit:.4f}\n"
                    msg += f"\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    send_notification(msg)
                    state['last_trade_alert'] = current_time
            
            # 每小时分析一次规律
            if current_time - daily_report_time >= 3600:
                daily_report_time = current_time
                
                # 分析规律
                patterns = analyze_patterns()
                
                # 检测新规律
                new_patterns = detect_new_patterns(patterns, state.get('known_patterns', []))
                
                if new_patterns:
                    msg = f"💡 QNT发现新规律！\n\n"
                    for p in new_patterns[:3]:
                        msg += f"• {p['description']}\n"
                    msg += f"\n分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    send_notification(msg)
                    
                    # 更新已知规律
                    state['known_patterns'] = state.get('known_patterns', []) + new_patterns
                    state['last_pattern_discovery'] = current_time
                
                save_state(state)
            
            time.sleep(10)  # 短间隔检查，但只在特定事件时推送
            
        except KeyboardInterrupt:
            log("⏹️ 用户中断")
            break
        except Exception as e:
            log(f"❌ 监控异常: {e}")
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
