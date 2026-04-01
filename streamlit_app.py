"""Streamlit frontend for the Multimodal Gemini FastAPI backend."""

from __future__ import annotations

import requests
import streamlit as st

st.set_page_config(page_title="Multimodal Gemini", page_icon="AI", layout="wide")

st.title("Multimodal Gemini Interface")
st.caption("No HTML needed. This UI calls your FastAPI endpoints directly.")

with st.sidebar:
    st.header("Connection")
    base_url = st.text_input("FastAPI URL", value="http://127.0.0.1:8000")
    api_secret_key = st.text_input("API Secret Key (optional)", type="password")

    st.header("Mode")
    mode = st.selectbox(
        "Choose mode",
        ["Text Chat", "Image URL + Text", "Image Upload + Text", "Audio Upload + Text"],
    )

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


def auth_headers() -> dict[str, str]:
    if not api_secret_key.strip():
        return {}
    return {"Authorization": f"Bearer {api_secret_key.strip()}"}


def post_text(message: str) -> requests.Response:
    history = []
    for msg in st.session_state.messages:
        role = "user" if msg["role"] == "user" else "model"
        history.append({"role": role, "parts": [{"text": msg["content"]}]})

    return requests.post(
        f"{base_url}/api/v1/chat",
        json={"message": message, "history": history},
        headers={"Content-Type": "application/json", **auth_headers()},
        timeout=120,
    )


def post_image_url(message: str, image_url: str) -> requests.Response:
    history = []
    for msg in st.session_state.messages:
        role = "user" if msg["role"] == "user" else "model"
        history.append({"role": role, "parts": [{"text": msg["content"]}]})

    return requests.post(
        f"{base_url}/api/v1/chat/image",
        json={"message": message, "image_url": image_url, "history": history},
        headers={"Content-Type": "application/json", **auth_headers()},
        timeout=120,
    )


def post_file(endpoint: str, message: str, uploaded_file) -> requests.Response:
    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
    data = {"message": message}
    return requests.post(
        f"{base_url}{endpoint}",
        data=data,
        files=files,
        headers=auth_headers(),
        timeout=180,
    )


user_prompt = st.chat_input("Type your prompt and press Enter")

if mode == "Image URL + Text":
    image_url_value = st.text_input("Image URL", placeholder="https://example.com/image.jpg")
else:
    image_url_value = ""

if mode == "Image Upload + Text":
    uploaded_image = st.file_uploader("Upload image", type=["jpg", "jpeg", "png", "gif", "webp"])
else:
    uploaded_image = None

if mode == "Audio Upload + Text":
    uploaded_audio = st.file_uploader("Upload audio", type=["mp3", "wav", "ogg", "flac", "aac", "webm", "mpeg"])
else:
    uploaded_audio = None

if user_prompt:
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                if mode == "Text Chat":
                    response = post_text(user_prompt)
                elif mode == "Image URL + Text":
                    if not image_url_value.strip():
                        st.error("Please provide an image URL.")
                        st.stop()
                    response = post_image_url(user_prompt, image_url_value.strip())
                elif mode == "Image Upload + Text":
                    if uploaded_image is None:
                        st.error("Please upload an image file.")
                        st.stop()
                    response = post_file("/api/v1/chat/image/upload", user_prompt, uploaded_image)
                else:
                    if uploaded_audio is None:
                        st.error("Please upload an audio file.")
                        st.stop()
                    response = post_file("/api/v1/chat/audio", user_prompt, uploaded_audio)

                if response.status_code >= 400:
                    try:
                        detail = response.json().get("detail", response.text)
                    except Exception:
                        detail = response.text
                    answer = f"Request failed ({response.status_code}): {detail}"
                else:
                    payload = response.json()
                    answer = payload.get("content", "(empty response)")
            except requests.RequestException as exc:
                answer = f"Connection error: {exc}"

        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})

if st.button("Clear Conversation"):
    st.session_state.messages = []
    st.rerun()
