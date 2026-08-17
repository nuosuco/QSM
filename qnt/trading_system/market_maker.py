"""
QNT v3 - 做市策略引擎
阈值: 0.12%（成本线），Post-Only瞬间挂单瞬间平仓
"""
import time
import sqlite3
import json
import ccxt
from datetime import datetime
from typing import Dict, List, Optional
import os

# 成本结构
MAKER_FEE = 0.0004   # 0.04%
SLIPPAGE = 0.0002    # 0.02%
COST_PCT = (MAKER_FEE + SLIPPAGE) * 2 * 100  # 0.12%

# 配置
THRESHOLD_PCT = 0.12  # 价差阈值（成本线）
MIN_PROFIT_PCT = 0.02  # 最小净利润（安全边际）
SCAN_INTERVAL = 2  # 扫描间隔（秒）
POSITION_SIZE_USDT = 50  # 单笔仓位


class MarketMaker:
    """做市策略引擎"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_db()
        
        # 交易所连接
        self.exchange = None
        self._connect_exchange()
        
        self.running = False
        self.trade_count = 0
        self.profit_count = 0
        self.loss_count = 0
        
    def _init_db(self):
        """初始化数据库表"""
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                symbol TEXT,
                exchange TEXT,
                spread_pct REAL,
                side TEXT,
                perp_price REAL,
                spot_price REAL,
                amount REAL,
                cost REAL,
                fee REAL,
                pnl REAL,
                pnl_pct REAL,
                status TEXT,
                order_id TEXT
            )
        ''')
        self.conn.commit()
    
    def _connect_exchange(self):
        """连接Bitget测试网"""
        try:
            self.exchange = ccxt.bitget({
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'swap',  # 永续合约
                    'quoteSwapAmount': True,  # 用USDT计价
                },
                'apiKey': os.getenv('BITGET_API_KEY', ''),
                'secret': os.getenv('BITGET_API_SECRET', ''),
                'password': os.getenv('BITGET_API_PASSPHRASE', ''),
            })
            print(f"✅ 已连接Bitget测试网")
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            self.exchange = None
    
    def get_spread(self, symbol: str) -> Optional[Dict]:
        """获取永续和现货价差"""
        try:
            # 永续合约
            swap = self.exchange.fetch_ticker(symbol.replace('/USDT', '/USDT:USDT'))
            perp_price = swap['last']
            
            # 现货
            spot = self.exchange.fetch_ticker(symbol)
            spot_price = spot['last']
            
            # 价差（永续溢价）
            spread_pct = (perp_price - spot_price) / spot_price * 100
            
            return {
                'symbol': symbol,
                'perp_price': perp_price,
                'spot_price': spot_price,
                'spread_pct': spread_pct,
                'timestamp': time.time()
            }
        except Exception as e:
            print(f"❌ 获取价差失败 {symbol}: {e}")
            return None
    
    def place_post_only_order(self, symbol: str, side: str, amount: float, price: float):
        """挂Post-Only订单（不做Taker）"""
        try:
            # 先获取订单簿确认价格
            ob = self.exchange.fetch_order_book(symbol.replace('/USDT:USDT', '/USDT'), limit=5)
            
            if side == 'buy':
                # 买盘挂单（Bid）- 低于当前买价
                buy_price = ob['bids'][0][0] * 0.999 if ob['bids'] else price
                order = self.exchange.create_order(
                    symbol=symbol.replace('/USDT', '/USDT:USDT'),
                    type='limit',
                    side='buy',
                    amount=amount,
                    price=buy_price,
                    params={'timeInForce': 'postOnly'}
                )
            else:
                # 卖盘挂单（Ask）- 高于当前卖价
                ask_price = ob['asks'][0][0] * 1.001 if ob['asks'] else price
                order = self.exchange.create_order(
                    symbol=symbol.replace('/USDT', '/USDT:USDT'),
                    type='limit',
                    side='sell',
                    amount=amount,
                    price=ask_price,
                    params={'timeInForce': 'postOnly'}
                )
            
            return order
        except ccxt.InsufficientFunds:
            print(f"⚠️ 资金不足")
            return None
        except Exception as e:
            print(f"❌ 下单失败: {e}")
            return None
    
    def execute_market_maker_trade(self, data: Dict):
        """执行做市交易"""
        symbol = data['symbol']
        spread = data['spread_pct']
        perp_price = data['perp_price']
        spot_price = data['spot_price']
        
        # 计算实际成交价（考虑手续费和滑点）
        actual_spread = spread - COST_PCT  # 扣除成本后的净利
        
        if actual_spread < MIN_PROFIT_PCT:
            return None  # 利润太低，不交易
        
        # 计算仓位
        cost = POSITION_SIZE_USDT
        amount_perp = cost / perp_price
        
        # 方向：永续溢价高 → 买永续卖现货；永续折价高 → 卖永续买现货
        if spread > 0:
            # 永续溢价 → 买永续 + 卖现货
            side_perp = 'buy'
            side_spot = 'sell'
        else:
            # 永续折价 → 卖永续 + 买现货
            side_perp = 'sell'
            side_spot = 'buy'
        
        # 尝试下单
        print(f"\n📊 {symbol} 价差{spread:.4f}%，净利{actual_spread:.4f}%")
        print(f"   永续${perp_price:.2f} vs 现货${spot_price:.2f}")
        
        # 永续合约下单
        order_perp = self.place_post_only_order(
            symbol.replace('/USDT:USDT', '/USDT'),
            side_perp,
            amount_perp,
            perp_price
        )
        
        # 现货下单
        order_spot = self.place_post_only_order(
            symbol,
            side_spot,
            amount_perp,
            spot_price
        )
        
        # 记录结果
        if order_perp or order_spot:
            trade = {
                'timestamp': time.time(),
                'symbol': symbol,
                'exchange': 'bitget',
                'spread_pct': spread,
                'side': side_perp,
                'perp_price': perp_price,
                'spot_price': spot_price,
                'amount': amount_perp,
                'cost': cost,
                'fee': cost * COST_PCT / 100,
                'pnl': cost * actual_spread / 100,
                'pnl_pct': actual_spread,
                'status': 'pending',
                'order_id': order_perp.get('id') if order_perp else None
            }
            
            self._save_trade(trade)
            self.trade_count += 1
            return trade
        
        return None
    
    def _save_trade(self, trade: Dict):
        """保存交易记录"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO market_trades
                (timestamp, symbol, exchange, spread_pct, side, perp_price, spot_price,
                 amount, cost, fee, pnl, pnl_pct, status, order_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                trade['timestamp'],
                trade['symbol'],
                trade['exchange'],
                trade['spread_pct'],
                trade['side'],
                trade['perp_price'],
                trade['spot_price'],
                trade['amount'],
                trade['cost'],
                trade['fee'],
                trade['pnl'],
                trade['pnl_pct'],
                trade['status'],
                trade['order_id']
            ))
            self.conn.commit()
            print(f"   💾 已保存交易记录")
        except Exception as e:
            print(f"   ⚠️ 保存失败: {e}")
    
    def run(self, symbols: List[str] = None):
        """运行做市引擎"""
        if not symbols:
            symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT', 'XRP/USDT']
        
        self.running = True
        print(f"\n🚀 QNT做市引擎启动")
        print(f"   阈值: >{THRESHOLD_PCT}%（成本线{COST_PCT:.3f}%）")
        print(f"   最小净利: >{MIN_PROFIT_PCT}%")
        print(f"   仓位: ${POSITION_SIZE_USDT}/笔")
        print(f"   扫描间隔: {SCAN_INTERVAL}秒")
        print()
        
        last_scan = 0
        
        while self.running:
            try:
                current_time = time.time()
                
                # 频率限制
                if current_time - last_scan < SCAN_INTERVAL:
                    time.sleep(0.5)
                    continue
                
                last_scan = current_time
                
                print(f"\n{'='*60}")
                print(f"📡 扫描时间: {datetime.now().strftime('%H:%M:%S')}")
                print(f"{'='*60}")
                
                for symbol in symbols:
                    data = self.get_spread(symbol)
                    if not data:
                        continue
                    
                    spread = data['spread_pct']
                    actual_profit = spread - COST_PCT
                    
                    print(f"\n{symbol}:")
                    print(f"  永续: ${data['perp_price']:.2f}")
                    print(f"  现货: ${data['spot_price']:.2f}")
                    print(f"  价差: {spread:.4f}%")
                    print(f"  净利: {actual_profit:+.4f}%")
                    
                    if actual_profit >= MIN_PROFIT_PCT:
                        print(f"  ✅ 触发做市！")
                        trade = self.execute_market_maker_trade(data)
                        if trade:
                            self.profit_count += 1
                    else:
                        print(f"  ❌ 利润不足，跳过")
                
                # 打印统计
                print(f"\n📊 当前统计:")
                print(f"   总交易: {self.trade_count}笔")
                print(f"   盈利信号: {self.profit_count}次")
                print(f"   亏损信号: {self.loss_count}次")
                
            except KeyboardInterrupt:
                print("\n🛑 引擎停止")
                break
            except Exception as e:
                print(f"⚠️ 运行时错误: {e}")
                time.sleep(5)
    
    def stop(self):
        """停止引擎"""
        self.running = False
        if self.exchange:
            self.exchange.close()
        if self.conn:
            self.conn.close()
    
    def get_stats(self) -> Dict:
        """获取统计数据"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*), SUM(pnl), AVG(pnl_pct) FROM market_trades WHERE status='completed'")
            row = cursor.fetchone()
            
            return {
                'total_trades': row[0] or 0,
                'total_pnl': row[1] or 0,
                'avg_profit_pct': row[2] or 0
            }
        except:
            return {'total_trades': 0, 'total_pnl': 0, 'avg_profit_pct': 0}


if __name__ == '__main__':
    engine = MarketMaker('/root/SOM/data/trading_system/adaptive.db')
    engine.run()
