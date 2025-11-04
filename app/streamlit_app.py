import streamlit as st
from rag_core import TrafficSoftRAG

@st.cache_resource
def get_rag_chain():
    rag = TrafficSoftRAG()
    rag_chain, retriever = rag.create_rag_chain()
    return rag_chain, retriever

rag_chain, retriever = get_rag_chain()

# Настройка страницы
st.set_page_config(
    page_title="TrafficSoft — HR-ассистент на базе ИИ",
    page_icon="💼",
    layout="centered"
)

# Заголовок и описание
st.title("💼 HR-ассистент TrafficSoft")
st.markdown(
    """
    Добро пожаловать в умного HR-ассистента на базе искусственного интеллекта!  
    Задавайте вопросы по внутренней политике компании — и получайте точные, подтверждённые источниками ответы:
    - Оформление отпусков и больничных  
    - Бонусы, премии и KPI  
    - Удалённая работа и гибкий график  
    - Адаптация новых сотрудников  
    - Корпоративные ценности и внутренние правила  
    """
)

# Инициализация истории сообщений
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Привет! Я — ваш AI-ассистент по HR-политике TrafficSoft. Задайте любой вопрос, и я помогу найти официальный ответ из внутренних документов."
        }
    ]

# Отображение истории чата
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Обработка нового ввода
if prompt_input := st.chat_input("Например: «Как оформить отпуск без сохранения зарплаты?»"):
    # Добавление сообщения пользователя
    st.session_state.messages.append({"role": "user", "content": prompt_input})
    with st.chat_message("user"):
        st.markdown(prompt_input)

    # Генерация ответа
    with st.chat_message("assistant"):
        with st.spinner("Ищу актуальную информацию в HR-документах…"):
            try:
                response = rag_chain.invoke(prompt_input)
            except Exception as e:
                response = f"⚠️ Произошла ошибка при обработке запроса: {str(e)}"
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})