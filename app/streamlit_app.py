import streamlit as st
from rag_core import TrafficSoftRAG 

# --- Настройка стилей и логотипа ---
def inject_custom_css_and_logo(logo_path: str = "logo.png"):
    st.markdown(
        f"""
        <style>
        /* Белый фон для всего приложения */
        .stApp {{
            background-color: white;
        }}

        /* Скрыть стандартный заголовок Streamlit, если нужно */
        header[data-testid="stHeader"] {{
            display: none;
        }}

        /* Контейнер для логотипа в левом верхнем углу */
        .logo-container {{
            position: fixed;
            top: 1rem;
            left: 1rem;
            z-index: 999;
        }}
        .logo-container img {{
            height: 40px; /* регулируйте по желанию */
        }}
        </style>
        <div class="logo-container">
            <img src="data:image/png;base64,{get_image_as_base64(logo_path)}" alt="Logo">
        </div>
        """,
        unsafe_allow_html=True,
    )

# Функция для загрузки изображения в base64 (поддерживает PNG и JPG)
import base64

def get_image_as_base64(image_path: str) -> str:
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# --- Инициализация RAG ---
@st.cache_resource
def get_rag_chain():
    rag = TrafficSoftRAG()
    rag_chain, retriever = rag.create_rag_chain()
    return rag_chain, retriever

rag_chain, retriever = get_rag_chain()

# --- Настройка страницы ---
st.set_page_config(page_title="Traffic Soft", layout="wide")

# Укажите путь к вашему логотипу (должен быть в той же папке или укажите полный путь)
inject_custom_css_and_logo("logo.png")  # ← замените на свой файл, например: "assets/logo.png"

st.title("HR consultant")

# --- История сообщений ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Задайте вопрос по HR-политике компании: отпуска, бонусы, remote work, адаптация и др."}
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Ввод пользователя ---
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