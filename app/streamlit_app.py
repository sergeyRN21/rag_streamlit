import streamlit as st

message = st.chat_message("assistant")
message.write("Hello!")
dialog = st.chat_input("Задай вопрос")
