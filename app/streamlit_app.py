import os
import streamlit as st
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.documents import Document

import regex as re
# Загрузка переменных окружения

# Инициализация LLM через OpenRouter
llm = ChatOpenAI(
    model="google/gemini-2.0-flash-001",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    temperature=0.1,
    max_tokens=512,
)

# Промпт
prompt = ChatPromptTemplate.from_template(
    """Ты — юрист, отвечающий строго по Конституции РФ.
Контекст: {context}
Вопрос: {question}
Ответь кратко. Обязательно укажи номер статьи.
Если в контексте нет ответа — скажи: "Я не знаю".
"""
)

def parse_constitution(text: str):
    articles = []
    # Разделяем по "Статья N"
    parts = re.split(r'\n(?=Статья \d+)', text)
    for part in parts:
        if "Статья" in part:
            # Извлекаем номер статьи
            match = re.search(r'Статья (\d+)', part)
            if match:
                article_num = int(match.group(1))
                articles.append({
                    "text": part.strip(),
                    "metadata": {"article": article_num, "doc_type": "constitution"}
                })
    return articles

# Кэшированная инициализация RAG-цепочки
@st.cache_resource
def create_rag_chain():
    # Загрузка и разбиение
    loader = TextLoader("data/constitution_rf.txt", encoding="utf-8")
    docs = loader.load()
    documents = [
        Document(page_content=art["text"], metadata=art["metadata"])
        for art in parse_constitution(docs)
    ]

    # Векторная БД
    embeddings = HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-large")
    vectorstore = FAISS.from_documents(documents, embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    # Цепочка
    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return rag_chain

# Создание цепочки (выполняется один раз)
rag_chain = create_rag_chain()

# Streamlit UI
st.set_page_config(page_title="Digital Lawyer", page_icon="⚖️")
st.title("⚖️ Digital Lawyer — Консультант по Конституции РФ")

# История чата
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Здравствуйте! Задайте вопрос по Конституции РФ."}
    ]

# Отображение истории
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Обработка ввода
if prompt_input := st.chat_input("Ваш вопрос"):
    # Добавить вопрос пользователя
    st.session_state.messages.append({"role": "user", "content": prompt_input})
    with st.chat_message("user"):
        st.markdown(prompt_input)

    # Генерация ответа
    with st.chat_message("assistant"):
        with st.spinner("Ищу в Конституции..."):
            try:
                response = rag_chain.invoke(prompt_input)
            except Exception as e:
                response = f"Ошибка: {str(e)}"
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

# Создание цепочки (выполняется один раз)
rag_chain = create_rag_chain()

# Streamlit UI
st.set_page_config(page_title="Digital Lawyer", page_icon="⚖️")
st.title("⚖️ Digital Lawyer — Консультант по Конституции РФ")

# История чата
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Здравствуйте! Задайте вопрос по Конституции РФ."}
    ]

# Отображение истории
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Обработка ввода
if prompt_input := st.chat_input("Ваш вопрос"):
    # Добавить вопрос пользователя
    st.session_state.messages.append({"role": "user", "content": prompt_input})
    with st.chat_message("user"):
        st.markdown(prompt_input)

    # Генерация ответа
    with st.chat_message("assistant"):
        with st.spinner("Ищу в Конституции..."):
            try:
                response = rag_chain.invoke(prompt_input)
            except Exception as e:
                response = f"Ошибка: {str(e)}"
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})