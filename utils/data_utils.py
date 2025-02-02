import sqlite3
import pandas as pd

def get_table_names(db_path):
    """Fetch table names from SQLite database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    return tables

def fetch_table_data(db_path, table_name):
    """Fetch data from a specific table."""
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(f'SELECT * FROM "{table_name}"', conn)
    conn.close()
    return df

def aggregate_data(db_path, table_names):
    """Aggregate data from multiple tables."""
    aggregated_data = []
    for table_name in table_names:
        df = fetch_table_data(db_path, table_name)
        df['Date'] = pd.to_datetime(table_name, format="%m%d%Y", errors='coerce')
        aggregated_data.append(df)
    return pd.concat(aggregated_data, ignore_index=True)
