"""
QNT WebSocket测试
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from api.websocket import WebSocketManager, QNTEventBus, EventBroker


class TestEventBroker:
    """事件广播器测试"""
    
    def test_subscribe_and_publish(self):
        """订阅和发布测试"""
        broker = EventBroker()
        received = []
        
        broker.subscribe('test_event', lambda data: received.append(data))
        broker.publish('test_event', {'key': 'value'})
        
        assert len(received) == 1
        assert received[0] == {'key': 'value'}
    
    def test_unsubscribe(self):
        """取消订阅测试"""
        broker = EventBroker()
        received = []
        
        def callback(data):
            received.append(data)
        
        broker.subscribe('test_event', callback)
        broker.unsubscribe('test_event', callback)
        broker.publish('test_event', {'key': 'value'})
        
        assert len(received) == 0
    
    def test_multiple_subscribers(self):
        """多订阅者测试"""
        broker = EventBroker()
        results = [[], []]
        
        broker.subscribe('event', lambda d: results[0].append(d))
        broker.subscribe('event', lambda d: results[1].append(d))
        
        broker.publish('event', {'test': 1})
        
        assert len(results[0]) == 1
        assert len(results[1]) == 1


@pytest.mark.asyncio
class TestWebSocketManager:
    """WebSocket管理器测试"""
    
    def test_connect_and_disconnect(self):
        """连接和断开测试"""
        manager = WebSocketManager()
        ws = AsyncMock()
        
        manager.connect('client1', ws)
        assert 'client1' in manager._connections
        
        manager.disconnect('client1')
        assert 'client1' not in manager._connections
    
    @pytest.mark.asyncio
    async def test_send_message(self):
        """发送消息测试"""
        manager = WebSocketManager()
        ws = AsyncMock()
        ws.send_json = AsyncMock()
        
        manager.connect('client1', ws)
        await manager.send('client1', {'event': 'test', 'data': {'x': 1}})
        
        ws.send_json.assert_called_once()
    
    def test_subscribe_event(self):
        """订阅事件测试"""
        manager = WebSocketManager()
        ws = AsyncMock()
        
        manager.connect('client1', ws)
        manager.subscribe('client1', 'blockchain.new_block')
        
        assert 'blockchain.new_block' in manager._connections['client1']['subscribed_events']
    
    def test_get_stats(self):
        """获取统计测试"""
        manager = WebSocketManager()
        ws1 = AsyncMock()
        ws2 = AsyncMock()
        
        manager.connect('client1', ws1)
        manager.connect('client2', ws2)
        
        stats = manager.get_stats()
        assert stats['total_connections'] == 2


@pytest.mark.asyncio
class TestQNTEventBus:
    """事件总线测试"""
    
    @pytest.mark.asyncio
    async def test_register_and_handle(self):
        """注册和处理测试"""
        ws_manager = WebSocketManager()
        bus = QNTEventBus(ws_manager)
        
        result = []
        bus.register('trade.executed', lambda data: result.append(data))
        
        await bus.handle('trade.executed', {'symbol': 'BTC/USDT', 'price': 50000})
        
        assert len(result) == 1
        assert result[0]['symbol'] == 'BTC/USDT'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
