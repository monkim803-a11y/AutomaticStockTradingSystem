# main.py

import time
import traceback
import yaml
from datetime import datetime

import KabusAPI
from OrderManager import *
from RiskManager import *
from Strategy import *

#市場がクローズする時間
Const MARKET_CLOSE_TIME = 16
#17:00-24:00まで、情報収集ストップ時間（7時間）
Const COLLECT_STOP_TIME = 3600 * 7

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
            previous = now
            now = datetime.now()
            #日付が変わった場合
            if previous.Day != now.Day:
                #日次バッチ処理を実行したかどうか
                daily_done = False
            elif daily_done = False:
                daily_batch_procedure()
                daily_done = True
            #マーケットクローズ後（念のため17時以降）
            elif now.hour > MARKET_CLOSE_TIME:
                #7時間スリープ
                time.sleep(COLLECT_STOP_TIME)
            else:
                print(f"[{now}] Checking market conditions...")
                market_data = api.get_market_data()
                signal = strategy.generate_signal(market_data)
                if signal is not None:
                    print(f"Signal detected: {signal}")
                    trader.execute(signal)
                time.sleep(interval)
        except Exception as e:
            print("例外が発生しました:", e)
            traceback.print_exc()
            print("10秒後にリトライします...")
            time.sleep(10)

if __name__ == "__main__":
    main()
