import streamlit as st
from rag_core import TrafficSoftRAG
import base64

# Загружаем логотип
def load_logo_base64(path="logo.png"):
    try:
        with open(path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        st.warning("⚠️ logo.png не найден. Поместите его в корень проекта.")
        return None

logo_b64 = load_logo_base64()

# === Стили в стиле TrafficSoft ===
st.markdown("""
<style>
    :root {
        --ts-cyan: #00E5D0;
        --ts-purple: #9C6BFF;
        --ts-blue: #4A90E2;
        --user-bg: #e3f2fd;
        --assistant-bg: #f3fdfa;
    }

    /* Градиентный фон */
    .stApp {
        background: linear-gradient(135deg, #ffffff 0%, #f0f8ff 100%);
    }

    /* Логотип в заголовке */
    .logo-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 20px;
    }
    .logo-header img {
        height: 36px;
    }
    .logo-header h1 {
        color: #333;
        font-weight: 700;
        margin: 0;
    }

    /* Градиентная линия под заголовком */
    .logo-header::after {
        content: '';
        display: block;
        width: 100%;
        height: 3px;
        background: linear-gradient(90deg, var(--ts-cyan), var(--ts-purple), var(--ts-blue));
        margin-top: 8px;
        border-radius: 2px;
    }

    /* Сообщения чата */
    .stChatMessage.user {
        background-color: var(--user-bg);
        border-left: 4px solid var(--ts-blue);
    }
    .stChatMessage.assistant {
        background-color: var(--assistant-bg);
        border-left: 4px solid var(--ts-cyan);
    }

    /* Кнопки */
    .stButton > button {
        background: linear-gradient(90deg, var(--ts-cyan), var(--ts-purple));
        color: white;
        border: none;
        border-radius: 20px;
        font-weight: 600;
        padding: 8px 20px;
    }
    .stButton > button:hover {
        transform: scale(1.03);
        box-shadow: 0 4px 10px rgba(0, 229, 208, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# === Инициализация RAG ===
@st.cache_resource
def get_rag_chain():
    rag = TrafficSoftRAG()
    rag_chain, _ = rag.create_rag_chain()
    return rag_chain

rag_chain = get_rag_chain()

# === Заголовок с логотипом ===
st.set_page_config(page_title="HR Консультант — TrafficSoft", page_icon="💼")

if logo_b64:
    st.markdown(f'''
    <div class="logo-header">
        <img src="data:image/png;base64,{logo_b64}" alt="TrafficSoft Logo">
        <h1>HR Консультант</h1>
    </div>
    ''', unsafe_allow_html=True)
else:
    st.title("💼 HR Консультант — TrafficSoft")

st.markdown("Задайте вопрос по HR-политике компании: отпуска, бонусы, remote work, адаптация и др.")

# === Инициализация чата ===
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Привет! Я помогу вам с вопросами по HR-политике TrafficSoft. Спрашивайте!"}
    ]

# === Отображение истории ===
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# === Ввод и ответ ===
if prompt := st.chat_input("Ваш вопрос по HR"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Ищу в HR-документах..."):
            try:
                response = rag_chain.invoke(prompt)
            except Exception as e:
                response = f"⚠️ Ошибка: {str(e)}"
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})