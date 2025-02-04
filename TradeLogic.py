from DB_Manager import DatabaseManager
import pandas as pd

# Trade logic class
class TradeLogic:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def get_atr(self, date, ticker):
        """Fetch ATR value for a given date and ticker."""
        query = f"""
            SELECT atr_14
            FROM daily_bars_atr
            WHERE ticker = '{ticker}'
              AND window_start = '{date}';
        """
        df = self.db_manager.execute_query(query)
        if not df.empty:
            return df.iloc[0, 0] * 0.1
        raise ValueError(f"No ATR value found for ticker {ticker} on {date}.")

    def generate_signals(self, first_5min_data, rest_of_day_data, stop_loss_date):
        print('Generating signals....')

        # Convert Series to DataFrame if renaming columns
        if isinstance(first_5min_data, pd.Series):
            first_5min_stats = first_5min_data.to_frame().T
        
        # rename columns 
        first_5min_data = first_5min_data.rename(columns={
            'high': 'high_5min',
            'low': 'low_5min',
            'close': 'close_5min'
        })

        first_5min_data = first_5min_data.reset_index(drop=True)
        rest_of_day_data = rest_of_day_data.reset_index(drop=True)

        merged_data = pd.merge(
            rest_of_day_data,
            first_5min_data,
            on=['ticker'],
            how='left'
        )

        merged_data['position_taken'] = False
        merged_data['trade_signal'] = None
        merged_data['entry_price'] = None
        merged_data['exit_price'] = None
        merged_data['stop_loss_price'] = None  # Track the stop loss price

        trade_details = self.resolve_signals(merged_data, stop_loss_date)  # Pass stop_loss_pct here

    # Return trade details to be used in calculate_portfolio
        return trade_details
    


    def resolve_signals(self, df, stop_loss_date):
        """Resolve signals and track stop loss for each trade, ensuring one trade per day per stock."""
        
        print(f"Resolving signals for ticker: {df['ticker'].iloc[0]}")

        
        trade_details = []
        """Resolve signals and update portfolio balance."""
        trade_executed = False  # Track if a trade has been executed
        entry_price = None
        exit_price = None
        exit_reason = None
        stop_loss_price = None
        signal_type = None

        ticker = df['ticker'].iloc[0]
        high_5min = df['high_5min'].iloc[0]
        low_5min = df['low_5min'].iloc[0]

        for idx, row in df.iterrows():
            
            # Skip further entry processing if a trade has already been executed
            if trade_executed:
                # Check stop loss or end-of-day exit
                if entry_price is not None:
                    # Stop-loss logic for LONG and SHORT trades
                    if signal_type == 'LONG' and row['low'] <= stop_loss_price:
                        exit_price = stop_loss_price
                        exit_reason = 'STOP LOSS'
                        print(f"Trade exited (STOP LOSS): Ticker={ticker}, Entry={entry_price}, Exit={exit_price}")
                        break  # Exit loop after processing the stop loss
                    elif signal_type == 'SHORT' and row['high'] >= stop_loss_price:
                        exit_price = stop_loss_price
                        exit_reason = 'STOP LOSS'
                        print(f"Trade exited (STOP LOSS): Ticker={ticker}, Entry={entry_price}, Exit={exit_price}")
                        break  # Exit loop after processing the stop loss

                    # If it's the last row, exit at the day's close
                    if idx == len(df) - 1:
                        exit_price = row['close']
                        print(f"Trade exited (END OF DAY): Ticker={ticker}, Entry={entry_price}, Exit={exit_price}")
                        break
                continue  # Skip further rows once the trade is executed and processed

            # Entry logic for the first valid trade
            if not trade_executed:
                if row['high'] > high_5min:  # LONG
                    entry_price = row['close']
                    stop_loss_price = entry_price - self.get_atr(stop_loss_date, ticker)
                    signal_type = 'LONG'
                    trade_executed = True
                    print(f"Trade entered (LONG): Ticker={ticker}, Entry={entry_price}, Stop Loss={stop_loss_price}")

                elif row['low'] < low_5min:  # SHORT
                    entry_price = row['close']
                    stop_loss_price = entry_price + self.get_atr(stop_loss_date, ticker)
                    signal_type = 'SHORT'
                    trade_executed = True
                    print(f"Trade entered (SHORT): Ticker={ticker}, Entry={entry_price}, Stop Loss={stop_loss_price}")

        return entry_price, exit_price, signal_type

    def calculate_portfolio(self, entry_price, exit_price, signal_type, balance):
        """Calculate PnL and update portfolio balance."""
        # Validate inputs and handle None gracefully
        if entry_price is None or exit_price is None:
            print(f"Warning: Skipping trade due to missing price. Entry: {entry_price}, Exit: {exit_price}")
            return balance  # Return the balance unchanged

        if entry_price <= 0 or exit_price <= 0:
            print(f"Warning: Skipping trade due to invalid price. Entry: {entry_price}, Exit: {exit_price}")
            return balance  # Return the balance unchanged

        if balance is None:
            raise ValueError("Balance must be initialized.")

        # Calculate PnL based on trade direction
        if signal_type == 'LONG':
            pnl = exit_price - entry_price
        elif signal_type == 'SHORT':
            pnl = entry_price - exit_price
        else:
            print(f"Warning: Invalid signal type '{signal_type}'. Skipping trade.")
            return balance  # Return the balance unchanged

        # Update balance
        balance += pnl
        print(f"This is the PnL for the trade: {pnl}")
        print(f"Updated Balance: {balance}")

        return balance