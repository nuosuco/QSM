"""
QNT API WebSocket实时推送
"""
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Callable, Any


class WebSocketManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        self.clients: List[Callable] = []
        self._handlers: Dict[str, Callable] = {}
        self._running = False
    
    def connect(self, client: Callable):
        """注册客户端"""
        self.clients.append(client)
        print(f"📡 New WebSocket client connected ({len(self.clients)} total)")
    
    def disconnect(self, client: Callable):
        """取消注册客户端"""
        if client in self.clients:
            self.clients.remove(client)
            print(f"📡 WebSocket client disconnected ({len(self.clients)} total)")
    
    async def send(self, data: Dict[str, Any]):
        """发送消息"""
        message = json.dumps(data, default=str)
        for client in self.clients:
            try:
                await client(message)
            except Exception as e:
                print(f"⚠️ WebSocket send error: {e}")
    
    def broadcast(self, event: str, payload: Dict[str, Any]):
        """广播事件"""
        message = json.dumps({
            'event': event,
            'timestamp': datetime.now().isoformat(),
            'payload': payload
        }, default=str)
        
        for client in self.clients:
            try:
                asyncio.create_task(client(message))
            except Exception as e:
                print(f"⚠️ WebSocket broadcast error: {e}")
    
    def register_handler(self, event: str, handler: Callable):
        """注册事件处理器"""
        self._handlers[event] = handler
    
    def handle_event(self, event: str, data: Dict[str, Any]):
        """分发事件"""
        if event in self._handlers:
            self._handlers[event](data)


# 全局WebSocket管理器
ws_manager = WebSocketManager()


class EventBus:
    """事件总线 - 用于模块间通信"""
    
    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}
    
    def subscribe(self, event: str, callback: Callable):
        """订阅事件"""
        if event not in self._listeners:
            self._listeners[event] = []
        self._listeners[event].append(callback)
    
    def publish(self, event: str, data: Dict[str, Any] = None):
        """发布事件"""
        if event in self._listeners:
            for callback in self._listeners[event]:
                try:
                    callback(data)
                except Exception as e:
                    print(f"⚠️ Event handler error: {e}")
    
    def unsubscribe(self, event: str, callback: Callable):
        """取消订阅"""
        if event in self._listeners:
            if callback in self._listeners[event]:
                self._listeners[event].remove(callback)


# 全局事件总线
event_bus = EventBus()
