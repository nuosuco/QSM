#!/usr/bin/env python3
"""轻量级REST API服务器 - 提供字形识别服务"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os

os.chdir('/root/QSM/QLife/v0.0.3')

class GlyphHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {
                "service": "QEntL Glyph Recognition API",
                "status": "running",
                "model": "单层感知机 64→16",
                "weights": {
                    "state_1": "glyph_state_1_n16.w (1024权重)",
                    "state_101": "glyph_state_101_n16.w",
                    "state_202": "glyph_state_202_n16.w",
                    "state_303": "glyph_state_303_n16.w"
                },
                "accuracy": "16/16 = 100%",
                "data_file": "yi_glyph_16_v3.data"
            }
            self.wfile.write(json.dumps(response).encode())
        elif self.path.startswith('/weights/'):
            # 返回权重文件
            state_id = self.path.split('/')[-1]
            weight_file = f'qdfs/ns/models/glyph_state_{state_id}_n16.w'
            if os.path.exists(weight_file):
                with open(weight_file) as f:
                    weights = f.read().strip().split('\n')
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"state": state_id, "weights": [int(w) for w in weights]}).encode())
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'{"error": "weight file not found"}')
        elif self.path.startswith('/glyphs/'):
            # 返回16个字形数据
            data_file = 'qdfs/ns/data/yi_glyph_16_v3.data'
            if os.path.exists(data_file):
                with open(data_file) as f:
                    lines = f.readlines()
                glyphs = []
                for line in lines:
                    parts = line.strip().split(':')
                    label = int(parts[0])
                    pixels = [int(p) for p in parts[1].split(',')]
                    code = parts[2]
                    glyphs.append({"label": label, "pixels": pixels, "code": code})
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(glyphs).encode())
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'{"error": "data file not found"}')
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'{"error": "not found"}')
    
    def log_message(self, format, *args):
        pass  # 静默日志

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 8765), GlyphHandler)
    print("QEntL Glyph API 运行在 http://0.0.0.0:8765/")
    print("端点:")
    print("  GET / - 服务信息")
    print("  GET /weights/1 - 态1权重")
    print("  GET /glyphs/ - 16个字形数据")
    server.serve_forever()