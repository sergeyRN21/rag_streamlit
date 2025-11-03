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

# === Стили — точная копия вашего дизайна ===
st.markdown("""
<style>
    :root {
        --ts-cyan: #00E5D0;
        --ts-purple: #9C6BFF;
        --ts-blue: #4A90E2;
        --bg-light: #f8fbff;
        --input-bg: #00E5D0;
        --text-dark: #333;
        --text-light: #777;
        --chat-bg: white;
        --avatar-bg: #ff7a00;
    }

    /* Полный фон */
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
        margin: 40px 0 20px 0;
        padding: 0 20px;
    }

    .logo-wrapper {
        width: 150px;
    }
    .logo-wrapper img {
        height: 40px;
        object-fit: contain;
    }

    .title-wrapper {
        display: flex;
        flex-direction: column;
        gap: 5px;
    }

    .title-main {
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
        margin-top: 10px;
    }

    /* Подзаголовок */
    .subtitle {
        color: var(--text-light);
        font-size: 0.9em;
        text-align: center;
        margin: 0 20px 30px;
    }

    /* Сообщение ассистента — один блок с аватаром */
    .assistant-message {
        display: flex;
        align-items: flex-start;
        gap: 10px;
        background: var(--chat-bg);
        border-radius: 12px;
        padding: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin: 20px 20px 30px;
    }

    .avatar {
        width: 36px;
        height: 36px;
        background: var(--avatar-bg);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 16px;
    }

    .message-content {
        flex-grow: 1;
        color: var(--text-dark);
        font-size: 1em;
        line-height: 1.5;
    }

    /* Поле ввода — бирюзовое с белым текстом */
    .input-container {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: var(--bg-light);
        padding: 15px 20px;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.05);
        z-index: 1000;
    }

    .input-field {
        display: flex;
        align-items: center;
        background: var(--input-bg);
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
        color: #fff;
        transform: scale(1.1);
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
            <div class="title-main">HR<br>Консультант</div>
            <div class="gradient-line"></div>
        </div>
    </div>
    ''', unsafe_allow_html=True)
else:
    st.markdown('<div class="header-container"><div class="title-wrapper"><div class="title-main">HR<br>Консультант</div><div class="gradient-line"></div></div></div>', unsafe_allow_html=True)

# === Подзаголовок ===
st.markdown('<p class="subtitle">Задайте вопрос по HR-политике компании: отпуска, бонусы, remote work, адаптация и др.</p>', unsafe_allow_html=True)

# === Приветственное сообщение — одно, без дублей ===
st.markdown(f'''
<div class="assistant-message">
    <div class="avatar">🤖</div>
    <div class="message-content">Привет! Я помогу вам с вопросами по HR-политике TrafficSoft. Спрашивайте!</div>
</div>
''', unsafe_allow_html=True)

# === Инициализация чата ===
if "messages" not in st.session_state:
    st.session_state.messages = []

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
    # Добавляем сообщение пользователя в историю
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Отображаем сообщение пользователя (если нужно — можно убрать, оставив только ответ)
    # st.markdown(f'<div class="assistant-message" style="background:#e3f2fd;"><div class="avatar">👤</div><div class="message-content">{prompt}</div></div>', unsafe_allow_html=True)

    # Получаем ответ от LLM
    with st.spinner("Ищу в HR-документах..."):
        try:
            response = rag_chain.invoke(prompt)
        except Exception as e:
            response = f"⚠️ Ошибка: {str(e)}"

    # Добавляем ответ в историю
    st.session_state.messages.append({"role": "assistant", "content": response})

    # Отображаем ответ — один раз, без дубля
    st.markdown(f'''
    <div class="assistant-message">
        <div class="avatar">🤖</div>
        <div class="message-content">{response}</div>
    </div>
    ''', unsafe_allow_html=True)

    # Прокрутка вниз (Streamlit не поддерживает JS-скролл, но можно обновить)
    st.rerun()