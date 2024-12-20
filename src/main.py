import streamlit as st

from ai import complete_chat
from database import Database
import globals as g


db = Database()


def set_page_configurations():
    st.set_page_config(page_title=g.PAGE_TITLE, page_icon=g.PAGE_ICON)
    st.title(g.CHATBOT_TITLE)
    st.caption(g.CHATBOT_CAPTION)


def init_session_state():
    """Initialize session state for messages and conversation_id"""
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": g.DEFAULT_ASSISTANT_MESSAGE}]
        st.session_state.conversation_id = None


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
            db.save_character(new_character_name, new_character_description, new_image_file.getvalue())
        else:
            db.save_character(new_character_name, new_character_description)

        st.success(f"Character '{new_character_name}' added successfully!")
        st.experimental_rerun()


def display_sidebar():
    """Configure and display the sidebar"""
    with st.sidebar:
        st.header(g.SIDEBAR_HEADER)
        st.write(g.SIDEBAR_PANEL_TEXT)

        # User and character selection
        user = st.selectbox(g.USER_SELECTBOX_LABEL, options=[g.DEFAULT_USER], index=0)
        characters = db.get_all_characters()
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
            conversations = db.get_conversations(user)
            if conversations:
                selected_conversation = st.radio(
                    g.PREVIOUS_CONVERSATIONS_LABEL,
                    conversations,
                    format_func=lambda x: f"Character: {x['character']}",
                )
                if selected_conversation:
                    st.session_state.messages = db.get_messages(selected_conversation["id"])
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
        # Save conversation if it's the first message
        if st.session_state.conversation_id is None:
            st.session_state.conversation_id = db.save_conversation(user, character["name"])

        # Append user message to session state and save to database
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        db.save_message(st.session_state.conversation_id, "user", prompt)

        # Get response from the chatbot API
        try:
            response = complete_chat(model="gpt-35-turbo-16k", messages=st.session_state.messages)
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
        db.save_message(st.session_state.conversation_id, msg["role"], msg["content"])


if __name__ == "__main__":
    set_page_configurations()
    init_session_state()
    user, character, avatar = display_sidebar()
    display_chat_messages()
    handle_user_input(user, character, avatar)

# Logical issues or bugs in the app:
# 1. The `avatar` variable is set to `None` in `display_sidebar` and is not updated with the actual image URL.
# 2. The `avatar` is not being displayed correctly in the chat messages.
# 3. The `create_character_form` function does not handle the case where the image file is not provided.
# 4. The `save_character` function in `utils.py` saves the image as bytes, but the `get_all_characters` function retrieves it as a string.
# 5. The `complete_chat` function is commented out and replaced with a mock response.
# 6. The `st.dialog` decorator is not a valid Streamlit function and should be replaced with a proper modal implementation.
# 7. The `st.rerun()` function is not a valid Streamlit function and should be replaced with `st.experimental_rerun()`.
# 8. The `character` selectbox in the sidebar does not update when a new character is added.
# 9. The `user` selectbox in the sidebar is hardcoded to "default_user" and does not allow for multiple users.
# 10. The `get_image_url_from_s3` function is not used anywhere in the code.
