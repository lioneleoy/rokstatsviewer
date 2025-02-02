import os
import sqlite3
import pandas as pd
import streamlit as st
import altair as alt

# Translation dictionary
translations = {
    "en": {
        "title": "Kingdom 1007 Stats Tracker",
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
        "warning_missing_column": "Column {column} is missing or non-numeric.",
        "kills_and_deads_summary": "Kills and Deads Summary"
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
        "error_ocurrido": "Ocurrió un error: {error}",
        "warning_missing_column": "La columna {column} falta o no es numérica.",
        "kills_and_deads_summary": "Resumen de Kills y Deads"
    }
}

# Function to translate text
def translate(text, lang="en"):
    return translations[lang].get(text, text)

# Function to read all CSV files in a folder and ingest them into SQLite
def ingest_csv_to_sqlite(folder_path, db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for file_name in os.listdir(folder_path):
        if file_name.endswith('.csv'):
            file_path = os.path.join(folder_path, file_name)
            table_name = os.path.splitext(file_name)[0]
            df = pd.read_csv(file_path)

            for column in df.columns:
                if df[column].dtype == 'object':
                    try:
                        df[column] = df[column].str.replace(',', '').astype(int)
                    except ValueError:
                        pass

            df.to_sql(table_name, conn, if_exists='replace', index=False)

    conn.commit()
    conn.close()

# Function to fetch table names from SQLite database
def get_table_names(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    return tables

# Function to fetch data from a specific table in SQLite database
def fetch_table_data(db_path, table_name):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(f'SELECT * FROM "{table_name}"', conn)
    conn.close()
    return df

# Function to aggregate data across all tables
def aggregate_data(db_path, table_names):
    aggregated_data = []

    for table_name in table_names:
        df = fetch_table_data(db_path, table_name)
        df['Date'] = pd.to_datetime(table_name, format="%m%d%Y", errors='coerce')
        aggregated_data.append(df)

    return pd.concat(aggregated_data, ignore_index=True)

# Function to get kills and deads changes for each governor, formatted by date
def get_kills_and_deads_summary(df):
    # Extract the columns needed for summary
    kills_summary = df[['governorID', 'name', 'Date', 'killpoints']].copy()
    deads_summary = df[['governorID', 'name', 'Date', 'deads']].copy()

    # Format the Date as MM/DD
    kills_summary['Date'] = kills_summary['Date'].dt.strftime('%m/%d')
    deads_summary['Date'] = deads_summary['Date'].dt.strftime('%m/%d')

    # Sort the data by Date (important for calculating changes)
    kills_summary = kills_summary.sort_values(by=['governorID', 'Date'])
    deads_summary = deads_summary.sort_values(by=['governorID', 'Date'])

    # Calculate the change (difference) in killpoints and deads between consecutive dates
    kills_summary['killpoints_change'] = kills_summary.groupby('governorID')['killpoints'].diff().fillna(0)
    deads_summary['deads_change'] = deads_summary.groupby('governorID')['deads'].diff().fillna(0)

    # Pivot the data so that Date becomes columns
    kills_pivot = kills_summary.pivot_table(index=['governorID', 'name'], columns='Date', values='killpoints_change', aggfunc='last').reset_index()
    deads_pivot = deads_summary.pivot_table(index=['governorID', 'name'], columns='Date', values='deads_change', aggfunc='last').reset_index()

    return kills_pivot, deads_pivot

# Streamlit app
st.set_page_config(page_title="Kingdom 1007 Stats Tracker", layout="wide")

# Language selection
lang = st.sidebar.selectbox("Choose language / Elige idioma:", ["en", "es"])

# Title
st.title(translate("title", lang))

folder_path = 'data/'
db_path = "ingested_data.db"

# Ingest CSV files into SQLite
if folder_path:
    try:
        ingest_csv_to_sqlite(folder_path, db_path)

        # Fetch table names
        table_names = get_table_names(db_path)

        if table_names:
            # Create sidebar navigation
            page = st.sidebar.radio("Select a page", ["Summary Table", "Trend Analysis", translate("kills_and_deads_summary", lang)])

            if page == "Summary Table":
                selected_table = st.sidebar.selectbox(translate("select_date", lang), table_names)

                if selected_table:
                    st.markdown(f"### {translate('display_data_for_table', lang)} {selected_table}")

                    data = fetch_table_data(db_path, selected_table)

                    # Sidebar Filters
                    with st.sidebar.expander(translate("filter_options", lang)):
                        filter_columns = st.multiselect(translate("select_columns_to_filter", lang), data.columns)

                        filtered_data = data.copy()
                        for column in filter_columns:
                            unique_values = data[column].unique()
                            filter_value = st.selectbox(f"{translate('filter_options', lang)} {column}:", unique_values)
                            filtered_data = filtered_data[filtered_data[column] == filter_value]

                        numeric_columns = data.select_dtypes(include=['number']).columns
                        if not numeric_columns.empty:
                            selected_numeric_column = st.selectbox(f"{translate('select_columns_to_filter', lang)}", numeric_columns)
                            if selected_numeric_column:
                                min_val = float(data[selected_numeric_column].min())
                                max_val = float(data[selected_numeric_column].max())
                                range_values = st.slider(
                                    f"{translate('select_columns_to_filter', lang)} {selected_numeric_column}:", min_val, max_val, (min_val, max_val)
                                )
                                filtered_data = filtered_data[filtered_data[selected_numeric_column].between(*range_values)]

                    # Expanded view of the data table
                    with st.expander("View Data Table", expanded=True):  # Expanding by default
                        st.dataframe(filtered_data, use_container_width=True)

            elif page == "Trend Analysis":
                selected_table = st.sidebar.selectbox(translate("select_date", lang), table_names)

                if selected_table:
                    st.markdown(f"### {translate('display_data_for_table', lang)} {selected_table}")

                    data = fetch_table_data(db_path, selected_table)

                    # Trend Visualization
                    if 'governorID' in data.columns:
                        g_id_with_name = data[['governorID', 'name']].drop_duplicates()
                        g_id_with_name['display'] = g_id_with_name.apply(lambda row: f"{row['governorID']} ({row['name']})", axis=1)

                        display_to_g_id = dict(zip(g_id_with_name['display'], g_id_with_name['governorID']))
                        selected_display = st.sidebar.selectbox(translate("select_governor", lang), g_id_with_name['display'])

                        if selected_display:
                            selected_g_id = display_to_g_id[selected_display]
                            st.markdown(f"### {translate('trend_analysis', lang)} {selected_display}")

                            aggregated_data = aggregate_data(db_path, table_names)
                            aggregated_data = aggregated_data[aggregated_data['governorID'] == int(selected_g_id)]

                            if not aggregated_data.empty:
                                trend_columns = st.multiselect("Select columns for trends:", ['power', 'killpoints', 'deads'])

                                for column in trend_columns:
                                    if column in aggregated_data.columns:
                                        aggregated_data[column] = pd.to_numeric(aggregated_data[column], errors='coerce')

                                        aggregated_data['Difference'] = aggregated_data[column].diff()
                                        aggregated_data['Label'] = aggregated_data['Difference'].apply(
                                            lambda x: f"{column.capitalize()}Gained +{x}" if x > 0 else (f"{column.capitalize()}Lost {abs(x)}" if x < 0 else "")
                                        )

                                        line_chart = alt.Chart(aggregated_data).mark_line(color='blue').encode(
                                            x='Date:T',
                                            y=alt.Y(column, title=f"{column}"),
                                            tooltip=['Date:T', column, 'Difference']
                                        )

                                        points_chart = alt.Chart(aggregated_data).mark_text(align='left', dx=5, dy=-10, fontSize=12).encode(
                                            x='Date:T',
                                            y=alt.Y(column),
                                            text='Label'
                                        )

                                        chart = (line_chart + points_chart).properties(
                                            title=translate("trend_of", lang).format(column=column, selected_display=selected_display),
                                            width=800,
                                            height=500
                                        )

                                        with st.expander(f"View Trend: {column}"):
                                            st.altair_chart(chart)

            elif page == translate("kills_and_deads_summary", lang):
                # Aggregate the data across all tables
                aggregated_data = aggregate_data(db_path, table_names)

                # Get Kills and Deads Summary (now showing changes instead of actual values)
                kills_changes_df, deads_changes_df = get_kills_and_deads_summary(aggregated_data)

                # Display Kills Changes Table
                st.markdown(f"### Kills Changes Summary")
                st.dataframe(kills_changes_df, use_container_width=True)

                # Display Deads Changes Table
                st.markdown(f"### Deads Changes Summary")
                st.dataframe(deads_changes_df, use_container_width=True)

        else:
            st.warning(translate("no_tables_found", lang))
    except Exception as e:
        st.error(translate("error_occurred", lang).format(error=e))