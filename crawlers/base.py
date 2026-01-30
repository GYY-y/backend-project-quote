import os
import requests
import time
import random
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from abc import ABC, abstractmethod
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseCrawler(ABC):
    """爬虫基类"""
    
    def __init__(self, name: str):
        self.name = name
        self.session = requests.Session()
        self.setup_headers()
        self.setup_proxy()
        # 可通过环境变量调整延迟/超时，便于在受限网络环境下调试
        self.min_delay = float(os.getenv("CRAWLER_MIN_DELAY", "0.8"))
        self.max_delay = float(os.getenv("CRAWLER_MAX_DELAY", "2.0"))
        self.request_timeout = int(os.getenv("CRAWLER_TIMEOUT", "10"))
        
    def setup_headers(self):
        """设置请求头"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        ]
        
        self.session.headers.update({
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def setup_proxy(self):
        """配置代理，支持通过环境变量设置"""
        # 优先使用自定义环境变量，其次使用系统的 HTTP(S)_PROXY
        http_proxy = os.getenv("CRAWLER_HTTP_PROXY") or os.getenv("HTTP_PROXY")
        https_proxy = os.getenv("CRAWLER_HTTPS_PROXY") or os.getenv("HTTPS_PROXY")
        if http_proxy or https_proxy:
            self.session.proxies.update({
                "http": http_proxy,
                "https": https_proxy or http_proxy,
            })
            logger.info(f"{self.name} 使用代理: http={http_proxy}, https={https_proxy or http_proxy}")
    
    def get_page(self, url: str, timeout: int = 10) -> Optional[BeautifulSoup]:
        """获取页面内容"""
        try:
            # 随机延迟，避免请求过快
            delay = random.uniform(self.min_delay, self.max_delay)
            time.sleep(delay)
            
            response = self.session.get(url, timeout=timeout or self.request_timeout)
            response.raise_for_status()
            
            # 检测编码
            if response.encoding == 'ISO-8859-1':
                response.encoding = response.apparent_encoding
            
            soup = BeautifulSoup(response.text, 'html.parser')
            logger.info(f"成功获取页面: {url}")
            return soup
            
        except requests.RequestException as e:
            logger.error(f"请求失败 {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"解析页面失败 {url}: {e}")
            return None
    
    def clean_text(self, text: str) -> str:
        """清理文本内容"""
        if not text:
            return ""
        
        # 去除多余空白字符
        text = ' '.join(text.split())
        # 去除HTML实体
        import html
        text = html.unescape(text)
        
        return text.strip()
    
    @abstractmethod
    def crawl_quotes(self) -> List[Dict]:
        """爬取金句 - 子类必须实现"""
        pass
    
    def is_quote(self, text: str) -> bool:
        """最小化过滤：只要有内容且长度合理即收录"""
        if not text:
            return False
        text = text.strip()
        return 6 <= len(text) <= 200
