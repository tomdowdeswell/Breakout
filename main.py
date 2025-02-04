from config import DB_CONFIG
from Trade_System import TradingSystem


if __name__ == "__main__":
    trading_system = TradingSystem(DB_CONFIG)
    trading_system.run()
  