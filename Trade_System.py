from config import STARTING_BALANCE
from DB_Manager import DatabaseManager
from Data_Processor import DataProcessor
from TradeLogic import TradeLogic
import logging

# Main execution class
class TradingSystem:
    def __init__(self, db_config):
        self.db_manager = DatabaseManager(db_config)
        self.data_processor = DataProcessor(self.db_manager)
        self.trade_logic = TradeLogic(self.db_manager)
        self.portfolio_balance = STARTING_BALANCE

    def run(self):
        dates = self.db_manager.get_available_dates()
        for date in dates:
            stop_loss_date = f'{date}T14:30:00.000000Z'
            print(f'Generating for {date}')
            tickers = self.data_processor.get_eligible_tickers(date) # returns all tickers elibgible based on filters as a list
            
            if not tickers:
                print(f"No eligible tickers for {date}.")
                continue

            top_20_rel_vol_stocks = self.data_processor.get_top_20_relative_volume_stocks(date, tickers) # Takes eligbile tickers and returns those with the 20 highest rel vol for the day
            if not top_20_rel_vol_stocks:
                print(f"No top 20 relative volume stocks for {date}.")
                continue

            for ticker in top_20_rel_vol_stocks:
            # Get first 5 min bar for eligible tickers
                first_5min_data = self.data_processor.get_first_5_minutes(date, ticker)
               
                if first_5min_data.empty:
                    print(f"No first 5-minute bar data for {ticker} on {date}. Skipping to next stock")
                    continue

                rest_of_day_data = self.data_processor.get_rest_of_day_data(date, ticker)


                entry_price, exit_price, signal_type = self.trade_logic.generate_signals(first_5min_data, rest_of_day_data, stop_loss_date=stop_loss_date)
               
                self.portfolio_balance = self.trade_logic.calculate_portfolio(entry_price, exit_price, signal_type, self.portfolio_balance)
            