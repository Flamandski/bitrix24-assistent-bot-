"""
Скрипт для перестроения FAISS-индекса после обновления документации.
Запускайте после python -m modules.scraper
"""

from modules.database import init_db
from modules.rag import get_rag_searcher

if __name__ == "__main__":
    init_db()
    rag = get_rag_searcher()
    rag.build_index()