import os

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="SHL Recommender Demo", layout="centered")
st.title("Conversational SHL Assessment Recommender")
st.caption("Beginner-friendly demo UI for the FastAPI backend.")

if "messages" not in st.session_state:
    st.session_state.messages = []

if st.button("Clear chat"):
    st.session_state.messages = []
    st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_text = st.chat_input("Describe the role or paste a short job description...")

if user_text:
    st.session_state.messages.append({"role": "user", "content": user_text})

    with st.chat_message("user"):
        st.markdown(user_text)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = requests.post(
                f"{BACKEND_URL}/chat",
                json={"messages": st.session_state.messages},
                timeout=60,
            )
            response.raise_for_status()
            data = response.json()

        st.markdown(data["reply"])

        recommendations = data.get("recommendations", [])
        if recommendations:
            st.subheader("Recommended assessments")
            for item in recommendations:
                st.markdown(
                    f"- [{item['name']}]({item['url']})  \n"
                    f"  Test type: `{item['test_type']}`"
                )

        history_reply = data["reply"]
        if recommendations:
            names = ", ".join(item["name"] for item in recommendations)
            history_reply += f"\nRecommended assessments: {names}"

        st.session_state.messages.append({"role": "assistant", "content": history_reply})
