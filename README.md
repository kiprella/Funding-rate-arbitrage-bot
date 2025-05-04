# Funding-rate-arbitrage-bot

Funding rate arbitrage bot is an automated trading system that exploits arbitrage opportunities between the spot and perpetual futures markets on cryptocurrency exchanges. The strategy involves entering a delta-neutral position by buying the asset on the spot market while simultaneously shorting the same asset on the perpetual futures market using the same position size. 
This strategy becomes profitable when the funding rate on perpetual futures is negative, meaning that traders holding short positions (anticipating a price drop) are paid a periodic funding fee by those holding long positions (expecting a price increase). Since the price risk is offset by the spot position, the bot earns a low risk return solely from the funding payments, regardless of market direction, since we are projecting two scenarios at the same time – that price will either go up or down. 
The bot continuously scans funding rates across supported crypto exchanges and prints out a message to the terminal automatically when predefined conditions are met.


How to run the program
•	Git clone https://github.com/kiprella/Kairos_Arbitrage_Bot
•	Create .env file and paste BYBIT_API_KEY and BYBIT_API_SECRET in root folder
•	In root folder run “pip install -r requirements.txt”
•	cd tickers_info and run fetch_tickers.py to fetch available perpetual tickers which will be saved in tickers_info folder
•	run x_funding_data.py from root foler (for now only bybit available)
•	in root folder run funding_opportunity _monitor.py and check terminal for available trades
•	[OPTIONAL] to run tests: “python -m unittest discover tests”
