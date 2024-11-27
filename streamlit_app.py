import streamlit as st
import subprocess,sys
import requests
import datetime
import traceback

try:
    req=requests.get('http://localhost:8000')
    if int(str(datetime.datetime.now().timestamp()).split('.')[0])-int(req.text.split('.')[0])>=10:
        raise Exception("Server not response")
    sys.exit("Exited")
except Exception as error:
    traceback.print_exc()
    subprocess.run(['uvicorn','app:app', '--reload'])

if not hasattr(st, 'already_started_server'):
    # Hack the fact that Python modules (like st) only load once to
    # keep track of whether this file already ran.
    st.already_started_server = True

    st.write('''
        The first time this script executes it will run forever because it's
        running a Flask server.

        Just close this browser tab and open a new one to see your Streamlit
        app.
    ''')

    from flask import Flask

    app = Flask(__name__)

    @app.route('/foo')
    def serve_foo():
        return 'This page is served via Flask!'

    app.run(port=8888)
