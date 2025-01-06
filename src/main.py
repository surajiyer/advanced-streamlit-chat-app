import streamlit as st


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

page1 = st.Page("pages/login.py")
page2 = st.Page("pages/characters.py", title="Characters", icon="👥")
page3 = st.Page("pages/chat.py", title="Chat", icon="💬")

if st.session_state.logged_in:
    pg = st.navigation([page2, page3])
else:
    pg = st.navigation([page1])
pg.run()
