import streamlit as st
from rag_core import TrafficSoftRAG 

@st.cache_resource
def get_rag_chain():
    rag = TrafficSoftRAG()
    rag_chain, retriever = rag.create_rag_chain()
    return rag_chain, retriever

rag_chain, retriever = get_rag_chain()

# Установка конфигурации страницы
st.set_page_config(
    page_title="Traffic Soft HR Consultant",
    page_icon="💼",  # можно заменить на путь к иконке, если есть
    layout="centered"
)

# Добавление логотипа в шапку страницы
st.logo("logo.png", size="medium")  # убедитесь, что logo.png в корне проекта

# Заголовок
st.title("HR consultant")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Задайте вопрос по HR-политике компании: отпуска, бонусы, remote work, адаптация и др."}
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt_input := st.chat_input("Ваш вопрос"):
    st.session_state.messages.append({"role": "user", "content": prompt_input})
    with st.chat_message("user"):
        st.markdown(prompt_input)

    with st.chat_message("assistant"):
        with st.spinner("Ищу в HR политике..."):
            try:
                response = rag_chain.invoke(prompt_input)
            except Exception as e:
                response = f"Ошибка: {str(e)}"
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})