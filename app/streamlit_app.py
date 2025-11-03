import streamlit as st
from rag_core import TrafficSoftRAG  # Убедитесь, что этот модуль существует

# Кастомный CSS — стиль TrafficSoft
st.markdown("""
<style>
    :root {
        --ts-cyan: #00E5D0;
        --ts-purple: #9C6BFF;
        --ts-blue: #4A90E2;
        --ts-gray: #333333;
    }

    /* Фон */
    .stApp {
        background: linear-gradient(135deg, #ffffff 0%, #f0f8ff 50%, #e6f7ff 100%);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Шапка */
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 15px 20px;
        border-bottom: 1px solid #eee;
        background: white;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }

    .header-logo {
        display: flex;
        align-items: center;
        gap: 10px;
        font-weight: bold;
        font-size: 1.3em;
        color: var(--ts-gray);
    }

    .nav-menu {
        display: flex;
        gap: 20px;
        font-weight: 500;
        color: var(--ts-gray);
    }

    .nav-menu a {
        text-decoration: none;
        color: var(--ts-gray);
        transition: color 0.2s;
    }

    .nav-menu a:hover {
        color: var(--ts-blue);
    }

    .contact-button {
        background: linear-gradient(90deg, var(--ts-cyan), var(--ts-purple));
        color: white;
        border: none;
        padding: 8px 20px;
        border-radius: 20px;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
    }

    .contact-button:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 12px rgba(0, 229, 208, 0.3);
    }

    /* Заголовок с градиентной линией */
    .title-with-line {
        position: relative;
        padding-bottom: 10px;
        font-size: 2.2em;
        font-weight: bold;
        color: var(--ts-gray);
    }
    .title-with-line::after {
        content: '';
        position: absolute;
        left: 0;
        bottom: 0;
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, var(--ts-cyan), var(--ts-purple), var(--ts-blue));
        border-radius: 2px;
    }

    /* Сообщения чата */
    .stChatMessage {
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 8px;
        background-color: #f8f9fa;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .stChatMessage.user {
        background-color: #e3f2fd;
        border-left: 4px solid var(--ts-blue);
    }
    .stChatMessage.assistant {
        background-color: #f3fdfa;
        border-left: 4px solid var(--ts-cyan);
    }

    /* Кнопки в чате */
    .stButton > button {
        background: linear-gradient(90deg, var(--ts-cyan), var(--ts-purple));
        color: white;
        border-radius: 20px;
        border: none;
        padding: 8px 16px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 12px rgba(0, 229, 208, 0.3);
    }

</style>
""", unsafe_allow_html=True)

# Инициализация RAG
@st.cache_resource
def get_rag_chain():
    rag = TrafficSoftRAG()
    rag_chain, retriever = rag.create_rag_chain()
    return rag_chain, retriever

rag_chain, retriever = get_rag_chain()

# Настройка страницы
st.set_page_config(page_title="TrafficSoft — HR Консультант", page_icon="💼")

# Шапка в стиле TrafficSoft
st.markdown("""
<div class="header-container">
    <div class="header-logo">
        <img src="data:image/png;base64,{logo_base64}" width="120" style="margin-right: 10px;">
        <span>TrafficSoft</span>
    </div>
    <div class="nav-menu">
        <a href="#">CGNAT</a>
        <a href="#">ADC</a>
        <a href="#">Проекты</a>
        <a href="#">Новости</a>
        <a href="#">Блог</a>
        <a href="#">О компании</a>
        <a href="#">Партнерам</a>
        <a href="#">Поддержка</a>
    </div>
    <button class="contact-button">Связаться с нами</button>
</div>
""", unsafe_allow_html=True)

# Загрузка логотипа из файла logo.png
import base64
with open("logo.png", "rb") as f:
    logo_data = f.read()
    logo_base64 = base64.b64encode(logo_data).decode()

# Обновляем шапку с реальным логотипом
st.markdown(f"""
<div class="header-container">
    <div class="header-logo">
        <img src="data:image/png;base64,{logo_base64}" width="120" style="margin-right: 10px;">
        <span>TrafficSoft</span>
    </div>
    <div class="nav-menu">
        <a href="#">CGNAT</a>
        <a href="#">ADC</a>
        <a href="#">Проекты</a>
        <a href="#">Новости</a>
        <a href="#">Блог</a>
        <a href="#">О компании</a>
        <a href="#">Партнерам</a>
        <a href="#">Поддержка</a>
    </div>
    <button class="contact-button">Связаться с нами</button>
</div>
""", unsafe_allow_html=True)

# Основной заголовок
st.markdown('<h1 class="title-with-line">HR Консультант TrafficSoft</h1>', unsafe_allow_html=True)

# Подзаголовок
st.markdown("""
<p style="color: #777; font-size: 1.1em; line-height: 1.6;">
Задайте вопрос по HR-политике компании — от оплаты труда до отпусков и корпоративной культуры.
Мы поможем вам быстро найти ответ в официальных документах.
</p>
""", unsafe_allow_html=True)

# Кнопка "Узнать о продуктах" — можно заменить на "HR-документы"
if st.button("Посмотреть HR-документы"):
    st.info("Это демонстрационная кнопка. В реальном приложении здесь может быть ссылка на внутренний портал.")

# Разделитель
st.markdown("---")

# Чат-интерфейс
st.subheader("💬 Задайте вопрос по HR-политике")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Привет! Я — ваш HR-консультант. Спрашивайте всё, что интересует: оплата, отпуска, командировки, адаптация и т.д."}
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt_input := st.chat_input("Ваш вопрос"):
    st.session_state.messages.append({"role": "user", "content": prompt_input})
    with st.chat_message("user"):
        st.markdown(prompt_input)

    with st.chat_message("assistant"):
        with st.spinner("Ищу в HR-документах..."):
            try:
                response = rag_chain.invoke(prompt_input)
            except Exception as e:
                response = f"Ошибка: {str(e)}"
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
