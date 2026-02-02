from .base import BaseCrawler
from typing import List, Dict
import logging
import re

logger = logging.getLogger(__name__)

class PaperCrawler(BaseCrawler):
    """人民日报爬虫"""
    
    def __init__(self):
        super().__init__("人民日报")
        self.base_urls = [
            "http://paper.people.com.cn",     # 人民日报电子版
            "https://www.people.com.cn",      # 人民网主页
        ]
        self.target_sections = [
            "rmrb",      # 人民日报
            "opinion",   # 观点
            "theory",    # 理论
        ]
    
    def crawl_quotes(self) -> List[Dict]:
        """爬取人民日报金句"""
        quotes = []
        
        for base_url in self.base_urls:
            try:
                # 获取主页
                soup = self.get_page(base_url)
                if not soup:
                    continue
                
                # 查找文章链接
                article_links = self._find_article_links(soup, base_url)
                logger.info(f"人民日报找到 {len(article_links)} 篇文章链接")
                
                # 爬取文章内容
                for link in article_links[:8]:  # 限制数量
                    article_quotes = self._crawl_article(link)
                    quotes.extend(article_quotes)
                    
            except Exception as e:
                logger.error(f"爬取人民日报失败: {e}")
                continue
        
        # 去重
        unique_quotes = self._deduplicate_quotes(quotes)
        logger.info(f"人民日报共获取 {len(unique_quotes)} 条金句")
        
        return unique_quotes
    
    def _find_article_links(self, soup, base_url: str) -> List[str]:
        """查找文章链接"""
        links = []
        
        # 人民日报常见的选择器
        selectors = [
            'a[href*="/n1/"]',        # 新闻链接格式
            'a[href*="/rmrb/"]',      # 人民日报链接
            'a[href*="paper.people"]', # 电子版链接
            '.news_list a',           # 新闻列表
            '.content_list a',        # 内容列表
            '.title a',               # 标题链接
            'h3 a',                   # 标题链接
            'h4 a',                   # 副标题链接
        ]
        
        for selector in selectors:
            try:
                elements = soup.select(selector)
                for element in elements:
                    href = element.get('href')
                    if href and self._is_article_link(href):
                        full_url = self._normalize_url(href, base_url)
                        if full_url not in links:
                            links.append(full_url)
            except Exception as e:
                logger.warning(f"选择器 {selector} 失败: {e}")
        
        return links
    
    def _is_article_link(self, href: str) -> bool:
        """判断是否为文章链接"""
        # 排除非文章链接
        exclude_patterns = [
            '#', 'javascript:', 'mailto:', '.jpg', '.png', '.gif',
            'index.htm', 'index.html', 'video', 'live', 'photo'
        ]
        
        for pattern in exclude_patterns:
            if pattern in href.lower():
                return False
        
        # 人民日报文章特征
        article_patterns = [
            '/n1/', '/rmrb/', '/paper/', '/opinion/',
            'people.com.cn'
        ]
        
        return any(pattern in href for pattern in article_patterns)
    
    def _normalize_url(self, href: str, base_url: str) -> str:
        """标准化URL"""
        if href.startswith('http'):
            return href
        elif href.startswith('//'):
            return 'https:' + href
        elif href.startswith('/'):
            domain = base_url.split('//')[0] + '//' + base_url.split('//')[1].split('/')[0]
            return domain + href
        else:
            return base_url.rstrip('/') + '/' + href.lstrip('/')
    
    def _crawl_article(self, url: str) -> List[Dict]:
        """爬取单篇文章的金句"""
        quotes = []
        
        try:
            soup = self.get_page(url)
            if not soup:
                return quotes
            
            # 获取标题
            title = self._get_title(soup)
            
            # 人民日报内容区域选择器
            content_selectors = [
                '.content',              # 主内容区域
                '.article-content',       # 文章内容
                '.news_content',         # 新闻内容
                '.text',                 # 文本区域
                'div[class*="content"]', # 包含content的div
                'p',                     # 段落
                '.rm_txt_con',          # 人民网文本内容
            ]
            
            for selector in content_selectors:
                try:
                    elements = soup.select(selector)
                    for element in elements:
                        full_text = self.clean_text(element.get_text())
                        sentences = [s.strip() for s in re.split(r'[。！？!]', full_text) if s.strip()]
                        
                        for sent in sentences:
                            normalized = self.normalize_quote_text(sent)
                            if not normalized:
                                continue
                            quote = {
                                'content': normalized,
                                'source': '人民日报',
                                'original_url': url,
                                'title': title,
                                'author': self._get_author(soup),
                                'category': self._get_category(soup)
                            }
                            quotes.append(quote)
                            
                            # 限制每篇文章最多获取3条金句
                            if len(quotes) >= 3:
                                break
                                
                except Exception as e:
                    logger.warning(f"选择器 {selector} 失败: {e}")
                    continue
                
                if len(quotes) >= 3:
                    break
                    
        except Exception as e:
            logger.error(f"爬取文章 {url} 失败: {e}")
        
        return quotes
    
    def _get_title(self, soup) -> str:
        """获取文章标题"""
        title_selectors = [
            'h1',
            '.title',
            '.article-title',
            '.news-title',
            '.main-title',
            'h2'
        ]
        
        for selector in title_selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    title = self.clean_text(element.get_text())
                    if title and len(title) > 5:
                        return title
            except:
                continue
        
        return ""
    
    def _get_author(self, soup) -> str:
        """获取作者信息"""
        author_selectors = [
            '.author',
            '.byline',
            '.source',
            '[class*="author"]',
            '.info',
            '.editor'
        ]
        
        for selector in author_selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    author = self.clean_text(element.get_text())
                    if author and len(author) < 50:
                        return author
            except:
                continue
        
        return ""
    
    def _get_category(self, soup) -> str:
        """获取分类信息"""
        category_selectors = [
            '.category',
            '.nav',
            '.breadcrumb',
            '.channel',
            '.section'
        ]
        
        for selector in category_selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    category = self.clean_text(element.get_text())
                    if category and len(category) < 30:
                        return category
            except:
                continue
        
        return "人民日报"
    
    def _deduplicate_quotes(self, quotes: List[Dict]) -> List[Dict]:
        """去重金句"""
        seen = set()
        unique_quotes = []
        
        for quote in quotes:
            content = quote['content'].strip()
            if content not in seen:
                seen.add(content)
                unique_quotes.append(quote)
        
        return unique_quotes
