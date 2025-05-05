import asyncio
import csv
import os
from datetime import datetime
from ..engine.trading_engine import TradingEngine
from tabulate import tabulate

async def save_tickers_to_csv(tickers: list, exchange: str):
    """Save tickers to a single CSV file with timestamp in the tickers_info folder"""
    # Create tickers_info directory if it doesn't exist
    os.makedirs('tickers_info', exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = os.path.join('tickers_info', f"all_tickers_{timestamp}.csv")
    
    # Check if file exists to determine if we need to write headers
    file_exists = os.path.exists(filename)
    
    with open(filename, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write headers only if file is new
        if not file_exists:
            writer.writerow(['Exchange', 'Symbol', 'Timestamp'])
        
        # Write tickers with current timestamp
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for ticker in tickers:
            writer.writerow([exchange, ticker, current_time])
    
    print(f"\nTickers saved to {filename}")

def get_exchange_choice() -> str:
    """Get exchange choice from user"""
    while True:
        print("\nAvailable exchanges:")
        print("1. Bybit")
        # Add more exchanges here as they become available
        # print("2. Binance")
        # print("3. OKX")
        
        choice = input("\nSelect exchange (1): ").strip()
        if choice == "1":
            return "bybit"
        print("Invalid choice. Please try again.")

def filter_perpetual_pairs(tickers: list) -> list:
    """Filter tickers to only include standard USDT perpetual pairs"""
    filtered_tickers = []
    for ticker in tickers:
        # Only include pairs that:
        # 1. End with USDT
        # 2. Don't contain any special characters or dates
        # 3. Are not PERP pairs
        if (ticker.endswith('USDT') and 
            '-' not in ticker and 
            'PERP' not in ticker):
            filtered_tickers.append(ticker)
    return filtered_tickers

async def main():
    # Get exchange choice
    exchange = get_exchange_choice()
    
    engine = TradingEngine()
    try:
        if await engine.initialize():
            # Get all perpetual tickers
            tickers = await engine.exchange.get_perpetual_tickers()
            
            # Filter tickers to only include standard USDT perpetual pairs
            tickers = filter_perpetual_pairs(tickers)
            
            # Sort tickers alphabetically
            tickers.sort()
            
            # Prepare data for tabulate
            table_data = [[ticker] for ticker in tickers]
            
            # Print the table
            print(f"\n=== Available Standard USDT Perpetual Pairs on {exchange.upper()} ===")
            print(tabulate(
                table_data,
                headers=['Symbol'],
                tablefmt='grid'
            ))
            
            print(f"\nTotal number of standard USDT perpetual pairs: {len(tickers)}")
            
            # Save tickers to CSV
            await save_tickers_to_csv(tickers, exchange)

    except Exception as e:
        print(f"Error in main: {str(e)}")
    finally:
        await engine.shutdown()

if __name__ == "__main__":
    asyncio.run(main()) 