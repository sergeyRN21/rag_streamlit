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
from rag_core import create_rag_chain

import regex as re
# Загрузка переменных окружения

@st.cache_resource
def get_rag_chain():
    return create_rag_chain()

rag_chain = get_rag_chain()

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