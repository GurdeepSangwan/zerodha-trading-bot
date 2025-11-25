import yfinance as yf
import pandas as pd
import time
import json
import os
import logging
from datetime import datetime

# Configuration
WATCHLIST = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
    "HINDUNILVR.NS", "SBIN.NS", "BHARTIARTL.NS", "ITC.NS", "KOTAKBANK.NS"
]
TARGET_PROFIT = 0.10  # 10%
STOP_LOSS = 0.05      # 5%
BUY_DIP_THRESHOLD = -2.0 # Buy if drops 2% in a day
PORTFOLIO_FILE = "portfolio.json"

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def load_portfolio():
    if os.path.exists(PORTFOLIO_FILE):
        with open(PORTFOLIO_FILE, 'r') as f:
            return json.load(f)
    return {"balance": 100000, "holdings": {}} # Start with ₹1 Lakh fake money

def save_portfolio(portfolio):
    with open(PORTFOLIO_FILE, 'w') as f:
        json.dump(portfolio, f, indent=4)

def get_current_price(symbol):
    try:
        ticker = yf.Ticker(symbol)
        # fast_info is faster than history() for current price
        price = ticker.fast_info['last_price']
        return price
    except Exception as e:
        logging.error(f"Error fetching price for {symbol}: {e}")
        return None

def get_day_change(symbol):
    try:
        ticker = yf.Ticker(symbol)
        # Get previous close
        prev_close = ticker.fast_info['previous_close']
        current = ticker.fast_info['last_price']
        if prev_close:
            change_pct = ((current - prev_close) / prev_close) * 100
            return change_pct, current
        return 0, current
    except Exception as e:
        logging.error(f"Error fetching change for {symbol}: {e}")
        return 0, 0

def run_paper_bot():
    portfolio = load_portfolio()
    logging.info(f"--- Starting Paper Bot ---")
    logging.info(f"Current Balance: ₹{portfolio['balance']:.2f}")
    
    while True:
        logging.info("\nScanning market...")
        
        # 1. Check Holdings for Exit
        current_holdings = list(portfolio["holdings"].keys())
        for symbol in current_holdings:
            data = portfolio["holdings"][symbol]
            current_price = get_current_price(symbol)
            
            if not current_price:
                continue
                
            buy_price = data["avg_price"]
            quantity = data["quantity"]
            
            pnl_pct = ((current_price - buy_price) / buy_price) * 100
            pnl_value = (current_price - buy_price) * quantity
            
            logging.info(f"[HOLD] {symbol}: Buy @ {buy_price:.2f}, Curr @ {current_price:.2f}, PnL: {pnl_pct:.2f}% (₹{pnl_value:.2f})")
            
            if pnl_pct >= (TARGET_PROFIT * 100):
                logging.info(f"✅ TARGET HIT for {symbol}! Selling...")
                portfolio["balance"] += current_price * quantity
                del portfolio["holdings"][symbol]
                save_portfolio(portfolio)
                
            elif pnl_pct <= -(STOP_LOSS * 100):
                logging.info(f"🛑 STOP LOSS HIT for {symbol}. Selling...")
                portfolio["balance"] += current_price * quantity
                del portfolio["holdings"][symbol]
                save_portfolio(portfolio)

        # 2. Check Watchlist for Entry
        for symbol in WATCHLIST:
            # Skip if already holding
            if symbol in portfolio["holdings"]:
                continue
                
            change_pct, current_price = get_day_change(symbol)
            
            if current_price == 0: 
                continue

            logging.info(f"[WATCH] {symbol}: ₹{current_price:.2f} ({change_pct:.2f}%)")
            
            if change_pct < BUY_DIP_THRESHOLD:
                logging.info(f"📉 DIP DETECTED for {symbol} ({change_pct:.2f}%). Buying...")
                
                # Buy logic: Invest max ₹10,000 per stock
                invest_amount = 10000
                if portfolio["balance"] >= invest_amount:
                    quantity = int(invest_amount / current_price)
                    if quantity > 0:
                        cost = quantity * current_price
                        portfolio["balance"] -= cost
                        portfolio["holdings"][symbol] = {
                            "avg_price": current_price,
                            "quantity": quantity,
                            "buy_time": str(datetime.now())
                        }
                        save_portfolio(portfolio)
                        logging.info(f"Bought {quantity} qty of {symbol} @ ₹{current_price:.2f}")
                else:
                    logging.warning("Insufficient funds to buy.")

        logging.info("Scan complete. Sleeping for 60 seconds...")
        time.sleep(60)

if __name__ == "__main__":
    run_paper_bot()
