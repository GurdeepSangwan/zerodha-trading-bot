import pandas as pd
import logging

def get_instrument_lookup(kite, exchange="NSE"):
    """
    Fetches instruments from Kite and returns a dictionary mapping
    TradingSymbol -> InstrumentToken for the specified exchange.
    """
    logging.info("Fetching instruments...")
    instruments = kite.instruments(exchange)
    lookup = {}
    for instrument in instruments:
        lookup[instrument['tradingsymbol']] = instrument['instrument_token']
    return lookup

def calculate_rsi(prices, period=14):
    """
    Calculates RSI for a given list/series of prices.
    Returns the last RSI value.
    """
    if len(prices) < period:
        return None
    
    series = pd.Series(prices)
    delta = series.diff()
    
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi.iloc[-1]

def is_market_open():
    """
    Checks if the market is currently open.
    (Simple time check, can be expanded)
    """
    # TODO: Implement time check based on exchange hours
    return True
