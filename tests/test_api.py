"""
QNT API接口测试
"""
import pytest
import asyncio
from unittest.mock import MagicMock


def test_websocket_manager():
    """测试WebSocket管理器"""
    from api.websocket import WebSocketManager
    
    ws = WebSocketManager()
    
    # 使用AsyncMock模拟websocket
    from unittest.mock import AsyncMock
    mock_ws = AsyncMock()
    ws.connect('test_client', mock_ws)
    
    assert 'test_client' in ws._connections
    print(f"✅ WebSocketManager: {len(ws._connections)} clients")


def test_event_bus():
    """测试事件总线"""
    from api.websocket import QNTEventBus, WebSocketManager
    
    ws_mgr = WebSocketManager()
    bus = QNTEventBus(ws_mgr)
    events = []
    
    def handler(data):
        events.append(data)
    
    bus.register('trade', handler)
    import asyncio
    asyncio.run(bus.handle('trade', {'price': 100}))
    asyncio.run(bus.handle('trade', {'price': 101}))
    
    assert len(events) == 2
    assert events[0]['price'] == 100
    print(f"✅ QNTEventBus: {len(events)} events handled")


def test_market_feed():
    """测试市场数据生成器"""
    from market.feeds import MarketDataGenerator, OrderBookSimulator
    
    gen = MarketDataGenerator(initial_price=100.0, volatility=0.01)
    
    # 生成多轮数据
    for _ in range(10):
        data = gen.generate_tick()
        assert data.price > 0
        assert data.bid < data.ask
    
    history = gen.get_history(5)
    assert len(history) == 5
    
    latest = gen.get_latest()
    assert latest is not None
    print(f"✅ MarketDataGenerator: price={latest.price:.2f}, generated={len(gen._history)} ticks")


def test_orderbook_simulator():
    """测试订单簿模拟器"""
    from market.feeds import OrderBookSimulator
    from market.feeds import MarketDataGenerator
    
    gen = MarketDataGenerator(initial_price=100.0)
    ob = OrderBookSimulator()
    
    for _ in range(5):
        data = gen.generate_tick()
        ob.update(data)
    
    best_bid = ob.get_best_bid()
    best_ask = ob.get_best_ask()
    spread = ob.get_spread()
    
    assert best_bid is not None
    assert best_ask is not None
    assert spread > 0
    print(f"✅ OrderBookSimulator: bid={best_bid:.2f}, ask={best_ask:.2f}, spread={spread:.4f}")


def test_feed_manager():
    """测试行情流管理器"""
    from market.feeds import FeedManager
    
    feed = FeedManager()
    assert feed.market_data is not None
    assert feed.order_book is not None
    print("✅ FeedManager initialized")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
