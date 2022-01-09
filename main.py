from pathlib import Path

import streamlit as st
from streamlit_multipage import MultiPage

from pages import pages


def landing_page(st):
    st.markdown(Path("README.md").read_text())


st.set_page_config(layout="wide")

app = MultiPage()
app.st = st
app.navbar_name = "Other Apps"
app.start_button = "Start App"

app.add_app("Landing", landing_page, initial_page=True)

for name, function in pages.items():
    app.add_app(name, function)

app.run()
