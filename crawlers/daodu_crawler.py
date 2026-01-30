from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class DaoduCrawler:
    """岛读精选语录（本地库，离线可用）"""

    def __init__(self):
        self.quotes = [
            "愿你在尘世获得幸福，也能拎起行囊踏遍山川湖海。",
            "心里有海，春暖花开，世界就会对你温柔以待。",
            "把生活的锋芒收一收，把温柔与耐心多一分。",
            "有些路只能一个人走，但不会一直走在夜里。",
            "向着光，逆着风，也要走完这段路。",
            "治愈自己最好的方式，是去做喜欢的事，并且去爱人。",
            "人生总要有一次奋不顾身，才知道自己有多强大。",
            "让自己安静一会儿，好运就会慢慢靠近。",
        ]

    def crawl_quotes(self) -> List[Dict]:
        logger.info("使用岛读本地语录库")
        return [
            {"content": c if c.endswith(("。", "！", "!")) else c + "。", "source": "岛读", "original_url": "", "author": "", "category": "治愈"}
            for c in self.quotes
        ]
