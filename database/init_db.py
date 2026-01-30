import sqlite3
import os

def init_database():
    """初始化SQLite数据库"""
    # 确保数据库目录存在
    db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'database', 'quotes.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建quotes表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quotes (
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
        CREATE TABLE IF NOT EXISTS crawl_logs (
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
    conn.close()
    print(f"数据库初始化完成: {db_path}")

if __name__ == "__main__":
    init_database()