from pathlib import Path

import streamlit as st
from streamlit_multipage import MultiPage

from pages import pages


def landing_page(st):
    st.markdown(Path("README.md").read_text())


def header(st):
    snippet = """
    <div style="text-align: right">
        <a href="https://github.com/ELC/python-compound-interest" target="_blank" style="text-decoration: none; color: goldenrod">Give it a ★ on Github</a>
    </div>
    """
    st.markdown(snippet, unsafe_allow_html=True)


def footer(st):
    snippet = """
    <div style="text-align: center; line-height: 2.5em;">
        Developed using 
        <a href="https://streamlit.io/" target="_blank" style="text-decoration: none">streamlit</a>
        by <a href="https://elc.github.io" target="_blank" style="text-decoration: none">Ezequiel Leonardo Castaño</a>
        - Python Code available at <a href="https://github.com/ELC/python-compound-interest" target="_blank" style="text-decoration: none">Github</a>.
        <br>
        If you like the app, consider <a href="https://elc.github.io/donate" target="_blank" style="text-decoration: none">donating</a>.
        <br>
        For contact information, reach out by <a href="https://www.linkedin.com/in/ezequielcastano/" target="_blank" style="text-decoration: none">LinkedIn</a>
    </div>
    """
    st.markdown(snippet, unsafe_allow_html=True)


st.set_page_config(layout="wide")

app = MultiPage()
app.st = st
app.navbar_name = "Other Apps"
app.start_button = "Start App"
app.navbar_style = "VerticalButton"

app.header = header
app.footer = footer
app.hide_navigation = True
app.hide_menu = True

app.add_app("Landing", landing_page, initial_page=True)

for name, function in pages.items():
    app.add_app(name, function)

app.run()
