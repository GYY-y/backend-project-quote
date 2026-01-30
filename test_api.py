#!/usr/bin/env python3
"""
API测试脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager
import json

def test_api_endpoints():
    """测试API端点"""
    print("=== API功能测试 ===")
    
    db = DatabaseManager()
    
    # 测试今日金句
    print("\n--- 今日金句 ---")
    try:
        quote = db.get_today_quote()
        if quote:
            print(f"✅ 获取今日金句成功")
            print(f"   内容: {quote['content'][:50]}...")
            print(f"   来源: {quote['source']}")
        else:
            print("❌ 今日金句为空")
    except Exception as e:
        print(f"❌ 获取今日金句失败: {e}")
    
    # 测试历史金句
    print("\n--- 历史金句 ---")
    try:
        result = db.get_history_quotes(page=1, limit=5)
        quotes = result['quotes']
        pagination = result['pagination']
        
        print(f"✅ 获取历史金句成功")
        print(f"   总数: {pagination['total']}")
        print(f"   当前页: {pagination['page']}")
        print(f"   返回数量: {len(quotes)}")
        
        if quotes:
            print(f"   最新金句: {quotes[0]['content'][:30]}...")
    except Exception as e:
        print(f"❌ 获取历史金句失败: {e}")
    
    # 测试搜索功能
    print("\n--- 搜索功能 ---")
    try:
        result = db.search_quotes(query="奋斗", page=1, limit=3)
        quotes = result['quotes']
        pagination = result['pagination']
        
        print(f"✅ 搜索功能正常")
        print(f"   搜索'奋斗'找到: {pagination['total']} 条")
        print(f"   返回数量: {len(quotes)}")
        
        if quotes:
            print(f"   示例: {quotes[0]['content'][:40]}...")
    except Exception as e:
        print(f"❌ 搜索功能失败: {e}")
    
    # 测试统计信息
    print("\n--- 统计信息 ---")
    try:
        stats = db.get_stats()
        print(f"✅ 统计信息获取成功")
        print(f"   总金句数: {stats['total_quotes']}")
        print(f"   今日金句数: {stats['today_quotes']}")
        print(f"   来源统计: {stats['source_stats']}")
    except Exception as e:
        print(f"❌ 统计信息获取失败: {e}")

def test_fastapi_app():
    """测试FastAPI应用"""
    print("\n=== FastAPI应用测试 ===")
    
    try:
        from main import app
        print("✅ FastAPI应用导入成功")
        
        # 检查路由
        routes = []
        for route in app.routes:
            if hasattr(route, 'path'):
                routes.append(f"{route.methods} {route.path}")
        
        print(f"✅ 注册路由数量: {len(routes)}")
        for route in routes[:5]:  # 显示前5个路由
            print(f"   {route}")
            
    except Exception as e:
        print(f"❌ FastAPI应用测试失败: {e}")

if __name__ == "__main__":
    test_api_endpoints()
    test_fastapi_app()