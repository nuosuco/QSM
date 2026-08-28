#!/usr/bin/env python3
"""QNT自动监控 - 有交易机会时主动推送"""
import os
import sys
import time
import subprocess
import ccxt
from datetime import datetime

THRESHOLD = 0.17
CHECK_INTERVAL = 60  # 每60秒检查一次
LOG_FILE = "/root/SOM/qnt/qnt_auto_monitor.log"

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

def check_spreads():
    """检查所有平台的所有交易对价差"""
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
    
    symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT', 'XRP/USDT', 'DOGE/USDT']
    
    opportunities = []
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
                
                if sp > THRESHOLD:
                    opportunities.append((ex_name, sym, sp))
            except Exception as e:
                pass
    
    return all_spreads, opportunities

def main():
    log("=" * 60)
    log("🚀 QNT自动监控系统启动")
    log("=" * 60)
    
    last_alert_spread = 0
    
    while True:
        try:
            all_spreads, opportunities = check_spreads()
            
            if all_spreads:
                max_spread = max(s[2] for s in all_spreads)
                max_info = next(s for s in all_spreads if s[2] == max_spread)
                
                log(f"📊 最高价差: {max_spread:.4f}% ({max_info[0]} {max_info[1]})")
                
                # 如果有超阈值机会，立即通知
                if opportunities:
                    log(f"🔥 发现{len(opportunities)}个超阈值机会！")
                    
                    msg = "🔥 QNT价差机会！\n\n"
                    for ex, sym, sp in sorted(opportunities, key=lambda x: x[2], reverse=True)[:5]:
                        msg += f"• {ex} {sym}: {sp:.4f}%\n"
                    msg += f"\n阈值: {THRESHOLD}%\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    
                    send_notification(msg)
                    last_alert_spread = max_spread
                
                # 每10分钟发送一次常规报告（如果没有新机会）
                elif max_spread > last_alert_spread * 1.5 and int(time.time()) % 600 < 5:
                    msg = f"📊 QNT监控报告\n\n"
                    msg += f"最高价差: {max_spread:.4f}%\n"
                    msg += f"阈值: {THRESHOLD}%\n"
                    msg += f"差距: {(THRESHOLD/max_spread-1)*100:.1f}%\n"
                    msg += f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    send_notification(msg)
                    last_alert_spread = max_spread
            
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            log("⏹️ 用户中断")
            break
        except Exception as e:
            log(f"❌ 监控异常: {e}")
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
