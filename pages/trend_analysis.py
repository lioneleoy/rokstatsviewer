import streamlit as st
import altair as alt
from utils.data_utils import fetch_table_data, aggregate_data, get_table_names
from utils.translate import translate

def show(lang):
    st.title(translate("trend_analysis", lang))
    
    db_path = "ingested_data.db"
    table_names = get_table_names(db_path)

    if table_names:
        selected_table = st.selectbox(translate("select_date", lang), table_names)
        if selected_table:
            data = fetch_table_data(db_path, selected_table)
            if 'governorID' in data.columns and 'name' in data.columns:
                g_id_with_name = data[['governorID', 'name']].drop_duplicates()
                g_id_with_name['display'] = g_id_with_name.apply(lambda row: f"{row['governorID']} ({row['name']})", axis=1)
                display_to_g_id = dict(zip(g_id_with_name['display'], g_id_with_name['governorID']))
                selected_display = st.selectbox(translate("select_governor", lang), g_id_with_name['display'])
                selected_g_id = display_to_g_id[selected_display]
                
                if selected_g_id:
                    st.header(f"{translate('trend_analysis', lang)} {selected_display}")
                    aggregated_data = aggregate_data(db_path, table_names)
                    aggregated_data = aggregated_data[aggregated_data['governorID'] == int(selected_g_id)]
                    
                    if not aggregated_data.empty:
                        trend_columns = ['power', 'killpoints', 'deads']
                        for column in trend_columns:
                            if column in aggregated_data.columns:
                                aggregated_data[column] = aggregated_data[column].astype(float)
                                chart = (
                                    alt.Chart(aggregated_data)
                                    .mark_line(strokeWidth=3)
                                    .encode(
                                        x=alt.X('Date:T', title='Date'),
                                        y=alt.Y(column, title=column, scale=alt.Scale(zero=False)),
                                        color=alt.value("#1f77b4"),
                                        tooltip=['Date:T', column]
                                    )
                                    .properties(
                                        title=translate("trend_of", lang).format(column=column, selected_display=selected_display),
                                        width=800,
                                        height=500
                                    )
                                )
                                st.altair_chart(chart)
                            else:
                                st.warning(translate("warning_missing_column", lang).format(column=column))
                    else:
                        st.warning(translate("no_data_for_g_id", lang))
    else:
        st.warning(translate("no_tables_found", lang))