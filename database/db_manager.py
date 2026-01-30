import sqlite3
import os
from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """数据库管理类"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # 默认数据库路径
            current_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(current_dir, '..', '..', 'database', 'quotes.db')
        
        self.db_path = db_path
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """确保数据库文件存在"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # 如果数据库不存在，创建表
        if not os.path.exists(self.db_path):
            self._init_tables()
    
    def _init_tables(self):
        """初始化数据库表"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 创建quotes表
            cursor.execute('''
                CREATE TABLE quotes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    source VARCHAR(50) NOT NULL,
                    original_url TEXT,
                    author VARCHAR(100),
                    category VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(content)
                )
            ''')
            
            # 创建crawl_logs表
            cursor.execute('''
                CREATE TABLE crawl_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source VARCHAR(50) NOT NULL,
                    quotes_count INTEGER DEFAULT 0,
                    status VARCHAR(20) DEFAULT 'success',
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建索引
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_quotes_source ON quotes(source)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_quotes_created_at ON quotes(created_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_crawl_logs_source ON crawl_logs(source)')
            
            conn.commit()
            logger.info(f"数据库初始化完成: {self.db_path}")
    
    def insert_quotes(self, quotes: List[Dict]) -> int:
        """插入金句数据"""
        if not quotes:
            return 0
        
        inserted_count = 0
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for quote in quotes:
                try:
                    cursor.execute('''
                        INSERT OR IGNORE INTO quotes 
                        (content, source, original_url, author, category)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        quote.get('content', ''),
                        quote.get('source', ''),
                        quote.get('original_url', ''),
                        quote.get('author', ''),
                        quote.get('category', '')
                    ))
                    
                    if cursor.rowcount > 0:
                        inserted_count += 1
                        
                except sqlite3.Error as e:
                    logger.error(f"插入金句失败: {e}")
                    continue
            
            conn.commit()
            logger.info(f"成功插入 {inserted_count} 条新金句")
        
        return inserted_count
    
    def log_crawl_result(self, source: str, quotes_count: int, status: str = 'success', error_message: str = None):
        """记录爬取日志"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO crawl_logs 
                (source, quotes_count, status, error_message)
                VALUES (?, ?, ?, ?)
            ''', (source, quotes_count, status, error_message))
            
            conn.commit()
            logger.info(f"记录爬取日志: {source} - {quotes_count} 条 - {status}")
    
    def get_today_quote(self) -> Optional[Dict]:
        """获取今日金句"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM quotes 
                WHERE DATE(created_at) = DATE('now')
                ORDER BY created_at DESC 
                LIMIT 1
            ''')
            
            row = cursor.fetchone()
            if row:
                return dict(row)
            
            # 如果今天没有金句，获取最新的
            cursor.execute('''
                SELECT * FROM quotes 
                ORDER BY created_at DESC 
                LIMIT 1
            ''')
            
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_history_quotes(self, page: int = 1, limit: int = 10) -> Dict:
        """获取历史金句（分页）"""
        offset = (page - 1) * limit
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 获取总数
            cursor.execute('SELECT COUNT(*) as total FROM quotes')
            total = cursor.fetchone()['total']
            
            # 获取分页数据
            cursor.execute('''
                SELECT * FROM quotes 
                ORDER BY created_at DESC 
                LIMIT ? OFFSET ?
            ''', (limit, offset))
            
            quotes = [dict(row) for row in cursor.fetchall()]
            
            total_pages = (total + limit - 1) // limit
            
            return {
                'quotes': quotes,
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'total_pages': total_pages
                }
            }
    
    def search_quotes(self, query: str, page: int = 1, limit: int = 10) -> Dict:
        """搜索金句"""
        offset = (page - 1) * limit
        search_query = f"%{query}%"
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 获取总数
            cursor.execute('''
                SELECT COUNT(*) as total FROM quotes 
                WHERE content LIKE ? OR author LIKE ? OR category LIKE ?
            ''', (search_query, search_query, search_query))
            total = cursor.fetchone()['total']
            
            # 获取搜索结果
            cursor.execute('''
                SELECT * FROM quotes 
                WHERE content LIKE ? OR author LIKE ? OR category LIKE ?
                ORDER BY created_at DESC 
                LIMIT ? OFFSET ?
            ''', (search_query, search_query, search_query, limit, offset))
            
            quotes = [dict(row) for row in cursor.fetchall()]
            
            total_pages = (total + limit - 1) // limit
            
            return {
                'quotes': quotes,
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'total_pages': total_pages
                },
                'query': query
            }
    
    def get_crawl_logs(self, source: str = None, limit: int = 10) -> List[Dict]:
        """获取爬取日志"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if source:
                cursor.execute('''
                    SELECT * FROM crawl_logs 
                    WHERE source = ?
                    ORDER BY created_at DESC 
                    LIMIT ?
                ''', (source, limit))
            else:
                cursor.execute('''
                    SELECT * FROM crawl_logs 
                    ORDER BY created_at DESC 
                    LIMIT ?
                ''', (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 总金句数
            cursor.execute('SELECT COUNT(*) as total_quotes FROM quotes')
            total_quotes = cursor.fetchone()[0]
            
            # 今日金句数
            cursor.execute('''
                SELECT COUNT(*) as today_quotes 
                FROM quotes 
                WHERE DATE(created_at) = DATE('now')
            ''')
            today_quotes = cursor.fetchone()[0]
            
            # 按来源统计
            cursor.execute('''
                SELECT source, COUNT(*) as count 
                FROM quotes 
                GROUP BY source 
                ORDER BY count DESC
            ''')
            source_stats = dict(cursor.fetchall())
            
            # 最近爬取状态
            cursor.execute('''
                SELECT source, status, created_at 
                FROM crawl_logs 
                ORDER BY created_at DESC 
                LIMIT 5
            ''')
            recent_logs = [
                {'source': row[0], 'status': row[1], 'created_at': row[2]}
                for row in cursor.fetchall()
            ]
            
            return {
                'total_quotes': total_quotes,
                'today_quotes': today_quotes,
                'source_stats': source_stats,
                'recent_logs': recent_logs
            }