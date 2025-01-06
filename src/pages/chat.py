import streamlit as st

from ai import complete_chat
from data.character import Character
from data.conversation import Conversation
from data.user import User
from data.utils import db_connection
import globals as g


@db_connection
def init_db(conn=None):
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS conversations
        (id TEXT PRIMARY KEY, user TEXT, character TEXT, title TEXT NOT NULL, created_at TIMESTAMP,
        updated_at TIMESTAMP)"""
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS messages
        (id INTEGER PRIMARY KEY AUTOINCREMENT, conversation_id TEXT, role TEXT, content TEXT, created_at TIMESTAMP,
        updated_at TIMESTAMP, FOREIGN KEY(conversation_id) REFERENCES conversations(id))"""
    )


def set_page_configurations():
    st.set_page_config(page_title=g.PAGE_TITLE, page_icon=g.PAGE_ICON)
    st.title(g.CHATBOT_TITLE)
    st.caption(g.CHATBOT_CAPTION)


def init_session_state():
    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "user" not in st.session_state:
        # TODO: get logged in user
        st.session_state.user = User(id=g.DEFAULT_USER, name=g.DEFAULT_USER)
    if "character" not in st.session_state:
        st.session_state.character = None


def load_existing_conversation(conversation: Conversation):
    """Load conversation messages from the database."""
    if not conversation:
        return
    if not conversation.messages:
        conversation.get_messages()
    st.session_state.conversation = conversation
    st.query_params[g.CONVERSATION_ID_QUERY_PARAM_KEY] = conversation.id


def display_conversations_sidebar():
    """Display previous conversations."""
    with st.sidebar:
        st.header(g.CONVERSATIONS_HEADER)
        if st.button(g.CREATE_NEW_CONVERSATION_LABEL, key="new_conversation_btn", use_container_width=True):
            st.session_state.conversation = None
            st.query_params.clear()
            st.rerun()

        conversations = Conversation.get_all(st.session_state.user)
        st.write(len(conversations), "conversations found.")
        if not conversations:
            return
        for conversation in conversations:
            st.button(
                conversation.title,
                key=conversation.id,
                on_click=load_existing_conversation,
                args=(conversation,),
                use_container_width=True,
            )


def display_chat_messages():
    """Display chat messages."""
    if not st.session_state.conversation:
        return
    for msg in st.session_state.conversation.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])


def handle_user_input():
    """Handle user input and chatbot response."""
    user: User = st.session_state.user
    character: Character = st.session_state.character
    conversation: Conversation = st.session_state.conversation

    if prompt := st.chat_input():
        # Save conversation if it's the first message
        if new_conversation := conversation is None:
            conversation = Conversation.new(user, character)

        # Append user message to session state and save to database
        conversation.save_message("user", prompt)
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get response from the chatbot API
        try:
            response = complete_chat(model="gpt-35-turbo-16k", messages=conversation.messages)
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.stop()
        if not response:
            st.stop()

        # Append chatbot response to session state and save to database
        msg = response["choices"][0]["message"]
        conversation.save_message(msg["role"], msg["content"])
        with st.chat_message(msg["role"], avatar=character.image):
            st.markdown(msg["content"])

        # Update conversation ID in URL if it's a new conversation and rerun
        if new_conversation:
            st.session_state.conversation = conversation
            st.query_params[g.CONVERSATION_ID_QUERY_PARAM_KEY] = conversation.id
            st.rerun()


def update_conversation_title(conversation: Conversation):
    """Update the title of an existing conversation."""
    new_title = st.text_input("New Conversation Title")
    if st.button("Update Title"):
        conversation.save(title=new_title)
        st.success("Conversation title updated successfully!")
        st.rerun()


def page():
    if not ("logged_in" in st.session_state and st.session_state.logged_in):
        return
    init_db()
    set_page_configurations()
    init_session_state()
    display_conversations_sidebar()
    display_chat_messages()
    handle_user_input()


# Notes for writing code (DO NOT REMOVE THE FOLLOWING LINES):
# * st.experimental_rerun() has been deprecated. Use st.rerun() instead.
# * datetime.utcnow() has been deprecaated. Use datetime.now(datetime.timezone.utc) instead.
# hidden characters that are not visible in chats
page()
