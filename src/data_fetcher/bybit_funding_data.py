import asyncio
import csv
import os
import sys
from datetime import datetime
from collections import defaultdict


current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.insert(0, root_dir)

from ..engine.trading_engine import TradingEngine
from tabulate import tabulate

def get_current_cycle() -> int:

    filename = get_funding_rates_file()
    if not os.path.exists(filename):
        return 0
    
    try:
        with open(filename, 'r') as csvfile:
            rows = list(csv.reader(csvfile))
            if len(rows) > 1: 
                return int(rows[-1][0])  
    except Exception:
        pass
    return 0

def get_latest_tickers_file() -> str:

    if not os.path.exists('tickers_info'):
        raise FileNotFoundError("No tickers_info directory found.")
    
    files = [f for f in os.listdir('tickers_info') if f.startswith('all_tickers_') and f.endswith('.csv')]
    if not files:
        raise FileNotFoundError("No ticker files found in tickers_info directory.")
    

    latest_file = sorted(files)[-1]
    return os.path.join('tickers_info', latest_file)

def read_bybit_tickers_from_csv(filepath: str) -> list:

    tickers = []
    with open(filepath, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['Exchange'].lower() == 'bybit':
                tickers.append(row['Symbol'])
    return tickers

def get_funding_rates_file() -> str:

    os.makedirs('funding_rates', exist_ok=True)
    return os.path.join('funding_rates', 'bybit_funding_rates.csv')

async def append_funding_rates_to_csv(funding_rates: list):

    filename = get_funding_rates_file()
    file_exists = os.path.exists(filename)
    

    current_cycle = get_current_cycle()
    cycle = current_cycle + 1
    
    with open(filename, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:

            writer.writerow([
                'Cycle',                     
                'Symbol',                    
                'Funding Rate',             
                'Funding Rate Value',        
                'Funding Timestamp',         
                'Fetch Timestamp',           
                'Is Negative',               
                'Absolute Rate',             
                'Hour',                      
                'Day',                       
                'Week',                      
                'Month'                      
            ])
        
        fetch_timestamp = datetime.now()
        for rate in funding_rates:
            symbol, rate_value, funding_timestamp = rate
            funding_dt = datetime.strptime(funding_timestamp, '%Y-%m-%d %H:%M:%S')
            
            is_negative = rate_value < 0
            abs_rate = abs(rate_value)
            
            writer.writerow([
                cycle,                       
                symbol,
                f"{rate_value:.4f}%",
                rate_value,                  
                funding_timestamp,
                fetch_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                is_negative,
                abs_rate,
                funding_dt.hour,
                funding_dt.weekday(),
                funding_dt.isocalendar()[1],  
                funding_dt.month
            ])
    
    print(f"\nFunding rates appended to {filename} (Cycle {cycle})")
    return cycle

async def fetch_with_rate_limit(engine, ticker: str, semaphore: asyncio.Semaphore) -> tuple:
    async with semaphore:  
        try:
            rate_data = await engine.exchange.get_funding_rate(ticker)
            if rate_data['retCode'] == 0 and rate_data['result']['list']:
                latest_rate = rate_data['result']['list'][0]
                return (
                    ticker,
                    float(latest_rate['fundingRate']) * 100,  
                    datetime.fromtimestamp(int(latest_rate['fundingRateTimestamp']) / 1000).strftime('%Y-%m-%d %H:%M:%S')
                )
        except Exception as e:
            print(f"Error fetching funding rate for {ticker}: {str(e)}")
        return None

def group_by_timestamp(funding_rates: list) -> dict:
    grouped = defaultdict(list)
    for rate in funding_rates:
        grouped[rate[2]].append(rate)
    return grouped

async def fetch_and_save_data(engine: TradingEngine, tickers: list):
    semaphore = asyncio.Semaphore(50)
    
    tasks = [fetch_with_rate_limit(engine, ticker, semaphore) for ticker in tickers]
    
    results = await asyncio.gather(*tasks)
    
    funding_rates = [rate for rate in results if rate is not None]
    
    grouped_rates = group_by_timestamp(funding_rates)
    
    current_cycle = get_current_cycle()
    cycle = current_cycle + 1
    
    for timestamp, rates in sorted(grouped_rates.items()):
        rates.sort(key=lambda x: x[1], reverse=True)
        
        table_data = [[rate[0], f"{rate[1]:.4f}%"] for rate in rates]
        
        print(f"\n=== Bybit Funding Rates for {timestamp} (Cycle {cycle}) ===")
        print(tabulate(
            table_data,
            headers=['Symbol', 'Funding Rate'],
            tablefmt='grid'
        ))
        print(f"Total pairs in this interval: {len(rates)}")
    
    await append_funding_rates_to_csv(funding_rates)

async def main():
    engine = None
    try:
        try:
            tickers_file = get_latest_tickers_file()
            print(f"Reading Bybit tickers from: {tickers_file}")
        except FileNotFoundError as e:
            print(f"Error: {str(e)}")
            print("Please run the ticker fetcher script first to generate ticker data.")
            return
        
        tickers = read_bybit_tickers_from_csv(tickers_file)
        print(f"Found {len(tickers)} Bybit tickers to process")
        
        engine = TradingEngine()
        if not await engine.initialize():
            print("Failed to initialize trading engine")
            return
            
        while True:
            print(f"\nFetching funding rates at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            await fetch_and_save_data(engine, tickers)
            
            print("\nWaiting 30 minutes before next fetch...")
            await asyncio.sleep(1800)  
            
    except KeyboardInterrupt:
        print("\nStopping the funding rate fetcher...")
    except Exception as e:
        print(f"Error in main: {str(e)}")
    finally:
        if engine:
            await engine.shutdown()

if __name__ == "__main__":
    asyncio.run(main()) 