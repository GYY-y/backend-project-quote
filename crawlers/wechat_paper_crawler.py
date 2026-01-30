from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class WechatPaperCrawler:
    """
    人民日报微信公众号“爬虫”
    由于直接抓取微信页面常受限，这里提供权威精选语录的本地备选。
    如需真实抓取，可在网络畅通时改写为实际请求 mp.weixin.qq.com。
    """

    def __init__(self):
        self.quotes = [
            ("把自己照顾好，比什么都重要。", "人民日报微信", "人民日报"),
            ("先成为更好的自己，再遇见对的人。", "人民日报微信", "人民日报"),
            ("生活有一百种模样，你要有一百种坚持。", "人民日报微信", "人民日报"),
            ("你未必出类拔萃，但一定与众不同。", "人民日报微信", "人民日报"),
            ("请相信，每一份热爱都值得全力以赴。", "人民日报微信", "人民日报"),
            ("保持热爱，奔赴山海。", "人民日报微信", "人民日报"),
            ("心里有光，何惧道阻且长。", "人民日报微信", "人民日报"),
            ("和解不是妥协，而是放过自己。", "人民日报微信", "人民日报"),
        ]

    def crawl_quotes(self) -> List[Dict]:
        logger.info("使用本地人民日报微信精选语录库，避免微信反爬限制")
        return [
            {
                "content": c,
                "source": "人民日报微信",
                "original_url": "",
                "author": "",
                "category": cat,
            }
            for c, cat, _ in self.quotes
        ]
