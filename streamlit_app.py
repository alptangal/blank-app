import streamlit as st
import subprocess,sys
import requests
import datetime

try:
    req=requests.get('http://localhost:8000')
    if int(str(datetime.datetime.now().timestamp()).split('.')[0])-int(req.text.split('.')[0])>=10:
        raise Exception("Server not response")
    sys.exit("Exited")
except Exception as error:
    print(error)
    subprocess.run(['uvicorn','app:app', '--reload'])

st.title("🎈 My new app")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)
