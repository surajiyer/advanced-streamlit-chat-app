import json
from typing import Optional
import requests

import streamlit as st


def get_api_key():
    return st.secrets["wartsila_gpt_api_key"]


def complete_chat(model="gpt-3.5-turbo", messages=None) -> Optional[dict]:
    valid_models = ["gpt-35-turbo-16k", "gpt-4", "gpt-4o"]
    if model not in valid_models:
        raise ValueError(f"Invalid model: {model}. Choose from {valid_models}")

    if messages is None:
        return

    url = "https://api.wartsila.com/int/wartsila-gpt/chat/completions"

    headers = {
        'Content-Type': 'application/json',
        'Cache-Control': 'no-cache',
        'Ocp-Apim-Subscription-Key': get_api_key(),
        'model': model
    }
    data = json.dumps({"messages": messages})
    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Request failed with status code {response.status_code}")
