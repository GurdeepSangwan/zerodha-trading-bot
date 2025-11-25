import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Zerodha API Credentials
API_KEY = os.getenv("ZERODHA_API_KEY")
API_SECRET = os.getenv("ZERODHA_API_SECRET")
ACCESS_TOKEN = os.getenv("ZERODHA_ACCESS_TOKEN") # Optional if you want to reuse tokens

# Trading Parameters
TARGET_PROFIT = 0.10  # 10%
STOP_LOSS = 0.05      # 5%

# Quality Watchlist (Nifty 50 or similar blue chips)
# Using a sample list for now. You can expand this.
WATCHLIST = [
    "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK",
    "HINDUNILVR", "SBIN", "BHARTIARTL", "ITC", "KOTAKBANK",
    "LTIM", "AXISBANK", "LT", "BAJFINANCE", "MARUTI"
]

# Exchange
EXCHANGE = "NSE"

# Safety
DRY_RUN = True  # Set to False to place real orders
