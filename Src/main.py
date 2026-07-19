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
            # 日付が変わった場合
            if previous.Day != now.Day:
                # 日次バッチ処理を実行したかどうか
                daily_done = False
            elif daily_done = False:
                daily_batch_procedure()
                daily_done = True
                now = datetime.now()
                # 今日の 8:00 を作る
                target = now.replace(hour=8, minute=0, second=0, microsecond=0)
                # もし既に8時を過ぎていたら、翌日の8時にする
                if target <= now:
                    target += timedelta(days=1)
                # 残り秒数を計算
                sleep_seconds = (target - now).total_seconds()             
                # sleep
                time.sleep(sleep_seconds)
            # マーケットクローズ後
            elif now.hour >= MARKET_CLOSE_TIME:
                target = datetime(now.year, now.month, now.day) + timedelta(days=1)
                time.sleep(COLLECT_STOP_TIME)
                # 24時まで待機
                sleep_seconds = (target - now).total_seconds()
                if sleep_seconds > 0:
                    time.sleep(sleep_seconds)
            else:
                target_time = datetime.now() + timedelta(seconds=interval)
                print(f"[{now}] Checking market conditions...")
                market_data = api.get_market_data()
                regular_batch_procedure()
                time.sleep(3)  # ダミー処理
                # 処理が終わったら、target_time まで sleep
                now = datetime.now()
                sleep_seconds = (target_time - now).total_seconds() + 1
                if sleep_seconds > 0:
                    time.sleep(sleep_seconds)
        except Exception as e:
            print("例外が発生しました:", e)
            traceback.print_exc()
            print("10秒後にリトライします...")
            time.sleep(10)

if __name__ == "__main__":
    main()
