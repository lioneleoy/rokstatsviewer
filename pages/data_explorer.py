import streamlit as st
from utils.data_utils import fetch_table_data, get_table_names
from utils.translate import translate

def show(lang):
    st.title(translate("display_data_for_table", lang))
    
    db_path = "ingested_data.db"
    table_names = get_table_names(db_path)

    if table_names:
        selected_table = st.selectbox(translate("select_date", lang), table_names)
        if selected_table:
            data = fetch_table_data(db_path, selected_table)
            st.dataframe(data)
    else:
        st.warning(translate("no_tables_found", lang))