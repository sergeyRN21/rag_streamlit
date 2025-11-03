import streamlit as st
from rag_core import TrafficSoftRAG 
import base64

# --- Загрузка изображения в base64 ---
def get_image_as_base64(image_path: str) -> str:
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        st.warning(f"Файл {image_path} не найден.")
        return ""

# --- Стилизация: логотип + цвета текста + фон чат-сообщений ---
def inject_styles(logo_path: str = "logo.png"):
    logo_b64 = get_image_as_base64(logo_path)
    
    st.markdown(
        f"""
        <style>
        /* Белый фон всего приложения */
        .stApp {{
            background-color: white;
        }}

        /* Цвет основного текста — тёмно-серый */
        .stApp, .stMarkdown, .stTitle, p, div {{
            color: #222222 !important;
        }}

        /* Логотип с фоном и отступами */
        .logo-badge {{
            position: absolute;
            top: 1rem;
            left: 1rem;
            z-index: 999;
            display: flex;
            align-items: center;
            gap: 0.6rem;
            background: rgba(255, 255, 255, 0.9);
            padding: 0.5rem 1rem;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            font-weight: 600;
            font-size: 16px;
            color: #1a1a1a;
        }}
        .logo-badge img {{
            height: 28px;
        }}

        /* Отступ для всего контента, чтобы не перекрывался логотипом */
        .main-wrapper {{
            margin-top: 4.5rem;
        }}

        /* Стили сообщений чата */
        .stChatMessage[data-testid="chat-message-user"] {{
            background-color: #f0f4ff;
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 0.8rem;
        }}
        .stChatMessage[data-testid="chat-message-assistant"] {{
            background-color: #f9f9f9;
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 0.8rem;
        }}

        /* Поле ввода — тёмная рамка для контраста */
        .stChatInput textarea {{
            color: #222222;
            background-color: white;
            border: 1px solid #ddd;
            border-radius: 12px;
            padding: 0.6rem;
        }}
        </style>

        <!-- Логотип с текстом -->
        <div class="logo-badge">
            <img src="data:image/png;base64,{logo_b64}" alt="Logo">
            <span>TrafficSoft</span>
        </div>
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
st.set_page_config(page_title="Traffic Soft", layout="wide")

# Применяем стили
inject_styles("logo.png")  # ← укажи путь к твоему логотипу

# Обёртка с отступом сверху
st.markdown('<div class="main-wrapper">', unsafe_allow_html=True)

st.title("HR consultant")

# История сообщений
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Задайте вопрос по HR-политике компании: отпуска, бонусы, remote work, адаптация и др."}
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Ввод пользователя
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

st.markdown('</div>', unsafe_allow_html=True)