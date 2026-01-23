#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask 应用的生产环境静态文件服务配置
当 Dockerfile 构建前端后，使用这个配置来服务静态文件
"""
import os
from flask import send_from_directory

def configure_static_files(app):
    """
    配置 Flask 服务前端静态文件
    
    Args:
        app: Flask 应用实例
    """
    # 获取前端构建目录
    frontend_dist = os.path.join(
        os.path.dirname(__file__), 
        'frontend', 
        'dist'
    )
    
    if not os.path.exists(frontend_dist):
        print(f"⚠️  Warning: Frontend dist folder not found at {frontend_dist}")
        print("   Run 'npm run build' in memdemo/frontend/ to build the frontend")
        return
    
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_frontend(path):
        """服务前端静态文件"""
        # API 路由已经在 app.py 中定义，不会到这里
        if path and os.path.exists(os.path.join(frontend_dist, path)):
            return send_from_directory(frontend_dist, path)
        else:
            # SPA fallback: 所有其他路由返回 index.html
            return send_from_directory(frontend_dist, 'index.html')
    
    print(f"✅ Static files serving enabled from {frontend_dist}")

