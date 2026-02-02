from typing import List, Dict
from .base import BaseCrawler
import logging

logger = logging.getLogger(__name__)


class CuratedCrawler(BaseCrawler):
    """
    精选金句合集（本地库）
    覆盖：生活类媒体、经典文化、海外主流、语录站、思想类
    """

    def __init__(self):
        super().__init__("精选金句")
        self.quotes_map = {
            "生活类": [
                ("生活偶尔失色，但请保持热爱和耐心。", "三联生活周刊"),
                ("把平凡的日子过出光亮，就是一种勇气。", "南方周末"),
                ("善待当下，就是善待未来。", "澎湃新闻"),
                ("慢下来，才能看见内心最真实的期待。", "界面新闻"),
            ],
            "经典文化": [
                ("道生一，一生二，二生三，三生万物。", "道德经"),
                ("上善若水，水善利万物而不争。", "道德经"),
                ("知者不惑，仁者不忧，勇者不惧。", "论语"),
                ("学而时习之，不亦说乎。", "论语"),
            ],
            "海外主流": [
                ("Success is the sum of small efforts, repeated day in and day out.", "Wallace D. Wattles"),
                ("Courage is not the absence of fear, but the triumph over it.", "Nelson Mandela"),
                ("The future depends on what you do today.", "Mahatma Gandhi"),
                ("Keep your face always toward the sunshine—and shadows will fall behind you.", "Walt Whitman"),
            ],
            "语录精选": [
                ("你走过的每一步，都算数。", "语录"),
                ("先行动，再有情绪；先开始，再谈坚持。", "语录"),
                ("你要悄悄拔尖，然后惊艳时光。", "语录"),
                ("把烦恼留在今天，把期待交给明天。", "语录"),
            ],
            "思想类": [
                ("大道至简，实干为要。", "评论"),
                ("思想有多远，脚步才能走多远。", "评论"),
                ("行胜于言，初心不改。", "评论"),
                ("知不足而奋进，望远山而前行。", "评论"),
            ],
        }

    def crawl_quotes(self) -> List[Dict]:
        logger.info("使用本地精选金句库")
        results: List[Dict] = []
        for category, pairs in self.quotes_map.items():
            for content, source in pairs:
                normalized = self.normalize_quote_text(content)
                if not normalized:
                    continue

                content_en = None
                translated = normalized

                # 海外主流：尝试翻译为中文，原文存 content_en
                if category == "海外主流":
                    content_en = content
                    try:
                        maybe = self.translator.translate(content, target_lang="ZH")
                        if maybe:
                            translated = self.normalize_quote_text(maybe) or maybe
                    except Exception as e:
                        logger.warning(f"翻译失败，使用原文: {e}")

                results.append(
                    {
                        "content": translated,
                        "content_en": content_en or "",
                        "source": source,
                        "original_url": "",
                        "author": "",
                        "category": category,
                    }
                )
        return results
