import os
import sqlite3
import pandas as pd
import streamlit as st
import altair as alt

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
    # Escape table name to handle special cases
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
st.title("Kingdom 1007 Stats tracker")

folder_path = 'data/'
db_path = "ingested_data.db"

if folder_path:
    try:
        # Ingest CSV files into SQLite
        ingest_csv_to_sqlite(folder_path, db_path)

        # Fetch table names
        table_names = get_table_names(db_path)

        if table_names:
            selected_table = st.selectbox("Select a date to display:", table_names)

            if selected_table:
                st.write(f"Displaying data for table: {selected_table}")
                data = fetch_table_data(db_path, selected_table)

                # Add filters for the selected table
                st.sidebar.header("Filter Options")
                filter_columns = st.sidebar.multiselect("Select columns to filter:", data.columns)

                filtered_data = data.copy()
                for column in filter_columns:
                    unique_values = data[column].unique()
                    filter_value = st.sidebar.selectbox(f"Filter {column}:", unique_values)
                    filtered_data = filtered_data[filtered_data[column] == filter_value]

                # Add range filters for a selected column
                st.sidebar.header("Range Filters")
                numeric_columns = data.select_dtypes(include=['number']).columns

                if not numeric_columns.empty:
                    selected_numeric_column = st.sidebar.selectbox("Select a column for range filter:", numeric_columns)

                    if selected_numeric_column:
                        min_val = float(data[selected_numeric_column].min())
                        max_val = float(data[selected_numeric_column].max())
                        range_values = st.sidebar.slider(
                            f"Select range for {selected_numeric_column}:", min_val, max_val, (min_val, max_val)
                        )
                        filtered_data = filtered_data[filtered_data[selected_numeric_column].between(*range_values)]

                st.write(filtered_data)

                # Add g_id filter for trend visualization
                if 'governorID' in data.columns and 'name' in data.columns:
                    g_id_with_name = data[['governorID', 'name']].drop_duplicates()
                    g_id_with_name['display'] = g_id_with_name.apply(lambda row: f"{row['governorID']} ({row['name']})", axis=1)

                    display_to_g_id = dict(zip(g_id_with_name['display'], g_id_with_name['governorID']))
                    selected_display = st.sidebar.selectbox("Select governorID for trend visualization:", g_id_with_name['display'])
                    selected_g_id = display_to_g_id[selected_display]

                    if selected_g_id:
                        st.header(f"Trend Analysis for governorID: {selected_display}")
                        aggregated_data = aggregate_data(db_path, table_names)

                        # Filter aggregated data by selected g_id
                        aggregated_data = aggregated_data[aggregated_data['governorID'] == int(selected_g_id)]

                        if not aggregated_data.empty:
                            # Ensure numeric data consistency for trend columns
                            trend_columns = ['power', 'killpoints', 'deads']
                            for column in trend_columns:
                                if column in aggregated_data.columns:
                                    aggregated_data[column] = pd.to_numeric(aggregated_data[column], errors='coerce')

                                    # Create a line chart with markers
                                    chart = alt.Chart(aggregated_data).mark_line().encode(
                                        x='Date:T',
                                        y=alt.Y(column, title=f"{column}"),
                                        tooltip=['Date:T', column]
                                    ).properties(
                                        title=f"Trend of {column} over Time for governorID {selected_display}",
                                        width=800,
                                        height=400
                                    ).mark_point()  # Adding markers to the line chart

                                    st.altair_chart(chart)
                                else:
                                    st.warning(f"Column {column} is missing or non-numeric.")
                        else:
                            st.warning("No data available for the selected g_id.")

        else:
            st.warning("No tables found in the database.")
    except Exception as e:
        st.error(f"An error occurred: {e}")
