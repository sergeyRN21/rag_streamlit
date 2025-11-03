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

# === Стили — точная копия вашего скриншота ===
st.markdown("""
<style>
    :root {
        --ts-cyan: #00E5D0;
        --ts-purple: #9C6BFF;
        --ts-blue: #4A90E2;
        --bg-light: #f8fbff;
        --input-bg: #1e1e2e;
        --text-dark: #333;
    }

    /* Полный фон — убираем чёрные полосы */
    .stApp {
        background: var(--bg-light);
        margin: 0;
        padding: 0;
        height: 100vh;
        overflow-y: auto;
    }

    /* Шапка: логотип + HR Консультант + градиентная линия */
    .header-container {
        display: flex;
        align-items: center;
        gap: 20px;
        margin: 40px 0 30px 0;
        padding: 0 20px;
    }

    .logo-wrapper {
        width: 120px;
    }
    .logo-wrapper img {
        height: 30px;
        object-fit: contain;
    }

    .title-wrapper {
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .title-text {
        font-size: 2.8em;
        font-weight: bold;
        color: var(--text-dark);
        line-height: 1.1;
    }

    .gradient-line {
        height: 3px;
        width: 300px;
        background: linear-gradient(90deg, var(--ts-cyan), var(--ts-purple), var(--ts-blue));
        border-radius: 2px;
    }

    /* Подзаголовок */
    .subtitle {
        color: #aaa;
        font-size: 0.9em;
        text-align: center;
        margin: 0 20px 40px;
    }

    /* Сообщения чата */
    .stChatMessage {
        background: white;
        border-radius: 12px;
        padding: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 10px;
    }
    .stChatMessage.user {
        background: #e3f2fd;
        border-left: 4px solid var(--ts-blue);
    }
    .stChatMessage.assistant {
        background: #f3fdfa;
        border-left: 4px solid var(--ts-cyan);
    }

    /* Инпут внизу — тёмная панель */
    .input-container {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: var(--input-bg);
        padding: 15px 20px;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
        z-index: 1000;
    }

    .input-field {
        display: flex;
        align-items: center;
        background: #2d2d3d;
        border-radius: 30px;
        padding: 0 15px;
        height: 50px;
        width: 100%;
    }

    .input-field input {
        background: transparent;
        border: none;
        color: white;
        font-size: 1em;
        flex-grow: 1;
        outline: none;
        padding: 0 10px;
    }

    .input-field button {
        background: transparent;
        border: none;
        color: white;
        font-size: 1.2em;
        cursor: pointer;
        padding: 0 10px;
    }

    .input-field button:hover {
        color: var(--ts-cyan);
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

# === Настройка страницы ===
st.set_page_config(page_title="HR Консультант — TrafficSoft", page_icon="💼")

# === Шапка: логотип + HR Консультант + градиентная линия ===
if logo_b64:
    st.markdown(f'''
    <div class="header-container">
        <div class="logo-wrapper">
            <img src="data:image/png;base64,{logo_b64}" alt="TrafficSoft Logo">
        </div>
        <div class="title-wrapper">
            <div class="title-text">HR<br>Консультант</div>
            <div class="gradient-line"></div>
        </div>
    </div>
    ''', unsafe_allow_html=True)
else:
    st.markdown('<div class="header-container"><div class="title-wrapper"><div class="title-text">HR<br>Консультант</div><div class="gradient-line"></div></div></div>', unsafe_allow_html=True)

# === Подзаголовок ===
st.markdown('<p class="subtitle">Задайте вопрос по HR-политике компании: отпуска, бонусы, remote work, адаптация и др.</p>', unsafe_allow_html=True)

# === Инициализация чата ===
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Привет! Я помогу вам с вопросами по HR-политике TrafficSoft. Спрашивайте!"}
    ]

# === Отображение истории ===
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# === Фиксированное поле ввода внизу ===
st.markdown('<div class="input-container">', unsafe_allow_html=True)

with st.form(key="chat_form", clear_on_submit=True):
    col1, col2 = st.columns([9, 1])
    with col1:
        prompt = st.text_input("", placeholder="Ваш вопрос по HR", label_visibility="collapsed")
    with col2:
        submit_button = st.form_submit_button("➤", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# === Обработка запроса ===
if submit_button and prompt.strip():
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

    # Прокрутка вниз (не работает в Streamlit, но можно обновить через релоад)
    st.rerun()