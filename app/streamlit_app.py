# streamlit_app.py — редизайн под TrafficSoft
import streamlit as st
from rag_core import TrafficSoftRAG

# Настройка страницы
st.set_page_config(
    page_title="TrafficSoft — Внутренний ассистент",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS для стиля TrafficSoft
st.markdown("""
<style>
/* Белый фон */
body {
    background-color: white;
    color: #333;
}

/* Заголовки */
h1, h2, h3 {
    color: #333;
    font-weight: 600;
}

/* Кнопка отправки */
.stButton>button {
    background-color: #00D1D1; /* Туркоазовый цвет из сайта */
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 20px;
    font-weight: bold;
    transition: background-color 0.3s;
}

.stButton>button:hover {
    background-color: #00B8B8;
}

/* Поле ввода */
input[type="text"] {
    border: 1px solid #ddd;
    border-radius: 20px;
    padding: 10px;
    font-size: 16px;
}

/* Сообщения чата */
.chat-message {
    padding: 10px;
    margin: 5px 0;
    border-radius: 10px;
    max-width: 80%;
}

.chat-message.user {
    background-color: #f0f0f0;
    align-self: flex-end;
    margin-left: auto;
}

.chat-message.assistant {
    background-color: #e8f8f8;
    align-self: flex-start;
}
</style>
""", unsafe_allow_html=True)

# Логотип и заголовок
col1, col2 = st.columns([1, 4])
with col1:
    # Если есть файл logo.png — разместите его в папке app/
    st.image("logo.png", width=80)
    
with col2:
    st.title("🤖 Внутренний ассистент TrafficSoft")
    st.markdown("Задайте вопрос по внутренним регламентам — получите точный ответ с цитированием.")

# Приветствие
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Здравствуйте! Я помогу найти информацию в ваших внутренних документах."}
    ]

# Отображение истории
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Ввод пользователя
if prompt_input := st.chat_input("Ваш вопрос"):
    st.session_state.messages.append({"role": "user", "content": prompt_input})
    with st.chat_message("user"):
        st.markdown(prompt_input)

    with st.chat_message("assistant"):
        with st.spinner("Ищу в регламентах..."):
            try:
                # Получаем RAG-цепочку (если ещё не создана)
                @st.cache_resource
                def get_rag_chain():
                    rag = TrafficSoftRAG()
                    return rag.create_rag_chain()

                rag_chain, _ = get_rag_chain()
                response = rag_chain.invoke(prompt_input)
            except Exception as e:
                response = f"Ошибка: {str(e)}"
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})