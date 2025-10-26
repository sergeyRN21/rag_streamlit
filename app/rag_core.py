import os
import regex as re
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough


class ConstitutionRag:
    def __init__(self, 
                file_path="data/constitution_rf.txt",
                k=3, 
                embedding_model="intfloat/multilingual-e5-large", 
                llm_model="google/gemini-2.0-flash-001",
                base_url="https://openrouter.ai/api/v1",
                api_key="OPENROUTER_API_KEY",
                temperature=0.1,
                max_tokens=512
                ):
        self.file_path = file_path
        self.k = k
        self.embedding_model = embedding_model
        self.llm_model = llm_model
        self.base_url = base_url
        self.api_key = api_key
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._full_text = None
        self._parsed_articles = None
        self._documents = None
        self._embeddings = None
        self._vectorstore = None

    def _load_text(self):
        if self._full_text is None:
            with open(self.file_path, "r", encoding="utf-8") as f:
                self._full_text = f.read()
        return self._full_text
    
    @staticmethod
    def parsed_articles(text):
        articles = []
        parts = re.split(r'\n(?=Статья \d+)', text)
        for part in parts:
            if "Статья" in part:
                match = re.search(r'Статья (\d+)', part)
                if match:
                    article_num = int(match.group(1))
                    articles.append({
                        "text": part.strip(),
                        "metadata": {"article": article_num, "doc_type": "constitution"}
                    })
        return articles

    def _get_parsed_articles(self):
        if self._parsed_articles is None:
            full_text = self._load_text()
            self._parsed_articles = self.parsed_articles(full_text)
        return self._parsed_articles
    

    def _get_documents(self):
        if self._documents is None:
            parsed_articles = self._get_parsed_articles()
            self._documents = [
                Document(page_content=art["text"], metadata=art["metadata"])
                for art in parsed_articles
            ]
        return self._documents
    
    def _get_embeddings(self):
        if self._embeddings is None:
            self._embeddings = HuggingFaceEmbeddings(model_name=self.embedding_model)
        return self._embeddings

    def _get_vectorstore(self):
        if self._vectorstore is None:
            documents = self._get_documents()
            embeddings = self._get_embeddings()
            self._vectorstore = FAISS.from_documents(documents, embeddings)
        return self._vectorstore
    
    def create_rag_chain(self, llm_model: str, k: int = 3) -> tuple:
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": k})

        llm = ChatOpenAI(
            model=llm_model,
            base_url=self.base_url,
            api_key=os.getenv(self.api_key),
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )

        prompt = ChatPromptTemplate.from_template(
            """Ты — юрист, отвечающий строго по Конституции РФ.
Контекст: {context}
Вопрос: {question}
Ответь кратко. Обязательно укажи номер статьи.
Если в контексте нет ответа — скажи: "Я не знаю".
"""
        )

        rag_chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
        return rag_chain, retriever