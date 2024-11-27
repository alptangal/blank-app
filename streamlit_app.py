import streamlit as st
import subprocess

subprocess.run(['uvicorn','app:app', '--reload'])

st.title("🎈 My new app")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)
