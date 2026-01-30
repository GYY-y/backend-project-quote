from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class YiYanCrawler:
    """一言（日常一句）本地精选"""

    def __init__(self):
        self.quotes = [
            "人间烟火气，最抚凡人心。",
            "你要悄悄拔尖，然后惊艳时光。",
            "一念放下，万般自在。",
            "心有山海，静而不争。",
            "愿你历尽千帆，归来仍少年。",
            "这世间的温柔，记得分一半给自己。",
            "慢品人间烟火色，闲观万事岁月长。",
            "把烦恼留在今天，把期待交给明天。"
        ]

    def crawl_quotes(self) -> List[Dict]:
        logger.info("使用一言本地精选库")
        return [
            {"content": c if c.endswith(('。','！','!')) else c + '。', "source": "一言", "original_url": "", "author": "", "category": "日常"}
            for c in self.quotes
        ]
