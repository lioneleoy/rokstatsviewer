import streamlit as st
from utils.translate import translate

st.set_page_config(page_title="Kingdom 1007 Stats Tracker", layout="wide")

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Data Explorer", "Trend Analysis"])
lang = st.sidebar.selectbox("Choose language / Elige idioma:", ["en", "es"])

if page == "Home":
    st.title(translate("title", lang))
    st.write("Welcome to the Kingdom 1007 Stats Tracker. Use the sidebar to navigate.")
elif page == "Data Explorer":
    from pages import data_explorer
    data_explorer.show(lang)
elif page == "Trend Analysis":
    from pages import trend_analysis
    trend_analysis.show(lang)