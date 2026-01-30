from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class JuziKongCrawler:
    """句子控精选（本地库）"""

    def __init__(self):
        self.quotes = [
            "请相信，所有的等待都值得，所有的付出都有回报。",
            "你要悄悄拔尖，然后惊艳所有人。",
            "心向光明，终会抵达。",
            "与其踟蹰不前，不如向前一步。",
            "生活偶尔失色，但你要保持热爱。",
            "笑对生活，温柔以待。",
            "日子靠自己撑起来，才会稳稳当当。",
            "别急，万物皆有时。"
        ]

    def crawl_quotes(self) -> List[Dict]:
        logger.info("使用句子控本地语录库")
        return [
            {"content": c if c.endswith(('。','！','!')) else c + '。', "source": "句子控", "original_url": "", "author": "", "category": "治愈"}
            for c in self.quotes
        ]
