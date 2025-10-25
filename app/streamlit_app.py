import streamlit as st


st.title("RAG SYSTEM")
message = st.chat_message("assistant")
message.write("Hello!")
dialog = st.chat_input("Задай вопрос")