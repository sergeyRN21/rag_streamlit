import streamlit as st
from rag_core import TrafficSoftRAG 
import base64

# --- Функция для загрузки логотипа ---
def get_image_as_base64(image_path: str) -> str:
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        return ""

# --- Внедрение стилей + JS для плавной прокрутки ---
def inject_beautiful_ui(logo_path: str = "logo.png"):
    logo_b64 = get_image_as_base64(logo_path)
    
    # Если логотип не найден — используем текстовый вариант
    if not logo_b64:
        logo_html = '<span style="font-weight: 600; font-size: 14px;">TrafficSoft</span>'
    else:
        logo_html = f'<img src="image/png;base64,{logo_b64}" alt="Logo" style="height: 24px; margin-right: 8px;">'

    st.markdown(
        f"""
        <style>
        /* Белый фон */
        .stApp {{
            background-color: white;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }}

        /* Логотип в углу — компактный, с тенью */
        .app-header {{
            position: fixed;
            top: 1rem;
            left: 1.5rem;
            z-index: 999;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.4rem 0.8rem;
            background: linear-gradient(135deg, #ffffff, #fafafa);
            border-radius: 16px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
            font-weight: 600;
            font-size: 14px;
            color: #1a1a1a;
            transition: all 0.2s ease;
        }}
        .app-header:hover {{
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }}

        /* Основной контент — центрирован, с отступами */
        .main-container {{
            max-width: 800px;
            margin: 5rem auto 2rem;
            padding: 0 1rem;
        }}

        /* Заголовок */
        h1 {{
            font-size: 28px;
            font-weight: 700;
            color: #222;
            margin-bottom: 1rem;
            line-height: 1.3;
        }}

        /* Сообщения */
        .stChatMessage[data-testid="chat-message-user"] {{
            background: #eef5ff;
            border-left: 4px solid #007bff;
            border-radius: 12px;
            padding: 0.8rem 1rem;
            margin: 0.5rem 0;
        }}
        .stChatMessage[data-testid="chat-message-assistant"] {{
            background: #f8f8f8;
            border-left: 4px solid #6c757d;
            border-radius: 12px;
            padding: 0.8rem 1rem;
            margin: 0.5rem 0;
        }}

        /* Поле ввода — красивое, с анимацией */
        .stChatInput textarea {{
            border: 1px solid #ddd;
            border-radius: 16px;
            padding: 0.8rem 1rem;
            font-size: 16px;
            transition: border 0.2s ease, box-shadow 0.2s ease;
            background: white;
            color: #222;
        }}
        .stChatInput textarea:focus {{
            border-color: #007bff;
            box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.1);
        }}

        /* Кнопка отправки — скрыта, но работает */
        .stChatInput button {{
            opacity: 0.8;
            transition: opacity 0.2s;
        }}
        .stChatInput button:hover {{
            opacity: 1;
        }}
        </style>

        <!-- Логотип -->
        <div class="app-header">
            {logo_html}
            <span>TrafficSoft</span>
        </div>

        <!-- JS: плавная прокрутка к последнему сообщению -->
        <script>
        function scrollToBottom() {{
            const container = document.querySelector('.main-container');
            if (container) {{
                container.scrollTop = container.scrollHeight;
            }}
        }}
        // Запуск при загрузке и после каждого нового сообщения
        setTimeout(scrollToBottom, 300);
        </script>
        """,
        unsafe_allow_html=True,
    )

# --- Инициализация RAG ---
@st.cache_resource
def get_rag_chain():
    rag = TrafficSoftRAG()
    rag_chain, retriever = rag.create_rag_chain()
    return rag_chain, retriever

rag_chain, retriever = get_rag_chain()

# --- Настройка страницы ---
st.set_page_config(page_title="Traffic Soft", layout="centered")

# Применяем стиль
inject_beautiful_ui("logo.png")  # ← замени на свой путь

# Обёртка основного контента
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Заголовок
st.title("HR consultant")

# Приветственное сообщение
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Задайте вопрос по HR-политике компании: отпуска, бонусы, remote work, адаптация и др."}
    ]

# Отображаем сообщения
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Поле ввода
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

    # Плавная прокрутка к новому сообщению
    st.markdown(
        """
        <script>
        setTimeout(() => {
            const container = document.querySelector('.main-container');
            if (container) {
                container.scrollTop = container.scrollHeight;
            }
        }, 100);
        </script>
        """,
        unsafe_allow_html=True,
    )

st.markdown('</div>', unsafe_allow_html=True)