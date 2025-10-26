import os
import streamlit as st
from rag_core import ConstitutionRag 

@st.cache_resource
def get_rag_chain():
    rag = ConstitutionRag()
    rag_chain, retriever = rag.create_rag_chain()
    return rag_chain, retriever

rag_chain, retriever = get_rag_chain()

st.set_page_config(page_title="Digital Lawyer", page_icon="⚖️")
st.title("⚖️ Digital Lawyer — Консультант по Конституции РФ")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Здравствуйте! Задайте вопрос по Конституции РФ."}
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt_input := st.chat_input("Ваш вопрос"):
    st.session_state.messages.append({"role": "user", "content": prompt_input})
    with st.chat_message("user"):
        st.markdown(prompt_input)

    with st.chat_message("assistant"):
        with st.spinner("Ищу в Конституции..."):
            try:
                response = rag_chain.invoke(prompt_input)
            except Exception as e:
                response = f"Ошибка: {str(e)}"
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})