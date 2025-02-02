import os
import sqlite3
import pandas as pd
import streamlit as st
import altair as alt

# Translation dictionary
translations = {
    "en": {
        "title": "Kingdom 1007 Stats tracker",
        "select_date": "Select a date to display:",
        "display_data_for_table": "Displaying data for table: ",
        "filter_options": "Filter Options",
        "select_columns_to_filter": "Select columns to filter:",
        "select_governor": "Select governorID for trend visualization:",
        "trend_analysis": "Trend Analysis for governorID:",
        "trend_of": "Trend of {column} over Time for governorID {selected_display}",
        "no_data_found": "No data found for table: ",
        "no_data_for_g_id": "No data available for the selected g_id.",
        "no_tables_found": "No tables found in the database.",
        "error_occurred": "An error occurred: {error}",
        "warning_missing_column": "Column {column} is missing or non-numeric."
    },
    "es": {
        "title": "Rastreador de estadísticas Kingdom 1007",
        "select_date": "Seleccionar una fecha para mostrar:",
        "display_data_for_table": "Mostrando datos para la tabla: ",
        "filter_options": "Opciones de filtro",
        "select_columns_to_filter": "Seleccionar columnas para filtrar:",
        "select_governor": "Seleccionar governorID para visualización de tendencias:",
        "trend_analysis": "Análisis de tendencias para governorID:",
        "trend_of": "Tendencia de {column} a lo largo del tiempo para governorID {selected_display}",
        "no_data_found": "No se encontraron datos para la tabla: ",
        "no_data_for_g_id": "No hay datos disponibles para el governorID seleccionado.",
        "no_tables_found": "No se encontraron tablas en la base de datos.",
        "error_occurred": "Ocurrió un error: {error}",
        "warning_missing_column": "La columna {column} falta o no es numérica."
    }
}

# Function to translate text
def translate(text, lang="en"):
    return translations[lang].get(text, text)

# Function to fetch table data
def fetch_table_data(db_path, table_name):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(f'SELECT * FROM "{table_name}"', conn)
    conn.close()
    return df

# Function to aggregate data
def aggregate_data(db_path, table_names):
    aggregated_data = []
    for table_name in table_names:
        df = fetch_table_data(db_path, table_name)
        df['Date'] = pd.to_datetime(table_name, format="%m%d%Y", errors='coerce')
        aggregated_data.append(df)
    return pd.concat(aggregated_data, ignore_index=True)

# Streamlit app
lang = st.selectbox("Choose language / Elige idioma:", ["en", "es"])
st.title(translate("title", lang))

db_path = "ingested_data.db"
table_names = ["sample_table"]  # Example list of tables

if table_names:
    selected_table = st.selectbox(translate("select_date", lang), table_names)
    if selected_table:
        data = fetch_table_data(db_path, selected_table)
        if 'governorID' in data.columns and 'name' in data.columns:
            g_id_with_name = data[['governorID', 'name']].drop_duplicates()
            g_id_with_name['display'] = g_id_with_name.apply(lambda row: f"{row['governorID']} ({row['name']})", axis=1)
            display_to_g_id = dict(zip(g_id_with_name['display'], g_id_with_name['governorID']))
            selected_display = st.sidebar.selectbox(translate("select_governor", lang), g_id_with_name['display'])
            selected_g_id = display_to_g_id[selected_display]

            if selected_g_id:
                st.header(f"{translate('trend_analysis', lang)} {selected_display}")
                aggregated_data = aggregate_data(db_path, table_names)
                aggregated_data = aggregated_data[aggregated_data['governorID'] == int(selected_g_id)]

                if not aggregated_data.empty:
                    trend_columns = ['power', 'killpoints', 'deads']
                    for column in trend_columns:
                        if column in aggregated_data.columns:
                            aggregated_data[column] = pd.to_numeric(aggregated_data[column], errors='coerce')
                            
                            chart = (
                                alt.Chart(aggregated_data)
                                .mark_line(strokeWidth=3)
                                .encode(
                                    x=alt.X('Date:T', title='Date', axis=alt.Axis(labelAngle=-45)),
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