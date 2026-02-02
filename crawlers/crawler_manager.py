from .people_crawler import PeopleCrawler
from .paper_crawler import PaperCrawler
from .wechat_paper_crawler import WechatPaperCrawler
from .healing_crawler import HealingCrawler
from .daodu_crawler import DaoduCrawler
from .motivation_crawler import MotivationCrawler
from .juzikong_crawler import JuziKongCrawler
from .yiyan_crawler import YiYanCrawler
from .judou_crawler import JuDouCrawler
from .curated_crawler import CuratedCrawler
from database.db_manager import DatabaseManager
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class CrawlerManager:
    """爬虫管理器"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.crawlers = {
            '人民网': PeopleCrawler(),
            '人民日报': PaperCrawler(),
            '人民日报微信': WechatPaperCrawler(),
            '治愈系精选': HealingCrawler(),
            '岛读': DaoduCrawler(),
            'Motivation': MotivationCrawler(),
            '句子控': JuziKongCrawler(),
            '一言': YiYanCrawler(),
            '句读': JuDouCrawler(),
            '精选金句': CuratedCrawler(),
        }
    
    def crawl_all_sources(self) -> Dict[str, int]:
        """爬取所有来源的金句"""
        results = {}
        
        for source_name, crawler in self.crawlers.items():
            try:
                logger.info(f"开始爬取 {source_name}")
                quotes = crawler.crawl_quotes()
                
                if quotes:
                    # 插入数据库
                    inserted_count = self.db_manager.insert_quotes(quotes)
                    
                    # 记录日志
                    self.db_manager.log_crawl_result(
                        source=source_name,
                        quotes_count=inserted_count,
                        status='success'
                    )
                    
                    results[source_name] = inserted_count
                    logger.info(f"{source_name} 爬取完成，新增 {inserted_count} 条金句")
                else:
                    self.db_manager.log_crawl_result(
                        source=source_name,
                        quotes_count=0,
                        status='no_quotes'
                    )
                    results[source_name] = 0
                    logger.warning(f"{source_name} 未获取到金句")
                    
            except Exception as e:
                error_msg = str(e)
                logger.error(f"{source_name} 爬取失败: {error_msg}")
                
                # 记录错误日志
                self.db_manager.log_crawl_result(
                    source=source_name,
                    quotes_count=0,
                    status='error',
                    error_message=error_msg
                )
                
                results[source_name] = 0
        
        return results
    
    def crawl_single_source(self, source_name: str) -> int:
        """爬取单个来源的金句"""
        if source_name not in self.crawlers:
            raise ValueError(f"不支持的爬虫来源: {source_name}")
        
        crawler = self.crawlers[source_name]
        
        try:
            logger.info(f"开始爬取 {source_name}")
            quotes = crawler.crawl_quotes()
            
            if quotes:
                # 插入数据库
                inserted_count = self.db_manager.insert_quotes(quotes)
                
                # 记录日志
                self.db_manager.log_crawl_result(
                    source=source_name,
                    quotes_count=inserted_count,
                    status='success'
                )
                
                logger.info(f"{source_name} 爬取完成，新增 {inserted_count} 条金句")
                return inserted_count
            else:
                self.db_manager.log_crawl_result(
                    source=source_name,
                    quotes_count=0,
                    status='no_quotes'
                )
                logger.warning(f"{source_name} 未获取到金句")
                return 0
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f"{source_name} 爬取失败: {error_msg}")
            
            # 记录错误日志
            self.db_manager.log_crawl_result(
                source=source_name,
                quotes_count=0,
                status='error',
                error_message=error_msg
            )
            
            return 0
    
    def get_available_sources(self) -> List[str]:
        """获取可用的爬虫来源列表"""
        return list(self.crawlers.keys())
    
    def test_crawler(self, source_name: str) -> Dict[str, any]:
        """测试单个爬虫"""
        if source_name not in self.crawlers:
            return {
                'success': False,
                'error': f"不支持的爬虫来源: {source_name}"
            }
        
        crawler = self.crawlers[source_name]
        
        try:
            logger.info(f"测试爬虫: {source_name}")
            quotes = crawler.crawl_quotes()
            
            return {
                'success': True,
                'source': source_name,
                'quotes_found': len(quotes),
                'sample_quotes': quotes[:3] if quotes else []
            }
            
        except Exception as e:
            return {
                'success': False,
                'source': source_name,
                'error': str(e)
            }
    
    def get_crawl_stats(self) -> Dict:
        """获取爬虫统计信息"""
        return self.db_manager.get_stats()
