# streamlit_app.py — стиль как на вашем скриншоте
import streamlit as st
from rag_core import TrafficSoftRAG

# Настройка страницы
st.set_page_config(
    page_title="Внутренний ассистент TrafficSoft",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS для тёмного стиля TrafficSoft
st.markdown("""
<style>
/* Тёмный фон */
body {
    background-color: #0E0E10;
    color: white;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Заголовки */
h1, h2, h3 {
    color: white;
    font-weight: 600;
}

/* Кнопка отправки */
.stButton>button {
    background-color: #FF7A00; /* Оранжевый цвет из вашего скриншота */
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 10px;
    font-weight: bold;
    transition: background-color 0.3s;
}

.stButton>button:hover {
    background-color: #E56D00;
}

/* Поле ввода */
input[type="text"] {
    background-color: #2A2A2C;
    color: white;
    border: 1px solid #444;
    border-radius: 20px;
    padding: 10px;
    font-size: 16px;
}

/* Сообщения чата */
.chat-message {
    padding: 10px 15px;
    margin: 8px 0;
    border-radius: 12px;
    max-width: 80%;
    display: flex;
    align-items: center;
    gap: 10px;
}

.chat-message.user {
    background-color: #2A2A2C;
    align-self: flex-end;
    margin-left: auto;
    justify-content: flex-end;
}

.chat-message.assistant {
    background-color: #1E1E20;
    align-self: flex-start;
    justify-content: flex-start;
}

.chat-message .avatar {
    width: 30px;
    height: 30px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    font-weight: bold;
}

.chat-message.user .avatar {
    background-color: #FF7A00;
    color: white;
}

.chat-message.assistant .avatar {
    background-color: #00D1D1;
    color: white;
}

/* Подсказка внизу */
.footer {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background-color: #0E0E10;
    padding: 10px;
    text-align: center;
    border-top: 1px solid #2A2A2C;
}
</style>
""", unsafe_allow_html=True)

# Логотип и заголовок
col1, col2 = st.columns([1, 4])
with col1:
    # Если есть файл logo.png — разместите его в папке app/
    try:
        st.image("app/logo.png", width=80)
    except:
        # Заглушка — если логотипа нет
        st.markdown('<div style="background:#2A2A2C; padding:5px; border-radius:10px; text-align:center">TrafficSoft</div>', unsafe_allow_html=True)

with col2:
    st.markdown("<h1 style='font-size: 2.5em;'>🤖 Внутренний ассистент TrafficSoft</h1>", unsafe_allow_html=True)
    st.markdown("Задайте вопрос по внутренним регламентам — получите точный ответ с цитированием.")

# Приветствие
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Здравствуйте! Я помогу найти информацию в ваших внутренних документах."}
    ]

# Отображение истории
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        avatar = "🤖" if msg["role"] == "assistant" else "👤"
        st.markdown(f'<div class="chat-message {msg["role"]}"><div class="avatar">{avatar}</div>{msg["content"]}</div>', unsafe_allow_html=True)

# Поле ввода внизу
st.markdown('<div class="footer">', unsafe_allow_html=True)
if prompt_input := st.chat_input("Ваш вопрос"):
    st.session_state.messages.append({"role": "user", "content": prompt_input})
    with st.chat_message("user"):
        st.markdown(f'<div class="chat-message user"><div class="avatar">👤</div>{prompt_input}</div>', unsafe_allow_html=True)

    with st.chat_message("assistant"):
        with st.spinner("Ищу в регламентах..."):
            try:
                @st.cache_resource
                def get_rag_chain():
                    rag = TrafficSoftRAG()
                    return rag.create_rag_chain()

                rag_chain, _ = get_rag_chain()
                response = rag_chain.invoke(prompt_input)
            except Exception as e:
                response = f"Ошибка: {str(e)}"
        st.markdown(f'<div class="chat-message assistant"><div class="avatar">🤖</div>{response}</div>', unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": response})
st.markdown('</div>', unsafe_allow_html=True)