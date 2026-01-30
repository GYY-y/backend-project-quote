#!/usr/bin/env python3
"""
爬虫测试脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crawlers.crawler_manager import CrawlerManager
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_crawler_manager():
    """测试爬虫管理器"""
    print("=== 励志金句爬虫测试 ===")
    
    manager = CrawlerManager()
    
    # 显示可用爬虫
    sources = manager.get_available_sources()
    print(f"可用爬虫来源: {', '.join(sources)}")
    
    # 测试单个爬虫
    for source in sources:
        print(f"\n--- 测试 {source} 爬虫 ---")
        try:
            result = manager.test_crawler(source)
            if result['success']:
                print(f"✅ {source} 测试成功")
                print(f"   找到金句: {result['quotes_found']} 条")
                if result['sample_quotes']:
                    print("   示例金句:")
                    for i, quote in enumerate(result['sample_quotes'][:2], 1):
                        print(f"   {i}. {quote.get('content', '')[:50]}...")
            else:
                print(f"❌ {source} 测试失败: {result.get('error', '未知错误')}")
        except Exception as e:
            print(f"❌ {source} 测试异常: {e}")
    
    # 获取统计信息
    print(f"\n--- 数据库统计信息 ---")
    try:
        stats = manager.get_crawl_stats()
        print(f"总金句数: {stats['total_quotes']}")
        print(f"今日金句数: {stats['today_quotes']}")
        print(f"来源统计: {stats['source_stats']}")
    except Exception as e:
        print(f"获取统计信息失败: {e}")

def test_single_crawl():
    """测试单次爬取"""
    print("\n=== 执行单次爬取测试 ===")
    
    manager = CrawlerManager()
    
    # 只测试人民网
    source = "人民网"
    print(f"开始爬取 {source}...")
    
    try:
        count = manager.crawl_single_source(source)
        print(f"✅ {source} 爬取完成，新增 {count} 条金句")
    except Exception as e:
        print(f"❌ {source} 爬取失败: {e}")

if __name__ == "__main__":
    # 选择测试模式
    if len(sys.argv) > 1 and sys.argv[1] == "crawl":
        test_single_crawl()
    else:
        test_crawler_manager()