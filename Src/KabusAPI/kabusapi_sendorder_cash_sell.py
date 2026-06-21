import urllib.request
import json
import pprint

class ReverseLimitOrder:
    def __init__(self,
                 TriggerSec=1,
                 TriggerPrice=2600,
                 UnderOver=1,
                 AfterHitOrderType=1,
                 AfterHitPrice=0):
        self.TriggerSec = TriggerSec
        self.TriggerPrice = TriggerPrice
        self.UnderOver = UnderOver
        self.AfterHitOrderType = AfterHitOrderType
        self.AfterHitPrice = AfterHitPrice

    def to_dict(self):
        return {
            "TriggerSec": self.TriggerSec,
            "TriggerPrice": self.TriggerPrice,
            "UnderOver": self.UnderOver,
            "AfterHitOrderType": self.AfterHitOrderType,
            "AfterHitPrice": self.AfterHitPrice
        }
class SellOrderRequest:
    def __init__(self,
                 Symbol, #銘柄コード
                 Exchange=1, #市場コード
                 SecurityType=1, #商品種別（=1（株式））
                 Side="1", #売買区分（=1（売））
                 CashMargin=1, #信用区分（=1（現物））
                 DelivType=0, #受渡区分（=0（指定なし））
                 FundType="  ", #資産区分（="  "（現物売は固定））
                 AccountType=4, #口座種別（=4（特定））
                 Qty, #数量
                 FrontOrderType, #執行条件
                 Price, #注文価格
                 ExpireDay=0, #注文有効期限
                 ReverseLimitOrder #逆指値情報
                ):

        # --- メイン注文パラメータ ---
        self.Symbol = Symbol
        self.Exchange = Exchange
        self.SecurityType = SecurityType
        self.Side = Side
        self.CashMargin = CashMargin
        self.DelivType = DelivType
        self.FundType = FundType
        self.AccountType = AccountType
        self.Qty = Qty
        self.FrontOrderType = FrontOrderType
        self.Price = Price
        self.ExpireDay = ExpireDay

        # --- 逆指値 ---
        self.ReverseLimitOrder = ReverseLimitOrder

    # JSON 変換
    def to_dict(self):
        return {
            "Symbol": self.Symbol,
            "Exchange": self.Exchange,
            "SecurityType": self.SecurityType,
            "Side": self.Side,
            "CashMargin": self.CashMargin,
            "DelivType": self.DelivType,
            "FundType": self.FundType,
            "AccountType": self.AccountType,
            "Qty": self.Qty,
            "FrontOrderType": self.FrontOrderType,
            "Price": self.Price,
            "ExpireDay": self.ExpireDay,
            "ReverseLimitOrder": {
                "TriggerSec": self.ReverseLimitOrder.TriggerSec,
                "TriggerPrice": self.ReverseLimitOrder.TriggerPrice,
                "UnderOver": self.ReverseLimitOrder.UnderOver,
                "AfterHitOrderType": self.ReverseLimitOrder.AfterHitOrderType,
                "AfterHitPrice": self.ReverseLimitOrder.AfterHitPrice
            }
        }

    # --- 注文送信メソッド ---
    def send(self, api_key, url="http://localhost:18080/kabusapi/sendorder"):
        json_data = json.dumps(self.to_dict()).encode("utf-8")

        req = urllib.request.Request(url, json_data, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("X-API-KEY", api_key)

        try:
            with urllib.request.urlopen(req) as res:
                content = json.loads(res.read())
                return {"status": res.status, "response": content}

        except urllib.error.HTTPError as e:
            content = json.loads(e.read())
            return {"status": e.code, "response": content}

        except Exception as e:
            return {"status": "error", "response": str(e)}
