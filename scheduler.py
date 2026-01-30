#!/usr/bin/env python3
"""
定时任务调度器
"""

import os
import sys
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import asyncio

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crawlers.crawler_manager import CrawlerManager
from database.db_manager import DatabaseManager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class QuoteScheduler:
    """金句爬取调度器"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.crawler_manager = CrawlerManager()
        self.db_manager = DatabaseManager()
        
    async def daily_crawl_job(self):
        """每日爬取任务"""
        logger.info("=== 开始执行每日爬取任务 ===")
        
        try:
            # 爬取所有来源
            results = self.crawler_manager.crawl_all_sources()
            
            # 记录结果
            total_quotes = sum(results.values())
            logger.info(f"每日爬取完成，总计新增 {total_quotes} 条金句")
            
            for source, count in results.items():
                logger.info(f"  {source}: {count} 条")
            
            # 获取统计信息
            stats = self.db_manager.get_stats()
            logger.info(f"数据库总金句数: {stats['total_quotes']}")
            
        except Exception as e:
            logger.error(f"每日爬取任务失败: {e}")
    
    async def health_check_job(self):
        """健康检查任务"""
        try:
            stats = self.db_manager.get_stats()
            logger.info(f"健康检查 - 总金句数: {stats['total_quotes']}, 今日新增: {stats['today_quotes']}")
        except Exception as e:
            logger.error(f"健康检查失败: {e}")
    
    def setup_jobs(self):
        """设置定时任务"""
        # 每日上午9点执行爬取任务
        self.scheduler.add_job(
            self.daily_crawl_job,
            CronTrigger(hour=9, minute=0),
            id='daily_crawl',
            name='每日金句爬取',
            replace_existing=True,
            misfire_grace_time=300  # 允许5分钟的延迟
        )
        
        # 每小时执行健康检查
        self.scheduler.add_job(
            self.health_check_job,
            CronTrigger(minute=0),
            id='health_check',
            name='健康检查',
            replace_existing=True
        )
        
        logger.info("定时任务设置完成:")
        logger.info("  - 每日爬取: 09:00")
        logger.info("  - 健康检查: 每小时")
    
    def start(self):
        """启动调度器"""
        self.setup_jobs()
        self.scheduler.start()
        logger.info("调度器已启动")
    
    def stop(self):
        """停止调度器"""
        self.scheduler.shutdown()
        logger.info("调度器已停止")
    
    def get_jobs(self):
        """获取任务列表"""
        jobs = []
        for job in self.scheduler.get_jobs():
            try:
                next_run = getattr(job, 'next_run_time', None)
                next_run_str = next_run.isoformat() if next_run else None
            except Exception:
                next_run_str = None
                
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run': next_run_str
            })
        return jobs

async def main():
    """主函数"""
    scheduler = QuoteScheduler()
    
    try:
        # 启动调度器
        scheduler.start()
        
        # 显示任务信息
        jobs = scheduler.get_jobs()
        print(f"已启动 {len(jobs)} 个定时任务:")
        for job in jobs:
            print(f"  - {job['name']}: {job['next_run']}")
        
        # 保持运行
        print("调度器运行中，按 Ctrl+C 停止...")
        
        # 定期显示状态
        while True:
            await asyncio.sleep(3600)  # 每小时显示一次状态
            jobs = scheduler.get_jobs()
            print(f"[{datetime.now().strftime('%H:%M')}] 调度器正常运行，下次任务: {jobs[0]['next_run'] if jobs else '无'}")
            
    except KeyboardInterrupt:
        print("\n收到停止信号...")
        scheduler.stop()
        print("调度器已停止")
    except Exception as e:
        logger.error(f"调度器运行异常: {e}")
        scheduler.stop()

if __name__ == "__main__":
    # 检查命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            # 测试模式：立即执行一次爬取
            print("=== 测试模式：执行单次爬取 ===")
            scheduler = QuoteScheduler()
            asyncio.run(scheduler.daily_crawl_job())
        elif sys.argv[1] == "status":
            # 状态模式：显示任务状态
            scheduler = QuoteScheduler()
            scheduler.setup_jobs()
            jobs = scheduler.get_jobs()
            print("定时任务状态:")
            for job in jobs:
                print(f"  {job['name']}: {job['next_run']}")
        else:
            print("用法:")
            print("  python scheduler.py        # 启动调度器")
            print("  python scheduler.py test   # 测试爬取")
            print("  python scheduler.py status # 查看状态")
    else:
        # 正常启动调度器
        asyncio.run(main())