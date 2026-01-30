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
    
    def get_page(self, url: str, timeout: int = 10) -> Optional[BeautifulSoup]:
        """获取页面内容"""
        try:
            # 随机延迟，避免请求过快
            delay = random.uniform(2, 5)
            time.sleep(delay)
            
            response = self.session.get(url, timeout=timeout)
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
        """判断是否为励志金句"""
        if not text or len(text) < 10:
            return False
        
        # 排除包含以下关键词的文本
        exclude_keywords = [
            '广告', '推广', '链接', '点击', '下载', '购买', '价格',
            '电话', '地址', '邮箱', '网站', 'http', 'www'
        ]
        
        for keyword in exclude_keywords:
            if keyword in text:
                return False
        
        # 励志相关关键词
        include_keywords = [
            '奋斗', '坚持', '努力', '成功', '梦想', '希望', '勇气',
            '信念', '励志', '人生', '成长', '进步', '挑战', '目标'
        ]
        
        # 如果文本较长且包含励志相关词汇，更可能是金句
        text_lower = text.lower()
        has_inspirational = any(keyword in text_lower for keyword in include_keywords)
        
        # 简单启发式：长度适中、包含积极词汇
        return (10 <= len(text) <= 200 and 
                (has_inspirational or len(text) > 30))