from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from pydantic import BaseModel
from database.db_manager import DatabaseManager
from crawlers.crawler_manager import CrawlerManager
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["quotes"])
db_manager = DatabaseManager()
crawler_manager = CrawlerManager()

# 响应模型
class QuoteResponse(BaseModel):
    id: int
    content: str
    source: str
    original_url: Optional[str] = None
    author: Optional[str] = None
    category: Optional[str] = None
    created_at: str

class PaginationInfo(BaseModel):
    page: int
    limit: int
    total: int
    total_pages: int

class QuotesListResponse(BaseModel):
    quotes: list[QuoteResponse]
    pagination: PaginationInfo
    query: Optional[str] = None

class TodayQuoteResponse(BaseModel):
    id: int
    content: str
    source: str
    original_url: Optional[str] = None
    author: Optional[str] = None
    category: Optional[str] = None
    created_at: str
    is_today: bool

@router.get("/today", response_model=TodayQuoteResponse)
async def get_today_quote():
    """获取今日金句"""
    try:
        quote = db_manager.get_today_quote()
        if not quote:
            raise HTTPException(status_code=404, detail="暂无金句")
        
        # 判断是否为今日金句
        from datetime import datetime
        today = datetime.now().strftime('%Y-%m-%d')
        quote_date = quote['created_at'].split(' ')[0]
        is_today = quote_date == today
        
        return {
            **quote,
            'is_today': is_today
        }
    except HTTPException:
        # 将业务类 HTTPException 原样抛出，避免被捕获为 500
        raise
    except Exception as e:
        logger.error(f"获取今日金句失败: {e}")
        raise HTTPException(status_code=500, detail="获取今日金句失败")

@router.get("/history", response_model=QuotesListResponse)
async def get_history_quotes(
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(10, ge=1, le=100, description="每页数量")
):
    """获取历史金句（分页）"""
    try:
        result = db_manager.get_history_quotes(page=page, limit=limit)
        
        # 格式化响应
        quotes = []
        for quote in result['quotes']:
            quotes.append(QuoteResponse(**quote))
        
        return QuotesListResponse(
            quotes=quotes,
            pagination=PaginationInfo(**result['pagination'])
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取历史金句失败: {e}")
        raise HTTPException(status_code=500, detail="获取历史金句失败")

@router.get("/search", response_model=QuotesListResponse)
async def search_quotes(
    q: str = Query(..., min_length=1, description="搜索关键词"),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(10, ge=1, le=100, description="每页数量")
):
    """搜索金句"""
    try:
        result = db_manager.search_quotes(query=q, page=page, limit=limit)
        
        # 格式化响应
        quotes = []
        for quote in result['quotes']:
            quotes.append(QuoteResponse(**quote))
        
        return QuotesListResponse(
            quotes=quotes,
            pagination=PaginationInfo(**result['pagination']),
            query=q
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"搜索金句失败: {e}")
        raise HTTPException(status_code=500, detail="搜索金句失败")

@router.get("/stats")
async def get_statistics():
    """获取统计信息"""
    try:
        stats = db_manager.get_stats()
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@router.post("/crawl/{source}")
async def trigger_crawl(source: str):
    """手动触发爬取"""
    try:
        if source not in crawler_manager.get_available_sources():
            raise HTTPException(status_code=404, detail=f"不支持的来源: {source}")
        
        count = crawler_manager.crawl_single_source(source)
        
        return {
            "success": True,
            "message": f"{source}爬取完成",
            "quotes_added": count
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"触发爬取失败: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@router.get("/crawl/status")
async def get_crawl_status():
    """获取爬取状态"""
    try:
        logs = db_manager.get_crawl_logs(limit=20)
        sources = crawler_manager.get_available_sources()
        
        return {
            "success": True,
            "data": {
                "available_sources": sources,
                "recent_logs": logs
            }
        }
    except Exception as e:
        logger.error(f"获取爬取状态失败: {e}")
        return {
            "success": False,
            "error": str(e)
        }
