# rag_core.py
import os
import regex as re
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

def parse_constitution(text: str):
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

def create_rag_chain_and_retriever():
    with open("data/constitution_rf.txt", "r", encoding="utf-8") as f:
        full_text = f.read()

    parsed_articles = parse_constitution(full_text)
    documents = [
        Document(page_content=art["text"], metadata=art["metadata"])
        for art in parsed_articles
    ]

    embeddings = HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-large")
    vectorstore = FAISS.from_documents(documents, embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    llm = ChatOpenAI(
        model="google/gemini-2.0-flash-001",
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        temperature=0.1,
        max_tokens=512,
    )

    prompt = ChatPromptTemplate.from_template(
        """Ты — юрист, отвечающий строго по Конституции РФ.
Контекст: {context}
Вопрос: {question}
Ответь кратко. Обязательно укажи номер статьи.
Если в контексте нет ответа — скажи: "Я не знаю".
"""
    )

    # Цепочка
    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return rag_chain, retriever