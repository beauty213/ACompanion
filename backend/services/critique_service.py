from typing import Any, Dict, List, Optional
from backend.services.online_meme_service import online_meme_service

class MemeCritiqueService:
    """
    Evaluates journal entries and pairs them with related online memes sourced from
    social media (Reddit, Twitter/X, Instagram, Know Your Meme) and Google.
    Does NOT use local folder memes.
    """

    def evaluate(self, text: str, title: Optional[str] = None) -> Dict[str, Any]:
        return online_meme_service.evaluate(text, title)

    def shuffle(self, text: str, current_meme: Optional[str] = None) -> Dict[str, Any]:
        return online_meme_service.shuffle(text, current_meme)

    def search(self, query: str) -> List[Dict[str, Any]]:
        return online_meme_service.search_online_memes(query)

critique_service = MemeCritiqueService()
