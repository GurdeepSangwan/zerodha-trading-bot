import logging
import time
import sys
from kiteconnect import KiteConnect, KiteTicker
import pandas as pd
import config
import utils

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_access_token(kite):
    """
    Flow to get access token from user if not already available/valid.
    """
    print(f"Login URL: {kite.login_url()}")
    request_token = input("Login and enter the Request Token here: ")
    try:
        data = kite.generate_session(request_token, api_secret=config.API_SECRET)
        kite.set_access_token(data["access_token"])
        logging.info(f"Access Token generated: {data['access_token']}")
        print("Copy this Access Token to your .env file to avoid logging in every time.")
        return data["access_token"]
    except Exception as e:
        logging.error(f"Error generating session: {e}")
        sys.exit(1)

def place_order(kite, symbol, transaction_type, quantity):
    """
    Places a market order.
    """
    if config.DRY_RUN:
        logging.info(f"[DRY RUN] Would place {transaction_type} order for {quantity} of {symbol}")
        return

    try:
        order_id = kite.place_order(
            tradingsymbol=symbol,
            exchange=config.EXCHANGE,
            transaction_type=transaction_type,
            quantity=quantity,
            variety=kite.VARIETY_REGULAR,
            order_type=kite.ORDER_TYPE_MARKET,
            product=kite.PRODUCT_CNC,
            validity=kite.VALIDITY_DAY
        )
        logging.info(f"Order placed. ID: {order_id}")
    except Exception as e:
        logging.error(f"Order placement failed: {e}")

def run_bot():
    # Initialize Kite Connect
    kite = KiteConnect(api_key=config.API_KEY)

    # Set access token if available
    if config.ACCESS_TOKEN:
        kite.set_access_token(config.ACCESS_TOKEN)
    else:
        get_access_token(kite)

    # Verify connection
    try:
        profile = kite.profile()
        logging.info(f"Connected as {profile['user_name']}")
    except Exception as e:
        logging.error(f"Connection failed: {e}. Token might be expired.")
        get_access_token(kite)

    # Get Instrument Lookup
    instrument_lookup = utils.get_instrument_lookup(kite)

    while True:
        logging.info("Starting scan...")
        
        # 1. Check Holdings for Exits
        try:
            holdings = kite.holdings()
            for holding in holdings:
                symbol = holding['tradingsymbol']
                quantity = holding['quantity']
                pnl_pct = holding['pnl'] / (holding['average_price'] * quantity) * 100 if quantity > 0 else 0
                
                # Current PnL percentage calculation might need adjustment based on API response structure
                # Kite returns 'pnl' as total value. Let's calculate percentage manually.
                current_price = holding['last_price']
                avg_price = holding['average_price']
                if avg_price > 0:
                    pnl_pct = ((current_price - avg_price) / avg_price) * 100
                else:
                    pnl_pct = 0

                logging.info(f"Holding: {symbol}, PnL: {pnl_pct:.2f}%")

                if pnl_pct >= (config.TARGET_PROFIT * 100):
                    logging.info(f"Target hit for {symbol}. Selling...")
                    place_order(kite, symbol, kite.TRANSACTION_TYPE_SELL, quantity)
                elif pnl_pct <= -(config.STOP_LOSS * 100):
                    logging.info(f"Stop Loss hit for {symbol}. Selling...")
                    place_order(kite, symbol, kite.TRANSACTION_TYPE_SELL, quantity)
        
        except Exception as e:
            logging.error(f"Error fetching holdings: {e}")

        # 2. Check Watchlist for Entries
        # We need to fetch quotes for the watchlist
        watchlist_tokens = []
        for symbol in config.WATCHLIST:
            if symbol in instrument_lookup:
                watchlist_tokens.append(instrument_lookup[symbol])
            else:
                logging.warning(f"Symbol {symbol} not found in instrument lookup.")
        
        # Convert tokens to 'Exchange:Symbol' format for quote call? 
        # Kite Connect quote takes list of 'exchange:tradingsymbol'
        quote_ids = [f"{config.EXCHANGE}:{symbol}" for symbol in config.WATCHLIST]
        
        try:
            quotes = kite.quote(quote_ids)
            for symbol in config.WATCHLIST:
                key = f"{config.EXCHANGE}:{symbol}"
                if key in quotes:
                    data = quotes[key]
                    last_price = data['last_price']
                    ohlc = data['ohlc']
                    close_price = ohlc['close']
                    
                    # Strategy: Buy if price dropped > 2% from yesterday's close
                    # This is a simple "Buy Low" proxy. 
                    # For more complex "Quality at Low", we might want RSI.
                    
                    pct_change = ((last_price - close_price) / close_price) * 100
                    
                    logging.info(f"{symbol}: {last_price} ({pct_change:.2f}%)")
                    
                    if pct_change < -2.0: # Buy dip of 2%
                        logging.info(f"Buying signal for {symbol} (Dip {pct_change:.2f}%)")
                        # Quantity logic: Fixed amount or fixed quantity?
                        # Let's assume 1 share for now or calculate based on a budget
                        qty = 1 
                        place_order(kite, symbol, kite.TRANSACTION_TYPE_BUY, qty)

        except Exception as e:
            logging.error(f"Error fetching quotes: {e}")

        logging.info("Scan complete. Sleeping for 5 minutes...")
        time.sleep(300)

if __name__ == "__main__":
    run_bot()
