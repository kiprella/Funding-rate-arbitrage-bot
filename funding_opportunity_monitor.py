import time
import pandas as pd
import os

CSV_PATH = 'funding_rates/bybit_funding_rates.csv'
CHECK_INTERVAL = 1800  # seconds

def get_latest_cycle(df):
    if df.empty:
        return 0
    return df['Cycle'].max()

def analyze_cycle(df, cycle):
    cycle_df = df[df['Cycle'] == cycle]
    # Only look for positive funding rates (shorts pay longs)
    positive_opps = cycle_df[cycle_df['Is Negative'] == False]
    if not positive_opps.empty:
        print(f"\n=== Positive Funding Arbitrage Opportunities (Cycle {cycle}) ===")
        for _, row in positive_opps.iterrows():
            print(
                f"Symbol: {row['Symbol']}, Funding Rate: {row['Funding Rate']} "
                f"=> Suggestion: SHORT PERP, BUY SPOT (get paid funding)"
            )
    else:
        print(f"\nNo positive funding rates found in cycle {cycle}.")

def main():
    last_cycle = 0
    print("Monitoring for new funding rate cycles...")
    while True:
        if not os.path.exists(CSV_PATH):
            print("Waiting for CSV file to be created...")
            time.sleep(CHECK_INTERVAL)
            continue

        try:
            df = pd.read_csv(CSV_PATH)
        except Exception as e:
            print(f"Error reading CSV: {e}")
            time.sleep(CHECK_INTERVAL)
            continue

        if 'Cycle' not in df.columns or 'Is Negative' not in df.columns:
            print("CSV does not have required columns yet.")
            time.sleep(CHECK_INTERVAL)
            continue

        df['Cycle'] = pd.to_numeric(df['Cycle'], errors='coerce')
        df['Is Negative'] = df['Is Negative'].astype(bool)

        latest_cycle = get_latest_cycle(df)
        if latest_cycle > last_cycle:
            for cycle in range(last_cycle + 1, latest_cycle + 1):
                analyze_cycle(df, cycle)
            last_cycle = latest_cycle

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main() 