# Zerodha Trading Bot
A Python-based automated trading bot for the Zerodha Kite Connect platform. This bot implements a swing trading strategy focusing on high-quality stocks.
## Features
*   **Automated Trading**: Buys and sells based on predefined logic.
*   **Strategy**:
    *   **Buy**: Enters when a watchlist stock dips significantly (e.g., -2% in a day).
    *   **Sell**: Exits at **+10% Profit**.
    *   **Stop Loss**: Exits at **-5% Loss** to protect capital.
*   **Paper Trading Mode**: Includes a `paper_bot.py` that uses free Yahoo Finance data to simulate trades without real money.
*   **Safety**: Includes a `DRY_RUN` mode to prevent accidental real orders.
## Prerequisites
*   Python 3.x
*   Zerodha Kite Connect Account (for live trading)
## Installation
1.  Clone the repository:
    ```bash
    git clone https://github.com/YOUR_USERNAME/zerodha-trading-bot.git
    cd zerodha-trading-bot
    ```
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configuration**:
    *   Rename `.env.example` to `.env` (or create a new `.env` file).
    *   Add your Zerodha API credentials:
        ```text
        ZERODHA_API_KEY=your_api_key
        ZERODHA_API_SECRET=your_api_secret
        ```
## Usage
### 1. Paper Trading (Free Simulation)
Test the strategy with fake money using Yahoo Finance data.
```bash
python paper_bot.py
```
*   Tracks portfolio in `portfolio.json`.
*   Starts with ₹1,00,000 virtual capital.
### 2. Live Trading (Real Money)
**⚠️ WARNING**: Trading involves financial risk. Use at your own risk.
1.  Open `config.py` and ensure `DRY_RUN = True` (default) to test connection and logic without placing orders.
2.  Run the bot:
    ```bash
    python trading_bot.py
    ```
3.  To enable real orders, change `DRY_RUN = False` in `config.py`.
## Disclaimer
This software is for educational purposes only. Do not risk money you cannot afford to lose. The authors are not responsible for any financial losses.
