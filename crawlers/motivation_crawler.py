from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class MotivationCrawler:
    """Motivation 精选语录（本地库）"""

    def __init__(self):
        self.quotes = [
            "今天的汗水，都是明天的底气。",
            "把时间花在让自己变好的事情上。",
            "先行动，再有情绪；先开始，再谈坚持。",
            "把简单的事做好，就是不简单；把平凡的事做好，就是不平凡。",
            "相信过程，所有积累都会发光。",
            "越自律，越自由；越坚持，越幸运。",
            "行动是最好的治愈，努力是最好的回应。",
            "不在沉默中爆发，就在沉默中入睡；所以要醒着拼。"
        ]

    def crawl_quotes(self) -> List[Dict]:
        logger.info("使用 Motivation 本地语录库")
        return [
            {"content": c if c.endswith(('。','！','!')) else c + '。', "source": "Motivation", "original_url": "", "author": "", "category": "励志"}
            for c in self.quotes
        ]
