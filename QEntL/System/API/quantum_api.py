#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
量子模拟器API - Web API接口
"""

import json
import math
import random
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

class QuantumSimulator:
    """简易量子模拟器"""

    def __init__(self, num_qubits=4):
        self.num_qubits = num_qubits
        self.state = self._zero_state(num_qubits)

    def _zero_state(self, n):
        """创建|0...0⟩态"""
        state = [0] * (2 ** n)
        state[0] = 1
        return state

    def hadamard(self, qubit):
        """Hadamard门"""
        new_state = self.state.copy()
        h = 1 / math.sqrt(2)

        for i in range(len(self.state)):
            if (i >> qubit) & 1 == 0:
                j = i | (1 << qubit)
                new_state[i] = h * self.state[i] + h * self.state[j]
                new_state[j] = h * self.state[i] - h * self.state[j]

        self.state = new_state
        return self.state

    def cnot(self, control, target):
        """CNOT门"""
        new_state = self.state.copy()

        for i in range(len(self.state)):
            if (i >> control) & 1 == 1:
                j = i ^ (1 << target)
                new_state[i] = self.state[j]
                new_state[j] = self.state[i]

        self.state = new_state
        return self.state

    def measure(self):
        """测量"""
        probs = [abs(x)**2 for x in self.state]
        r = random.random()
        cumulative = 0
        for i, p in enumerate(probs):
            cumulative += p
            if r <= cumulative:
                return i
        return len(probs) - 1

    def get_probabilities(self):
        """获取概率分布"""
        return [abs(x)**2 for x in self.state]

class QuantumAPIHandler(BaseHTTPRequestHandler):
    """量子API处理器"""

    def log_message(self, format, *args):
        # 静默日志
        pass

    def send_json(self, data):
        """发送JSON响应"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

    def do_GET(self):
        """处理GET请求"""
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)

        if path == '/api/quantum/status':
            self.send_json({
                'status': 'running',
                'max_qubits': 8,
                'available_gates': ['H', 'X', 'Y', 'Z', 'CNOT', 'T', 'S'],
                'timestamp': datetime.now().isoformat()
            })

        elif path == '/api/quantum/bell':
            sim = QuantumSimulator(2)
            sim.hadamard(0)
            sim.cnot(0, 1)
            probs = sim.get_probabilities()
            measurements = [sim.measure() for _ in range(100)]

            self.send_json({
                'state': 'Bell',
                'probabilities': probs,
                'measurements': measurements[:10],
                'correlation': 'perfect_entanglement'
            })

        elif path == '/api/quantum/ghz':
            num_qubits = int(params.get('qubits', [3])[0])
            sim = QuantumSimulator(num_qubits)

            for i in range(num_qubits):
                sim.hadamard(i)

            for i in range(1, num_qubits):
                sim.cnot(0, i)

            probs = sim.get_probabilities()

            self.send_json({
                'state': 'GHZ',
                'num_qubits': num_qubits,
                'probabilities': probs,
                'entanglement': 'maximal'
            })

        elif path == '/api/quantum/random':
            num_bits = int(params.get('bits', [8])[0])
            sim = QuantumSimulator(1)

            bits = []
            for _ in range(num_bits):
                sim = QuantumSimulator(1)
                sim.hadamard(0)
                bits.append(sim.measure())

            self.send_json({
                'num_bits': num_bits,
                'random_bits': bits,
                'random_hex': hex(int(''.join(map(str, bits)), 2))
            })

        else:
            self.send_json({'error': 'Unknown endpoint', 'path': path})

    def do_POST(self):
        """处理POST请求"""
        parsed = urlparse(self.path)
        path = parsed.path

        if path == '/api/quantum/circuit':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode()
            data = json.loads(body)

            num_qubits = data.get('qubits', 2)
            gates = data.get('gates', [])

            sim = QuantumSimulator(num_qubits)

            for gate in gates:
                gate_type = gate.get('type')
                if gate_type == 'H':
                    sim.hadamard(gate.get('target', 0))
                elif gate_type == 'CNOT':
                    sim.cnot(gate.get('control', 0), gate.get('target', 1))

            probs = sim.get_probabilities()
            measurement = sim.measure()

            self.send_json({
                'status': 'executed',
                'final_state': sim.state,
                'probabilities': probs,
                'measurement': measurement
            })

        else:
            self.send_json({'error': 'Unknown endpoint'})

def main():
    print("=" * 60)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 量子模拟器API启动")
    print("=" * 60)

    server = HTTPServer(('0.0.0.0', 8765), QuantumAPIHandler)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 服务运行在端口 8765")
    print("API端点:")
    print("  GET /api/quantum/status - 状态检查")
    print("  GET /api/quantum/bell - Bell态")
    print("  GET /api/quantum/ghz?qubits=N - GHZ态")
    print("  GET /api/quantum/random?bits=N - 量子随机数")
    print("  POST /api/quantum/circuit - 执行量子电路")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 服务停止")

if __name__ == "__main__":
    main()
