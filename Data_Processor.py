from DB_Manager import DatabaseManager

# Data processing class
class DataProcessor:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def get_eligible_tickers(self, date, volume_threshold=1000000, atr_threshold=0.5, rel_vol_threshold=100):

        """Fetch eligible tickers based on volume, ATR, and relative volume criteria."""
        vol_query = f"""
            SELECT DISTINCT ticker
            FROM precomputed_metrics
            WHERE rolling_14_day_avg_volume > {volume_threshold}
            AND date = '{date}T00:00:00.000000Z';
        """
        atr_query = f"""
            SELECT DISTINCT ticker
            FROM daily_bars_atr
            WHERE atr_14 > {atr_threshold}
            AND window_start = '{date}T14:30:00.000000Z';
        """
        rel_vol_query = f"""
            SELECT DISTINCT ticker
            FROM first_5min_volume
            WHERE rel_volume_pct > {rel_vol_threshold}
            AND date = '{date}T00:00:00.000000Z';
        """
        vol_tickers = self.db_manager.execute_query(vol_query)['ticker'].tolist()
        atr_tickers = self.db_manager.execute_query(atr_query)['ticker'].tolist()
        rel_vol_tickers = self.db_manager.execute_query(rel_vol_query)['ticker'].tolist()

        return list(set(vol_tickers) & set(atr_tickers) & set(rel_vol_tickers))


    def get_top_20_relative_volume_stocks(self, date, tickers):
        """
        Fetch the highest percentage relative volume among the top 20 tickers with 
        the largest relative volume for a given day from the input tickers.

        Parameters:
            date (str): The date for which to fetch data (format: 'YYYY-MM-DD').
            tickers (list): List of ticker symbols to filter by.

        Returns:
            float: The highest percentage relative volume among the top 20 tickers for the day.
        """
        # Ensure tickers list is not empty
        if not tickers:
            print("Tickers list is empty. Returning None.")
            return None

        tickers_str = "', '".join(tickers)
        query = f"""
        SELECT ticker, rel_volume_pct
        FROM first_5min_volume
        WHERE ticker IN ('{tickers_str}')
          AND date = '{date}T00:00:00.000Z'
        ORDER BY rel_volume_pct DESC
        LIMIT 20;
        """
        # Execute the query and fetch the results
        df = self.db_manager.execute_query(query)
        df = df['ticker'].tolist()

        if not df:
            print(f"No data found for the given tickers on {date}. Returning an empty DataFrame.")
        else:
            print(f"Top 20 tickers by relative volume for {date} fetched successfully.")
        return df


    def get_first_5_minutes(self, date, ticker):
        """
        Fetch the first 5-minute bar for eligible tickers for a given day from the 5_min_bars table,
        and return the top 20 stocks by volume sorted from highest to lowest.

        Parameters:
            date (str): The date for which to fetch data (format: 'YYYY-MM-DD').
            tickers (list): List of ticker symbols to filter by.

        Returns:
            pd.DataFrame: A DataFrame containing the first 5-minute bar data for the top 20 stocks.
        """
        if not ticker:
            print(f"No tickers provided for {date}. Returning an empty DataFrame.")
            return pd.DataFrame()

        query = f"""
            SELECT
                ticker,
                window_start,
                volume,
                high,
                low,
                close
            FROM
                5_min_bars
                WHERE
                    ticker = '{ticker}'
                    AND window_start = '{date}T14:30:00.000Z'
        """
        df = self.db_manager.execute_query(query)
        return df.reset_index(drop=True)
    

    def get_rest_of_day_data(self, date, ticker):
        """Fetch the rest of the day's data for the tickers."""
        query = f"""
            SELECT ticker, window_start, volume, high, low, close
            FROM stocks_data
            WHERE ticker = '{ticker}'
              AND window_start BETWEEN '{date}T14:34:00.000Z' AND '{date}T21:00:00.000Z'
        """
        df = self.db_manager.execute_query(query)
        return df.reset_index(drop=True)
