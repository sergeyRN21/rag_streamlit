import streamlit as st
from rag_core import TrafficSoftRAG

# --- Настройка страницы ---
st.set_page_config(
    page_title="HR Consultant | TrafficSoft",
    page_icon="💼",  # Можно заменить на путь к файлу, если нужно
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- Добавление логотипа в шапку ---
# Используем columns для выравнивания логотипа и заголовка
col1, col2 = st.columns([1, 4])
with col1:
    try:
        st.image("logo.png", width=80)  # Логотип слева
    except Exception:
        st.warning("Логотип не найден. Убедитесь, что logo.png лежит в корне репозитория.")
with col2:
    st.title("HR Consultant")
    st.markdown("💬 Задайте вопрос по HR-политике компании: отпуска, бонусы, remote work, адаптация и др.")

# --- Инициализация RAG ---
@st.cache_resource
def get_rag_chain():
    rag = TrafficSoftRAG()
    rag_chain, retriever = rag.create_rag_chain()
    return rag_chain, retriever

rag_chain, retriever = get_rag_chain()

# --- Инициализация сессии ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Привет! Я ваш HR-консультант. Задавайте вопросы по политикам компании — я помогу найти ответы 😊"
        }
    ]

# --- Отображение истории сообщений ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else "👤"):
        st.markdown(msg["content"])

# --- Поле ввода ---
if prompt_input := st.chat_input("Например: Какие бонусы за годовщину работы?"):
    # Добавляем сообщение пользователя
    st.session_state.messages.append({"role": "user", "content": prompt_input})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt_input)

    # Генерируем ответ
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("🔍 Ищу ответ в HR-политиках..."):
            try:
                response = rag_chain.invoke(prompt_input)
                # Добавляем немного форматирования, если ответ длинный
                if len(response) > 200:
                    st.markdown(f"{response[:200]}...")
                    with st.expander("Показать полностью"):
                        st.markdown(response)
                else:
                    st.markdown(response)
            except Exception as e:
                st.error(f"❌ Произошла ошибка: {str(e)}")
                response = "Извините, не удалось получить ответ. Попробуйте позже."

    # Сохраняем ответ в историю
    st.session_state.messages.append({"role": "assistant", "content": response})

# --- Небольшая подсказка внизу ---
st.markdown("---")
st.caption("💡 Подсказка: Спрашивайте про отпуска, бонусы, удалёнку, адаптацию, гибкий график и другие HR-политики.")