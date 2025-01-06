import streamlit as st


def set_page_configurations():
    st.set_page_config(page_title="Login", page_icon="🔒")
    st.title("Login")


def init_session_state():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False


def logout():
    st.session_state.logged_in = False
    st.success("You have been logged out.")
    st.rerun()


def login(username: str, password: str):
    if username == "admin" and password == "password":
        st.session_state.logged_in = True
        st.success("Login successful!")
        st.rerun()
    else:
        st.session_state.logged_in = False
        st.error("Invalid username or password")


def page():
    set_page_configurations()
    init_session_state()

    if st.session_state.logged_in:
        return
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        login(username, password)


page()
