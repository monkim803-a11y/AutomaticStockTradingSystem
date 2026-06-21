# main.py

import time
import traceback
import yaml
from datetime import datetime

import KabusAPI
from OrderManager import *
from RiskManager import *
from Strategy import *


def load_config(path="config.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    print("=== Auto Trading System Started ===")

    # --- Config 読み込み ---
    config = load_config()

    # --- API クライアント ---
    api = KabuClient(
        host=config["api"]["host"],
        api_key=config["api"]["api_key"]
    )

    # --- 戦略 ---
    strategy = Strategy(config["strategy"])

    # --- リスク管理 ---
    risk = RiskManager(config["risk"]["max_loss_rate"])

    # --- トレーダー ---
    trader = Trader(api_client=api, risk_manager=risk)

    interval = config["system"]["interval_seconds"]

    # --- メインループ ---
    while True:
        try:
            now = datetime.now()
            print(f"[{now}] Checking market conditions...")

            market_data = api.get_market_data()
            signal = strategy.generate_signal(market_data)

            if signal is not None:
                print(f"Signal detected: {signal}")
                trader.execute(signal)

            time.sleep(interval)

        except Exception as e:
            print("Error occurred:", e)
            traceback.print_exc()
            print("Retrying in 10 seconds...")
            time.sleep(10)


if __name__ == "__main__":
    main()
