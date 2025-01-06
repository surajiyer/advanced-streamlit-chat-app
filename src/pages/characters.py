import streamlit as st

import globals as g
from data.utils import db_connection
from data.character import Character


@db_connection
def init_db(conn=None):
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS characters
        (id TEXT PRIMARY KEY, name TEXT, description TEXT, image TEXT, created_at TIMESTAMP,
        updated_at TIMESTAMP)"""
    )
    c.execute("SELECT COUNT(*) FROM characters WHERE name = ?", (g.DEFAULT_CHARACTER,))
    if c.fetchone()[0] == 0:
        Character.new(g.DEFAULT_CHARACTER, "Default character for the chatbot", conn=conn)


def set_page_configurations():
    st.set_page_config(page_title="Characters", page_icon="👥")
    st.title("Characters")


@st.dialog(g.CREATE_NEW_CHARACTER_LABEL)
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
        Character.new(
            new_character_name, new_character_description, new_image_file.getvalue() if new_image_file else None
        )

        st.success(f"Character '{new_character_name}' added successfully!")
        st.rerun()


def display_character_selection():
    """Display character selection."""
    if st.button(g.CREATE_NEW_CHARACTER_LABEL, key="new_character_btn", use_container_width=True):
        create_character_form()
    characters = Character.get_all()
    character: Character = st.selectbox(
        g.CHARACTER_SELECTBOX_LABEL,
        options=characters,
        index=0,
        format_func=lambda x: x.name,
        label_visibility="collapsed",
    )
    st.session_state.character = character
    if character.image:
        st.image(character.image)


def page():
    if not ("logged_in" in st.session_state and st.session_state.logged_in):
        return
    init_db()
    set_page_configurations()
    display_character_selection()


page()
