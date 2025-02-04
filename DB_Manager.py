
from config import DB_CONFIG
import pandas as pd
import psycopg2
import logging

# Database management class
class DatabaseManager:
    def __init__(self, config):
        self.config = config

    def get_connection(self):
        """Establish a connection to the database."""
        return psycopg2.connect(
            host=self.config['host'],
            port=self.config['port'],
            user=self.config['user'],
            password=self.config['password'],
            database=self.config['database']
        )

    def execute_query(self, query):
        """Execute a SQL query and return the results as a DataFrame."""
        conn = self.get_connection()
        try:
            return pd.read_sql(query, conn)
        finally:
            conn.close()

    def get_available_dates(self):
        """
        Fetch all unique dates (without time) from QuestDB stock data table.
        Returns:
            list: A list of unique dates as strings in 'YYYY-MM-DD' format.
        """
        query = "SELECT DISTINCT CAST(window_start AS DATE) AS date FROM 5_min_bars ORDER BY date ASC;"
        try:
            # Execute the query and fetch results
            dates_df = self.execute_query(query)
            # Convert the timestamps to date only and drop duplicates
            dates_df['date'] = dates_df['date'].dt.date
            dates_df = dates_df.drop_duplicates(subset=['date'])
            # Convert the dates to string format and return as a list
            date_list = dates_df['date'].apply(lambda x: x.strftime('%Y-%m-%d')).tolist()
            return date_list
        except Exception as e:
            logging.error(f"Error fetching dates: {e}")
            return []