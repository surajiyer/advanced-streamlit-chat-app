import streamlit as st
from utils import (
    complete_chat,
    init_db,
    save_chat_log,
    save_message,
    get_chat_logs,
    get_messages,
    save_character,
    get_all_characters,
)
import globals as g


def set_page_configurations():
    st.set_page_config(page_title=g.PAGE_TITLE, page_icon=g.PAGE_ICON)
    st.title(g.CHATBOT_TITLE)
    st.caption(g.CHATBOT_CAPTION)


def init_session_state():
    """Initialize session state for messages and log_id"""
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": g.DEFAULT_ASSISTANT_MESSAGE}]
        st.session_state.log_id = None


@st.dialog("Create a new character")
def create_character_form():
    """Popup form for adding a new character."""
    new_character_name = st.text_input("Character Name")
    new_character_description = st.text_area("Character Description")
    new_image_file = st.file_uploader(g.IMAGE_UPLOAD_LABEL, type=["png", "jpg", "jpeg", "webp"])
    save_button = st.button("Save")

    if save_button:
        if not new_character_name:
            st.error("Character name is required.")
            st.stop()
        if not new_character_description:
            st.error("Character description is required.")
            st.stop()

        # Save character details and image
        if new_image_file:
            st.success(g.IMAGE_UPLOAD_SUCCESS)
            save_character(new_character_name, new_character_description, new_image_file.getvalue())
        else:
            save_character(new_character_name, new_character_description)

        st.success(f"Character '{new_character_name}' added successfully!")
        st.rerun()


def display_sidebar():
    """Configure and display the sidebar"""
    with st.sidebar:
        st.header(g.SIDEBAR_HEADER)
        st.write(g.SIDEBAR_PANEL_TEXT)

        # User and character selection
        user = st.selectbox(g.USER_SELECTBOX_LABEL, options=[g.DEFAULT_USER], index=0)
        characters = get_all_characters()
        character = st.selectbox(
            g.CHARACTER_SELECTBOX_LABEL, options=characters, index=0, format_func=lambda x: x["name"]
        )
        avatar = character.get("image")
        if avatar:
            st.image(avatar)

        # Plus icon button to add a new character
        if st.button("➕"):
            create_character_form()

        # Display previous conversations
        if user:
            chat_logs = get_chat_logs(user)
            if chat_logs:
                selected_chat = st.radio(
                    g.PREVIOUS_CONVERSATIONS_LABEL,
                    chat_logs,
                    format_func=lambda x: f"Character: {x['character']}",
                )
                if selected_chat:
                    st.session_state.messages = get_messages(selected_chat["id"])
            else:
                st.write(g.NO_PREVIOUS_CONVERSATIONS_TEXT)

    return user, character, avatar


def display_chat_messages():
    """Display chat messages."""
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])


def handle_user_input(user, character, avatar):
    """Handle user input and chatbot response."""
    if prompt := st.chat_input():
        # Save chat log if it's the first message
        if st.session_state.log_id is None:
            st.session_state.log_id = save_chat_log(user, character["name"])

        # Append user message to session state and save to database
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        save_message(st.session_state.log_id, "user", prompt)

        # Get response from the chatbot API
        try:
            # response = complete_chat(model="gpt-35-turbo-16k", messages=st.session_state.messages)
            last_user_message = st.session_state.messages[-1]["content"]
            response = {"choices": [{"message": {"role": "assistant", "content": f"Echo: {last_user_message}"}}]}
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.stop()
        if not response:
            st.stop()

        # Append chatbot response to session state and save to database
        msg = response["choices"][0]["message"]
        st.session_state.messages.append(msg)
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])
        save_message(st.session_state.log_id, msg["role"], msg["content"])


if __name__ == "__main__":
    init_db()
    set_page_configurations()
    init_session_state()
    user, character, avatar = display_sidebar()
    display_chat_messages()
    handle_user_input(user, character, avatar)
