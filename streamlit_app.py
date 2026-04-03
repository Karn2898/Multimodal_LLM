"""Streamlit frontend for the Multimodal Gemini FastAPI backend."""

from __future__ import annotations

import requests
import streamlit as st

st.set_page_config(page_title="Multimodal Gemini", page_icon="AI", layout="wide")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=DM+Serif+Display:ital@0;1&display=swap');

    :root {
        --bg-deep: #06131e;
        --bg-mid: #0d2438;
        --bg-soft: #113a57;
        --card-bg: rgba(255, 255, 255, 0.88);
        --card-border: rgba(255, 255, 255, 0.45);
        --ink: #0f1f2c;
        --muted: #42596d;
        --teal: #1ec8a5;
        --coral: #ff6f61;
        --sun: #ffd166;
        --sky: #58c9ff;
    }

    * {
        font-family: 'Space Grotesk', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at 12% 18%, rgba(30, 200, 165, 0.25) 0%, rgba(30, 200, 165, 0) 40%),
            radial-gradient(circle at 86% 12%, rgba(255, 111, 97, 0.3) 0%, rgba(255, 111, 97, 0) 35%),
            radial-gradient(circle at 75% 78%, rgba(255, 209, 102, 0.22) 0%, rgba(255, 209, 102, 0) 42%),
            linear-gradient(135deg, var(--bg-deep) 0%, var(--bg-mid) 50%, var(--bg-soft) 100%);
        color: #f7fbff;
    }

    .stApp::before,
    .stApp::after {
        content: "";
        position: fixed;
        width: 320px;
        height: 320px;
        border-radius: 50%;
        filter: blur(12px);
        z-index: -1;
        opacity: 0.6;
        pointer-events: none;
        animation: drift 10s ease-in-out infinite;
    }

    .stApp::before {
        top: -70px;
        right: -90px;
        background: radial-gradient(circle, rgba(88, 201, 255, 0.75) 0%, rgba(88, 201, 255, 0.08) 70%, transparent 100%);
    }

    .stApp::after {
        bottom: -80px;
        left: -80px;
        background: radial-gradient(circle, rgba(255, 111, 97, 0.72) 0%, rgba(255, 111, 97, 0.1) 65%, transparent 100%);
        animation-delay: 2s;
    }

    @keyframes drift {
        0%, 100% { transform: translateY(0px) scale(1); }
        50% { transform: translateY(-12px) scale(1.05); }
    }

    .block-container {
        padding-top: 1.6rem;
        max-width: 980px;
    }

    .app-shell {
        background: linear-gradient(125deg, rgba(255,255,255,0.93) 0%, rgba(247, 254, 255, 0.88) 45%, rgba(245, 255, 251, 0.86) 100%);
        border: 1px solid var(--card-border);
        border-radius: 24px;
        padding: 1.15rem 1.3rem 0.75rem 1.3rem;
        margin-bottom: 1rem;
        box-shadow: 0 18px 40px rgba(0, 12, 28, 0.22);
    }

    .app-title {
        font-family: 'DM Serif Display', serif;
        font-size: 2rem;
        font-weight: 400;
        color: var(--ink);
        margin: 0;
        letter-spacing: 0.01em;
        line-height: 1.05;
    }

    .app-subtitle {
        color: var(--muted);
        margin-top: 0.2rem;
        margin-bottom: 0.1rem;
        font-weight: 500;
    }

    .color-row {
        display: flex;
        gap: 0.45rem;
        margin: 0.7rem 0 0.25rem;
    }

    .pill {
        width: 36px;
        height: 10px;
        border-radius: 999px;
    }

    .p1 { background: var(--teal); }
    .p2 { background: var(--sky); }
    .p3 { background: var(--sun); }
    .p4 { background: var(--coral); }

    [data-testid="stSidebar"] {
        border-right: 1px solid rgba(235, 248, 255, 0.2);
        background: linear-gradient(180deg, rgba(4, 20, 33, 0.9) 0%, rgba(8, 36, 57, 0.88) 100%);
    }

    [data-testid="stSidebar"] * {
        color: #e8f6ff;
    }

    [data-testid="stSidebar"] [data-testid="stTextInput"] input,
    [data-testid="stSidebar"] [data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.24);
        color: #ffffff;
    }

    [data-testid="stChatMessage"] {
        border: 1px solid rgba(255, 255, 255, 0.34);
        border-radius: 18px;
        background: rgba(255, 255, 255, 0.9);
        box-shadow: 0 10px 22px rgba(8, 31, 48, 0.12);
        padding: 0.3rem 0.6rem;
    }

    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        background: linear-gradient(125deg, rgba(88, 201, 255, 0.2) 0%, rgba(30, 200, 165, 0.18) 100%);
        border-color: rgba(88, 201, 255, 0.35);
    }

    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
        background: linear-gradient(125deg, rgba(255, 209, 102, 0.24) 0%, rgba(255, 111, 97, 0.14) 100%);
        border-color: rgba(255, 111, 97, 0.28);
    }

    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"],
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] * {
        color: #102a3d !important;
    }

    [data-testid="stChatMessage"] code {
        background: rgba(16, 42, 61, 0.08);
        color: #0d3550 !important;
        border-radius: 6px;
        padding: 0.08rem 0.3rem;
    }

    [data-testid="stChatMessage"] pre {
        background: rgba(10, 37, 54, 0.9);
        color: #eef8ff !important;
        border-radius: 10px;
    }

    [data-testid="stChatMessage"] pre code {
        background: transparent;
        color: #eef8ff !important;
        padding: 0;
    }

    .stChatInputContainer {
        background: rgba(5, 24, 40, 0.55);
        border: 1px solid rgba(233, 249, 255, 0.18);
        backdrop-filter: blur(8px);
        border-radius: 16px;
        padding: 0.25rem;
    }

    .stButton button {
        border-radius: 999px;
        border: none;
        padding: 0.5rem 1rem;
        background: linear-gradient(90deg, var(--teal) 0%, var(--sky) 55%, var(--sun) 100%);
        color: #05283e;
        font-weight: 700;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .stButton button:hover {
        transform: translateY(-1px);
        box-shadow: 0 8px 20px rgba(88, 201, 255, 0.35);
    }

    [data-testid="stMarkdownContainer"] p {
        color: #11324a;
    }

    @media (max-width: 900px) {
        .app-title {
            font-size: 1.6rem;
        }
        .block-container {
            padding-top: 1.1rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="app-shell">
        <p class="app-title">Aurora Multimodal Studio</p>
        <p class="app-subtitle">Color-forward interface for text, image, and audio Gemini workflows.</p>
        <div class="color-row">
            <span class="pill p1"></span>
            <span class="pill p2"></span>
            <span class="pill p3"></span>
            <span class="pill p4"></span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.subheader("Connection")
    base_url = st.text_input("FastAPI URL", value="http://127.0.0.1:8000")
    api_secret_key = st.text_input("API Secret Key (optional)", type="password")

    st.subheader("Mode")
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
