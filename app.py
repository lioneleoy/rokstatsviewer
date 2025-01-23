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
        "warning_missing_column": "Column {column} is missing or non-numeric.",
        "metrics": "Metrics for Selected Date Range",
        "power_change": "Power Change:",
        "deads_gained": "Deads Gained:",
        "kill_points_gained": "Kill Points Gained:",
        "date_range_filter": "Date Range Filter",
        "select_date_range": "Select Date Range:"
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
        "warning_missing_column": "La columna {column} falta o no es numérica.",
        "metrics": "Métricas para el rango de fechas seleccionado",
        "power_change": "Cambio de Poder:",
        "deads_gained": "Muertos Ganados:",
        "kill_points_gained": "Puntos de Muerte Ganados:",
        "date_range_filter": "Filtro de Rango de Fechas",
        "select_date_range": "Seleccionar Rango de Fechas:"
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
            table_name = os.path.splitext(file_name)[0]  # Use the file name without extension as table name
            df = pd.read_csv(file_path)

            # Convert numeric columns stored as strings with commas to integers
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
        df['Date'] = pd.to_datetime(table_name, format="%m%d%Y", errors='coerce')  # Convert table name to datetime
        aggregated_data.append(df)

    return pd.concat(aggregated_data, ignore_index=True)

# Streamlit app
# Language selection
lang = st.selectbox("Choose language / Elige idioma:", ["en", "es"])

# Title
st.title(translate("title", lang))

folder_path = 'data/'
db_path = "ingested_data.db"

if folder_path:
    try:
        # Ingest CSV files into SQLite
        ingest_csv_to_sqlite(folder_path, db_path)

        # Fetch table names
        table_names = get_table_names(db_path)

        if table_names:
            selected_table = st.selectbox(translate("select_date", lang), table_names)

            if selected_table:
                st.write(f"{translate('display_data_for_table', lang)} {selected_table}")
                data = fetch_table_data(db_path, selected_table)

                # Add filters for the selected table
                st.sidebar.header(translate("filter_options", lang))
                filter_columns = st.sidebar.multiselect(translate("select_columns_to_filter", lang), data.columns)

                filtered_data = data.copy()
                for column in filter_columns:
                    unique_values = data[column].unique()
                    filter_value = st.sidebar.selectbox(f"{translate('filter_options', lang)} {column}:", unique_values)
                    filtered_data = filtered_data[filtered_data[column] == filter_value]

                # Add range filters for a selected column
                numeric_columns = data.select_dtypes(include=['number']).columns

                if not numeric_columns.empty:
                    selected_numeric_column = st.sidebar.selectbox(f"{translate('select_columns_to_filter', lang)}", numeric_columns)

                    if selected_numeric_column:
                        min_val = float(data[selected_numeric_column].min())
                        max_val = float(data[selected_numeric_column].max())
                        range_values = st.sidebar.slider(
                            f"{translate('select_columns_to_filter', lang)} {selected_numeric_column}:", min_val, max_val, (min_val, max_val)
                        )
                        filtered_data = filtered_data[filtered_data[selected_numeric_column].between(*range_values)]

                # Display the filtered data
                st.dataframe(filtered_data, use_container_width=True)

                # Add date range filter for aggregated data
                st.sidebar.header(translate("date_range_filter", lang))
                aggregated_data = aggregate_data(db_path, table_names)

                if not aggregated_data.empty:
                    date_range = st.sidebar.date_input(
                        translate("select_date_range", lang),
                        value=(aggregated_data['Date'].min(), aggregated_data['Date'].max()),
                        min_value=aggregated_data['Date'].min(),
                        max_value=aggregated_data['Date'].max()
                    )

                    if date_range and len(date_range) == 2:
                        start_date, end_date = date_range

                        filtered_by_date = aggregated_data[
                            (aggregated_data['Date'] >= pd.Timestamp(start_date)) &
                            (aggregated_data['Date'] <= pd.Timestamp(end_date))
                        ]

                        if not filtered_by_date.empty:
                            # Display filtered data
                            st.write(f"Data from {start_date} to {end_date}:")
                            st.dataframe(filtered_by_date)

                            # Compute metrics
                            power_change = (
                                filtered_by_date['power'].iloc[-1] - filtered_by_date['power'].iloc[0]
                                if 'power' in filtered_by_date.columns else None
                            )
                            deads_gained = (
                                filtered_by_date['deads'].sum()
                                if 'deads' in filtered_by_date.columns else None
                            )
                            kill_points_gained = (
                                filtered_by_date['killpoints'].sum()
                                if 'killpoints' in filtered_by_date.columns else None
                            )

                            # Display metrics
                            st.subheader(translate("metrics", lang))
                            st.write(f"**{translate('power_change', lang)}** {power_change if power_change is not None else 'N/A'}")
                            st.write(f"**{translate('deads_gained', lang)}** {deads_gained if deads_gained is not None else 'N/A'}")
                            st.write(f"**{translate('kill_points_gained', lang)}** {kill_points_gained if kill_points_gained is not None else 'N/A'}")
                        else:
                            st.warning(translate("no_data_found", lang))
                else:
                    st.warning(translate("no_data_found", lang))
        else:
            st.warning(translate("no_tables_found", lang))
    except Exception as e:
        st.error(translate("error_occurred", lang).format(error=e))
