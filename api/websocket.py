"""
QNT WebSocket实时推送服务
"""
import asyncio
import json
import time
from typing import Dict, List, Any, Optional, Callable
from collections import defaultdict
import threading


class EventBroker:
    """事件广播器"""
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._lock = threading.Lock()
    
    def subscribe(self, event: str, callback: Callable):
        """订阅事件"""
        with self._lock:
            self._subscribers[event].append(callback)
    
    def unsubscribe(self, event: str, callback: Callable):
        """取消订阅"""
        with self._lock:
            if event in self._subscribers:
                self._subscribers[event].remove(callback)
    
    def publish(self, event: str, data: Any):
        """发布事件"""
        with self._lock:
            callbacks = list(self._subscribers.get(event, []))
        
        for callback in callbacks:
            try:
                callback(data)
            except Exception as e:
                print(f"⚠️ Event callback error: {e}")


class WebSocketManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        self._connections: Dict[str, Any] = {}
        self._event_broker = EventBroker()
        self._lock = threading.Lock()
    
    def connect(self, client_id: str, websocket):
        """连接WebSocket"""
        with self._lock:
            self._connections[client_id] = {
                'websocket': websocket,
                'connected_at': time.time(),
                'subscribed_events': set()
            }
        self._event_broker.publish('connection', {'id': client_id, 'status': 'connected'})
    
    def disconnect(self, client_id: str):
        """断开WebSocket"""
        with self._lock:
            if client_id in self._connections:
                del self._connections[client_id]
        self._event_broker.publish('connection', {'id': client_id, 'status': 'disconnected'})
    
    def subscribe(self, client_id: str, event: str):
        """客户端订阅事件"""
        with self._lock:
            if client_id in self._connections:
                self._connections[client_id]['subscribed_events'].add(event)
    
    async def send(self, client_id: str, data: Dict):
        """发送数据给客户端"""
        with self._lock:
            conn = self._connections.get(client_id)
        
        if conn:
            try:
                await conn['websocket'].send_json(data)
            except Exception:
                self.disconnect(client_id)
    
    async def broadcast(self, event: str, data: Dict):
        """广播事件给所有订阅者"""
        with self._lock:
            subscribers = set()
            for client_id, conn in self._connections.items():
                if event in conn['subscribed_events']:
                    subscribers.add(client_id)
        
        for client_id in subscribers:
            await self.send(client_id, {'event': event, 'data': data})
    
    def get_stats(self) -> Dict[str, Any]:
        """获取WebSocket统计"""
        with self._lock:
            return {
                'total_connections': len(self._connections),
                'connections': list(self._connections.keys())
            }


class QNTEventBus:
    """QNT事件总线"""
    
    def __init__(self, ws_manager: WebSocketManager):
        self.ws_manager = ws_manager
        self._handlers: Dict[str, Callable] = {}
    
    def register(self, event: str, handler: Callable):
        """注册事件处理器"""
        self._handlers[event] = handler
    
    async def handle(self, event: str, data: Any):
        """处理事件"""
        if event in self._handlers:
            handler = self._handlers[event]
            # 支持同步和异步处理器
            if asyncio.iscoroutinefunction(handler):
                await handler(data)
            else:
                result = handler(data)
                if asyncio.iscoroutine(result):
                    await result
        
        # 广播到WebSocket
        await self.ws_manager.broadcast(event, data)


# 全局实例
ws_manager = WebSocketManager()
event_bus = QNTEventBus(ws_manager)
