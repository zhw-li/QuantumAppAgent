#!/usr/bin/env python3
"""QLSTM 前端本地开发服务器 — 启动脚本"""

import http.server
import socketserver
import os
import sys

PORT = 3000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        # 允许跨域（开发时便于调试）
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        super().end_headers()


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    with socketserver.TCPServer(('', port), Handler) as httpd:
        print(f'🚀 QLSTM 前端开发服务器已启动')
        print(f'   地址: http://localhost:{port}')
        print(f'   目录: {DIRECTORY}')
        print(f'   后端: http://localhost:8001')
        print(f'\n   按 Ctrl+C 停止服务器')
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('\n👋 服务器已停止')
