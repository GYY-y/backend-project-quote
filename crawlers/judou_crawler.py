from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class JuDouCrawler:
    """句读精选（本地库）"""

    def __init__(self):
        self.quotes = [
            "你走过的每一步，都算数。",
            "别让世俗淹没了你想要的生活。",
            "安静下来，听一听内心的答案。",
            "努力会说话，时间会回应。",
            "温柔要有，但不失锋芒。",
            "有些路，只有走过才知道苦与甜。",
            "给自己时间，慢慢沉淀，慢慢成长。",
            "做自己的光，照亮自己的路。"
        ]

    def crawl_quotes(self) -> List[Dict]:
        logger.info("使用句读本地精选库")
        return [
            {"content": c if c.endswith(('。','！','!')) else c + '。', "source": "句读", "original_url": "", "author": "", "category": "治愈"}
            for c in self.quotes
        ]
