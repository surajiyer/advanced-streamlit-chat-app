import streamlit as st

from utils import complete_chat


with st.sidebar:
    st.header("Sidebar")
    st.write("This is a sidebar panel.")

st.title("💬 Chatbot")
st.caption("🚀 A Streamlit chatbot powered by WärtsiläGPT")

if 'messages' not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    try:
        response = complete_chat(model="gpt-35-turbo-16k", messages=st.session_state.messages)
    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.stop()
    if not response:
        st.stop()
    msg = response["choices"][0]["message"]
    st.session_state.messages.append(msg)
    st.chat_message(msg["role"]).write(msg["content"])
