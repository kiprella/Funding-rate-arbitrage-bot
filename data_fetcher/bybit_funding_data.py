import asyncio
import csv
import os
import sys
from datetime import datetime
from collections import defaultdict

# Add the root directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.insert(0, root_dir)

from src.engine.trading_engine import TradingEngine
from tabulate import tabulate

def get_current_cycle() -> int:
    """Get the current cycle number from the last row of the CSV file"""
    filename = get_funding_rates_file()
    if not os.path.exists(filename):
        return 0
    
    try:
        with open(filename, 'r') as csvfile:
            # Read all rows and get the last one
            rows = list(csv.reader(csvfile))
            if len(rows) > 1:  # If file has data (header + at least one row)
                return int(rows[-1][0])  # First column is cycle number
    except Exception:
        pass
    return 0

def get_latest_tickers_file() -> str:
    """Get the most recent all_tickers CSV file from tickers_info directory"""
    if not os.path.exists('tickers_info'):
        raise FileNotFoundError("No tickers_info directory found.")
    
    files = [f for f in os.listdir('tickers_info') if f.startswith('all_tickers_') and f.endswith('.csv')]
    if not files:
        raise FileNotFoundError("No ticker files found in tickers_info directory.")
    
    # Sort by timestamp in filename and get the latest
    latest_file = sorted(files)[-1]
    return os.path.join('tickers_info', latest_file)

def read_bybit_tickers_from_csv(filepath: str) -> list:
    """Read Bybit tickers from CSV file"""
    tickers = []
    with open(filepath, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['Exchange'].lower() == 'bybit':
                tickers.append(row['Symbol'])
    return tickers

def get_funding_rates_file() -> str:
    """Get or create the funding rates file"""
    os.makedirs('funding_rates', exist_ok=True)
    return os.path.join('funding_rates', 'bybit_funding_rates.csv')

async def append_funding_rates_to_csv(funding_rates: list):
    """Append funding rates to the CSV file with optimized structure for analysis"""
    filename = get_funding_rates_file()
    file_exists = os.path.exists(filename)
    
    # Get current cycle and increment it
    current_cycle = get_current_cycle()
    cycle = current_cycle + 1
    
    with open(filename, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            # Optimized headers for analysis
            writer.writerow([
                'Cycle',                     # Fetch cycle number
                'Symbol',                    # Trading pair
                'Funding Rate',              # Raw funding rate (percentage)
                'Funding Rate Value',        # Actual decimal value for calculations
                'Funding Timestamp',         # When the funding rate was recorded
                'Fetch Timestamp',           # When we fetched the data
                'Is Negative',               # Boolean flag for negative rates
                'Absolute Rate',             # Absolute value of the rate
                'Hour',                      # Hour of the funding rate (0-23)
                'Day',                       # Day of the week (0-6)
                'Week',                      # Week number
                'Month'                      # Month number
            ])
        
        fetch_timestamp = datetime.now()
        for rate in funding_rates:
            symbol, rate_value, funding_timestamp = rate
            funding_dt = datetime.strptime(funding_timestamp, '%Y-%m-%d %H:%M:%S')
            
            # Calculate additional fields for analysis
            is_negative = rate_value < 0
            abs_rate = abs(rate_value)
            
            writer.writerow([
                cycle,                       # Add cycle number
                symbol,
                f"{rate_value:.4f}%",
                rate_value,                  # Raw value for calculations
                funding_timestamp,
                fetch_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                is_negative,
                abs_rate,
                funding_dt.hour,
                funding_dt.weekday(),
                funding_dt.isocalendar()[1],  # Week number
                funding_dt.month
            ])
    
    print(f"\nFunding rates appended to {filename} (Cycle {cycle})")
    return cycle

async def fetch_with_rate_limit(engine, ticker: str, semaphore: asyncio.Semaphore) -> tuple:
    """Fetch funding rate with rate limiting"""
    async with semaphore:  # This ensures we don't exceed 50 requests per second
        try:
            rate_data = await engine.exchange.get_funding_rate(ticker)
            if rate_data['retCode'] == 0 and rate_data['result']['list']:
                latest_rate = rate_data['result']['list'][0]
                return (
                    ticker,
                    float(latest_rate['fundingRate']) * 100,  # Convert to percentage
                    datetime.fromtimestamp(int(latest_rate['fundingRateTimestamp']) / 1000).strftime('%Y-%m-%d %H:%M:%S')
                )
        except Exception as e:
            print(f"Error fetching funding rate for {ticker}: {str(e)}")
        return None

def group_by_timestamp(funding_rates: list) -> dict:
    """Group funding rates by their timestamp"""
    grouped = defaultdict(list)
    for rate in funding_rates:
        grouped[rate[2]].append(rate)
    return grouped

async def fetch_and_save_data(engine: TradingEngine, tickers: list):
    """Fetch and save funding rate data"""
    # Create a semaphore to limit to 50 concurrent requests
    semaphore = asyncio.Semaphore(50)
    
    # Create tasks for all tickers
    tasks = [fetch_with_rate_limit(engine, ticker, semaphore) for ticker in tickers]
    
    # Wait for all tasks to complete
    results = await asyncio.gather(*tasks)
    
    # Filter out None results
    funding_rates = [rate for rate in results if rate is not None]
    
    # Group rates by timestamp
    grouped_rates = group_by_timestamp(funding_rates)
    
    # Get current cycle before printing
    current_cycle = get_current_cycle()
    cycle = current_cycle + 1
    
    # Print rates for each timestamp group
    for timestamp, rates in sorted(grouped_rates.items()):
        # Sort rates within each group by funding rate (highest to lowest)
        rates.sort(key=lambda x: x[1], reverse=True)
        
        # Prepare data for tabulate
        table_data = [[rate[0], f"{rate[1]:.4f}%"] for rate in rates]
        
        # Print the table
        print(f"\n=== Bybit Funding Rates for {timestamp} (Cycle {cycle}) ===")
        print(tabulate(
            table_data,
            headers=['Symbol', 'Funding Rate'],
            tablefmt='grid'
        ))
        print(f"Total pairs in this interval: {len(rates)}")
    
    # Append all rates to CSV
    await append_funding_rates_to_csv(funding_rates)

async def main():
    try:
        # Get the latest tickers file
        tickers_file = get_latest_tickers_file()
        print(f"Reading Bybit tickers from: {tickers_file}")
        
        # Read Bybit tickers from CSV
        tickers = read_bybit_tickers_from_csv(tickers_file)
        print(f"Found {len(tickers)} Bybit tickers to process")
        
        # Initialize trading engine
        engine = TradingEngine()
        if await engine.initialize():
            while True:
                print(f"\nFetching funding rates at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                await fetch_and_save_data(engine, tickers)
                
                # Wait for 30 minutes before next fetch
                print("\nWaiting 30 minutes before next fetch...")
                await asyncio.sleep(1800)  # 1800 seconds = 30 minutes
            
    except KeyboardInterrupt:
        print("\nStopping the funding rate fetcher...")
    except Exception as e:
        print(f"Error in main: {str(e)}")
    finally:
        await engine.shutdown()

if __name__ == "__main__":
    asyncio.run(main()) 