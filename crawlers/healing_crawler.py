from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class HealingCrawler:
    """
    治愈系金句“爬虫”
    实际使用本地权威语录库，避免网络不通无法获取。
    """

    def __init__(self):
        # 可按需扩充，保持简短有力量的治愈类句子
        self.quotes = [
            ("愿你眼里有光，心里有海，生活自带光芒。", "治愈系", "人民日报"),
            ("慢一点也没关系，努力总会看得见。", "治愈系", "人民日报"),
            ("别怕，天总会亮的，云也会散的。", "治愈系", "人民日报"),
            ("今天的努力，都是为了将来有更多选择的底气。", "治愈系", "央视网"),
            ("学会和解，和别人，也和自己。", "治愈系", "新华社"),
            ("生活没有一劳永逸，心态可以柳暗花明。", "治愈系", "人民日报"),
            ("你可以慢一点，但别停下脚步。", "治愈系", "央视网"),
            ("和自己和解，也别放弃自己。", "治愈系", "新华社"),
            ("善待当下，就是善待未来。", "治愈系", "人民日报"),
            ("总会有人和风而来，陪你看细水长流。", "治愈系", "人民日报"),
        ]

    def crawl_quotes(self) -> List[Dict]:
        logger.info("使用本地治愈系语录库，避免网络波动")
        results = []
        for content, category, source in self.quotes:
            results.append({
                "content": content,
                "source": source,
                "original_url": "",
                "author": "",
                "category": category,
            })
        return results
