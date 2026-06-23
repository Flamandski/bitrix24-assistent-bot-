"""
Модуль RAG (Retrieval-Augmented Generation) с векторным поиском.
Использует FAISS для быстрого поиска по эмбеддингам документов.
"""

import os
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

from modules.database import SessionLocal, BitrixDoc

# Путь для сохранения индекса FAISS
FAISS_INDEX_PATH = "faiss_index.bin"
FAISS_DOCS_PATH = "faiss_docs_ids.npy"

# Модель для эмбеддингов (маленькая, быстрая, работает локально)
# all-MiniLM-L6-v2 — 384-мерные векторы, хорошее качество/скорость
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"


class RAGSearcher:
    """Поисковик с векторным поиском через FAISS"""
    
    def __init__(self):
        self.model = None
        self.index = None
        self.doc_ids = None
        self._initialized = False
    
    def _load_model(self):
        """Загружает модель эмбеддингов (один раз)"""
        if self.model is None:
            print(f"🧠 Загрузка модели эмбеддингов: {EMBEDDING_MODEL_NAME}...")
            self.model = SentenceTransformer(EMBEDDING_MODEL_NAME)
            print("✅ Модель загружена")
    
    def build_index(self):
        """
        Строит FAISS-индекс из всех документов в БД.
        Вызывается один раз при старте бота или после обновления документации.
        """
        self._load_model()
        
        db = SessionLocal()
        try:
            docs = db.query(BitrixDoc).all()
            if not docs:
                print("⚠️ В базе данных нет документов. Сначала запустите парсер.")
                return False
            
            print(f"🔨 Построение FAISS-индекса из {len(docs)} документов...")
            
            # Формируем тексты для эмбеддингов (заголовок + начало контента)
            texts = []
            doc_ids = []
            for doc in docs:
                # Берём заголовок + первые 1500 символов контента
                text = f"{doc.title}. {doc.content[:1500]}"
                texts.append(text)
                doc_ids.append(doc.id)
            
            # Получаем эмбеддинги
            embeddings = self.model.encode(
                texts,
                show_progress_bar=True,
                convert_to_numpy=True,
                normalize_embeddings=True  # L2-нормализация для cosine similarity
            )
            embeddings = embeddings.astype('float32')
            
            # Создаём FAISS-индекс (Inner Product = cosine similarity для нормализованных векторов)
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatIP(dimension)
            self.index.add(embeddings)
            
            # Сохраняем ID документов
            self.doc_ids = np.array(doc_ids, dtype=np.int64)
            
            # Сохраняем индекс на диск (чтобы не перестраивать каждый раз)
            faiss.write_index(self.index, FAISS_INDEX_PATH)
            np.save(FAISS_DOCS_PATH, self.doc_ids)
            
            self._initialized = True
            print(f"✅ FAISS-индекс построен: {self.index.ntotal} векторов, размерность {dimension}")
            return True
            
        finally:
            db.close()
    
    def load_index(self):
        """Загружает существующий FAISS-индекс с диска"""
        if not os.path.exists(FAISS_INDEX_PATH):
            return False
        
        self._load_model()
        self.index = faiss.read_index(FAISS_INDEX_PATH)
        self.doc_ids = np.load(FAISS_DOCS_PATH)
        self._initialized = True
        print(f"✅ FAISS-индекс загружен: {self.index.ntotal} векторов")
        return True
    
    def search(self, query: str, top_k: int = 3) -> list:
        """
        Ищет top_k наиболее релевантных документов по запросу.
        Возвращает список объектов BitrixDoc.
        """
        if not self._initialized:
            # Пытаемся загрузить индекс, если не построен — строим
            if not self.load_index():
                if not self.build_index():
                    return []
        
        # Получаем эмбеддинг запроса
        query_embedding = self.model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True
        ).astype('float32')
        
        # Поиск в FAISS
        scores, indices = self.index.search(query_embedding, top_k)
        
        # Получаем документы по ID
        db = SessionLocal()
        try:
            results = []
            for idx, score in zip(indices[0], scores[0]):
                if idx == -1:  # FAISS возвращает -1 если не нашёл
                    continue
                doc_id = int(self.doc_ids[idx])
                doc = db.query(BitrixDoc).filter(BitrixDoc.id == doc_id).first()
                if doc:
                    results.append({
                        'doc': doc,
                        'score': float(score)
                    })
            return results
        finally:
            db.close()
    
    def get_context(self, query: str, top_k: int = 3) -> str:
        """
        Формирует контекст для LLM из найденных документов.
        """
        results = self.search(query, top_k)
        
        if not results:
            return "Документация не найдена в базе данных."
        
        context_parts = []
        for i, result in enumerate(results, 1):
            doc = result['doc']
            score = result['score']
            # Берём первые 1500 символов контента
            content = doc.content[:1500]
            context_parts.append(
                f"### Документ {i} (релевантность: {score:.3f})\n"
                f"Заголовок: {doc.title}\n"
                f"URL: {doc.url}\n"
                f"Категория: {doc.category}\n\n"
                f"{content}..."
            )
        
        return "\n\n---\n\n".join(context_parts)


# Глобальный экземпляр (синглтон)
_rag_searcher = None


def get_rag_searcher() -> RAGSearcher:
    """Возвращает глобальный экземпляр RAG-поисковика"""
    global _rag_searcher
    if _rag_searcher is None:
        _rag_searcher = RAGSearcher()
    return _rag_searcher
