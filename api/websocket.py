"""
QNT WebSocket 实时推送
"""
from flask_socketio import SocketIO, emit
import threading
import time


class QNTWebSocket:
    """QNT WebSocket 服务"""
    
    def __init__(self, app):
        self.socketio = SocketIO(app, cors_allowed_origins="*")
        self.clients = []
        self._start_background()
    
    def _start_background(self):
        """后台推送行情"""
        def push_loop():
            while True:
                time.sleep(1)
                # 推送心跳
                self.socketio.emit('heartbeat', {'time': time.time()})
        
        t = threading.Thread(target=push_loop, daemon=True)
        t.start()
    
    def on_connect(self):
        self.clients.append(self.socketio.session_id)
        emit('connected', {'clients': len(self.clients)})
    
    def on_disconnect(self):
        if self.socketio.session_id in self.clients:
            self.clients.remove(self.socketio.session_id)
    
    def broadcast_trade(self, trade_data):
        """广播成交信息"""
        self.socketio.emit('trade', trade_data)
    
    def broadcast_orderbook(self, orderbook_data):
        """广播订单簿"""
        self.socketio.emit('orderbook', orderbook_data)


def create_socketio(app):
    """创建SocketIO实例"""
    socketio = SocketIO(app, cors_allowed_origins="*")
    
    @socketio.on('connect')
    def handle_connect():
        emit('connected', {'status': 'ok'})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        pass
    
    return socketio
