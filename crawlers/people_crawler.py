from .base import BaseCrawler
from typing import List, Dict
import logging
import re

logger = logging.getLogger(__name__)

class PeopleCrawler(BaseCrawler):
    """人民网爬虫"""
    
    def __init__(self):
        super().__init__("人民网")
        self.base_urls = [
            "http://opinion.people.com.cn",  # 观点频道
            "http://theory.people.com.cn",   # 理论频道
        ]
        self.target_paths = [
            "/GB/82182/",
            "/GB/405214/",
            "/GB/82182/82213/",  # 人民评论
        ]
    
    def crawl_quotes(self) -> List[Dict]:
        """爬取人民网金句"""
        quotes = []
        
        for base_url in self.base_urls:
            try:
                # 获取主页
                soup = self.get_page(base_url)
                if not soup:
                    continue
                
                # 查找文章链接
                article_links = self._find_article_links(soup, base_url)
                logger.info(f"找到 {len(article_links)} 篇文章链接")
                
                # 爬取文章内容
                for link in article_links[:10]:  # 限制数量避免过多请求
                    article_quotes = self._crawl_article(link)
                    quotes.extend(article_quotes)
                    
            except Exception as e:
                logger.error(f"爬取人民网失败: {e}")
                continue
        
        # 去重
        unique_quotes = self._deduplicate_quotes(quotes)
        logger.info(f"人民网共获取 {len(unique_quotes)} 条金句")
        
        return unique_quotes
    
    def _find_article_links(self, soup, base_url: str) -> List[str]:
        """查找文章链接"""
        links = []
        
        # 常见的选择器
        selectors = [
            'a[href*="/GB/"]',  # 人民网文章链接格式
            'a[href*="n1"]',    # 新闻链接
            '.w1000 a',         # 内容区域链接
            '.hdNews a',        # 头条新闻链接
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
            'index.htm', 'index.html', 'mailto:', 'tel:'
        ]
        
        for pattern in exclude_patterns:
            if pattern in href.lower():
                return False
        
        # 人民网文章通常包含这些特征
        article_patterns = [
            '/n1/', '/GB/', 'people.com.cn'
        ]
        
        return any(pattern in href for pattern in article_patterns)
    
    def _normalize_url(self, href: str, base_url: str) -> str:
        """标准化URL"""
        if href.startswith('http'):
            return href
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
            
            # 查找可能包含金句的内容区域
            content_selectors = [
                '.rm_txt_con',    # 人民网内容区域
                '.article-content',
                '.content',
                '.text',
                'div[class*="content"]',
                'div[id*="content"]',
                'p',
            ]
            
            for selector in content_selectors:
                try:
                    elements = soup.select(selector)
                    for element in elements:
                        full_text = self.clean_text(element.get_text())
                        # 按句拆分，避免整段长文
                        sentences = [s.strip() for s in re.split(r'[。！？!]', full_text) if s.strip()]
                        
                        for sent in sentences:
                            if self.is_quote(sent):
                                quote = {
                                    'content': sent if sent.endswith(('。','！','!')) else sent + '。',
                                    'source': '人民网',
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
            '.article-title',
            '.title',
            'h2',
            '.main-title'
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
            '[class*="author"]',
            'span:contains("作者")',
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
            'span:contains("栏目")',
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
        
        return "观点"
    
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
