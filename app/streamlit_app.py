import streamlit as st
from rag_core import TrafficSoftRAG 

@st.cache_resource
def get_rag_chain():
    rag = TrafficSoftRAG()
    rag_chain, retriever = rag.create_rag_chain()
    return rag_chain, retriever

rag_chain, retriever = get_rag_chain()

# Установка конфигурации страницы
st.set_page_config(
    page_title="Traffic Soft HR Consultant",
    page_icon="💼",
    layout="centered"
)

# 🖼️ ЛОГОТИПЫ — используем st.logo() с icon_image
# Предполагаем, что у вас есть два файла:
# - logo_horizontal.png — горизонтальный логотип для шапки
# - logo_icon.png — квадратная иконка для меню/страницы

# Если файлы в папке images/
HORIZONTAL_LOGO = "logo.png"   # или просто "logo.png", если в корне


# Добавляем логотип в шапку и иконку в меню
st.logo(HORIZONTAL_LOGO, size="large")

# Заголовок
st.markdown("# 💼 HR Consultant")
st.markdown("##### *Ваш персональный консультант по HR-политике TrafficSoft*")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": (
            "Привет! Я ваш HR-консультант по политикам TrafficSoft. \n\n"
            "Спрашивайте про: \n"
            "- Отпуска и больничные \n"
            "- Бонусы и компенсации \n"
            "- Remote work и гибрид \n"
            "- Адаптацию и onboarding \n"
            "- Корпоративную культуру \n\n"
            "Я найду ответ в официальных документах компании 😊"
        )}
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

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

# 🧹 Очистить чат (опционально, но полезно для демонстрации)
with st.sidebar:
    if st.button("🗑️ Очистить чат"):
        st.session_state.messages = [
            {"role": "assistant", "content": (
                "Привет! Я ваш HR-консультант по политикам TrafficSoft. \n\n"
                "Спрашивайте про: \n"
                "- Отпуска и больничные \n"
                "- Бонусы и компенсации \n"
                "- Remote work и гибрид \n"
                "- Адаптацию и onboarding \n"
                "- Корпоративную культуру \n\n"
                "Я найду ответ в официальных документах компании 😊"
            )}
        ]
        st.rerun()