import os
import requests
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class QuoteTranslator:
    """
    简单翻译器：
    - 优先使用 DeepL（需设置 DEEPL_API_KEY）
    - 其次使用 LibreTranslate（设置 LIBRE_TRANSLATE_URL，可选 LIBRE_TRANSLATE_API_KEY）
    - 都未配置则返回 None（不翻译）
    """

    def __init__(self):
        self.deepl_key = os.getenv("DEEPL_API_KEY")
        self.libre_url = os.getenv("LIBRE_TRANSLATE_URL")
        self.libre_key = os.getenv("LIBRE_TRANSLATE_API_KEY")

    def translate(self, text: str, target_lang: str = "ZH") -> Optional[str]:
        if not text:
            return None

        # DeepL
        if self.deepl_key:
            try:
                resp = requests.post(
                    "https://api-free.deepl.com/v2/translate",
                    data={
                        "auth_key": self.deepl_key,
                        "text": text,
                        "target_lang": target_lang,
                    },
                    timeout=8,
                )
                resp.raise_for_status()
                data = resp.json()
                translations = data.get("translations") or []
                if translations:
                    return translations[0].get("text")
            except Exception as e:
                logger.warning(f"DeepL 翻译失败: {e}")

        # LibreTranslate
        if self.libre_url:
            try:
                payload = {
                    "q": text,
                    "source": "auto",
                    "target": target_lang.lower(),
                    "format": "text",
                }
                if self.libre_key:
                    payload["api_key"] = self.libre_key
                resp = requests.post(self.libre_url.rstrip("/") + "/translate", data=payload, timeout=8)
                resp.raise_for_status()
                data = resp.json()
                translated = data.get("translatedText")
                if translated:
                    return translated
            except Exception as e:
                logger.warning(f"LibreTranslate 翻译失败: {e}")

        return None
