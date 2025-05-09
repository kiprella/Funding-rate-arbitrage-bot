# Funding Rate Arbitrage Bot

Funding Rate Arbitrage Bot is an automated trading system that identifies and exploits arbitrage opportunities between the spot and perpetual futures markets on cryptocurrency exchanges.

The bot enters a delta-neutral position by simultaneously:
- Buying an asset on the spot market
- Shorting the same asset on the perpetual futures market with the same position size

This strategy is profitable when the funding rate is positive meaning short sellers are paid a periodic fee by long traders. Since price exposure is neutralized, the bot earns low-risk returns from funding payments alone, regardless of market direction.

The bot continuously monitors funding rates across supported exchanges (currently Bybit) and logs opportunities to the terminal when predefined conditions are met.

## How to Run

1. Clone the repository:
   git clone (https://github.com/kiprella/Funding-rate-arbitrage-bot.git)

2. Create a `.env` file in the root folder and add your API keys:
   BYBIT_API_KEY=your_key
   BYBIT_API_SECRET=your_secret

3. Install dependencies:
   pip install -e .

4. Fetch available perpetual tickers:
   python -m src.tickers_info.fetch_tickers from root folder

5. Run the funding data script from the root folder:
   python -m src.data_fetcher.bybit_funding_data from root folder

6. Start monitoring for opportunities:
   python funding_opportunity_monitor.py

## Optional: Run Unit Tests

   python -m unittest discover tests
