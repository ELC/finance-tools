from pathlib import Path

import streamlit as st

def landing_page(st):
    st.markdown(Path("README.md").read_text())

def entrypoint(st):
    st.set_page_config(layout="wide")
    landing_page(st)

if __name__ == "__main__":
    entrypoint(st)