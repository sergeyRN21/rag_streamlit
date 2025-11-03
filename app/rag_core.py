# rag_core.py
import os
import pdfplumber
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

load_dotenv()

class TrafficSoftRAG:
    def __init__(self,
                 file_path="data/hr_policy.pdf",
                 k=3,
                 embedding_model="BAAI/bge-m3",
                 llm_model="google/gemini-2.0-flash-exp",
                 openrouter_api_key=None,
                 temperature=0.1,
                 max_tokens=512
                 ):
        self.file_path = file_path
        self.k = k
        self.embedding_model = embedding_model
        self.llm_model = llm_model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.openrouter_api_key = openrouter_api_key or os.getenv("OPENROUTER_API_KEY")
        
        # Кэшируемые атрибуты
        self._full_text = None
        self._documents = None
        self._embeddings = None
        self._vectorstore = None

    def _load_text(self):
        """Извлекает текст из PDF-файла"""
        if self._full_text is None:
            full_text = ""
            try:
                with pdfplumber.open(self.file_path) as pdf:
                    for page in pdf.pages:
                        text = page.extract_text()
                        if text:
                            full_text += text + "\n"
            except Exception as e:
                raise ValueError(f"Не удалось прочитать PDF: {e}")
            self._full_text = full_text
        return self._full_text

    def _get_documents(self):
        """Разбивает текст на чанки и создаёт Document-объекты"""
        if self._documents is None:
            text = self._load_text()
            if not text.strip():
                raise ValueError("PDF-файл пуст или не содержит текста")

            splitter = RecursiveCharacterTextSplitter(
                chunk_size=400,
                chunk_overlap=50,
                separators=["\n\n", "\n", ". ", " "]
            )
            chunks = splitter.split_text(text)
            self._documents = [
                Document(
                    page_content=chunk,
                    metadata={"source": os.path.basename(self.file_path), "chunk_id": i}
                )
                for i, chunk in enumerate(chunks)
            ]
        return self._documents

    def _get_embeddings(self):
        if self._embeddings is None:
            self._embeddings = HuggingFaceEmbeddings(model_name=self.embedding_model, encode_kwargs={'normalize_embeddings': True})
        return self._embeddings

    def _get_vectorstore(self):
        if self._vectorstore is None:
            documents = self._get_documents()
            embeddings = self._get_embeddings()
            self._vectorstore = FAISS.from_documents(documents, embeddings)
        return self._vectorstore

    def create_rag_chain(self, llm_model: str = None, k: int = None):
        """
        Создаёт RAG-цепочку.
        Возвращает (chain, retriever)
        """
        if llm_model is None:
            llm_model = self.llm_model
        if k is None:
            k = self.k

        vectorstore = self._get_vectorstore()
        retriever = vectorstore.as_retriever(search_kwargs={"k": k})

        # Используем OpenRouter через совместимость с OpenAI API
        llm = ChatOpenAI(
            model=llm_model,
            base_url="https://openrouter.ai/api/v1",
            api_key=self.openrouter_api_key,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )

        # Промпт: строго по документу, с запретом на галлюцинации
        prompt = ChatPromptTemplate.from_template(
            """Ты — внутренний ассистент компании TrafficSoft. Отвечай строго на основе предоставленного контекста.
Контекст: {context}
Вопрос: {question}

Правила:
1. Если ответ есть в контексте — дай краткий, точный ответ.
2. Обязательно укажи, откуда информация (например: «Согласно разделу 4.3 регламента»).
3. Если в контексте нет ответа — скажи: «Информация по этому вопросу отсутствует в регламентах. Обратитесь в HR.»
4. Никогда не выдумывай.
"""
        )

        rag_chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
        return rag_chain, retriever