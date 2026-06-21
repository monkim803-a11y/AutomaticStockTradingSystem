import urllib.request
import json
import pprint

#指値注文情報
class ReverseLimitOrder:
    def __init__(self,
                 TriggerSec,
                 TriggerPrice,
                 UnderOver,
                 AfterHitOrderType,
                 AfterHitPrice):
        self.TriggerSec = TriggerSec
        self.TriggerPrice = TriggerPrice
        self.UnderOver = UnderOver
        self.AfterHitOrderType = AfterHitOrderType
        self.AfterHitPrice = AfterHitPrice
	
	# 注文文字列化
    def to_dict(self):
        return {
            "TriggerSec": self.TriggerSec,
            "TriggerPrice": self.TriggerPrice,
            "UnderOver": self.UnderOver,
            "AfterHitOrderType": self.AfterHitOrderType,
            "AfterHitPrice": self.AfterHitPrice
        }

#買い注文情報
class BuyOrderRequest:
    def __init__(self,
                 Symbol,
                 Exchange,
                 SecurityType = 1,
                 Side = 2,
                 CashMargin = 1,
                 DelivType = 2,
                 FundType = "AA",
                 AccountType = 4,
                 Qty,
                 FrontOrderType,
                 Price,
                 ExpireDay,
                 ReverseLimitOrder):

        self.Symbol = Symbol #銘柄コード
        self.Exchange = Exchange #市場コード
        self.SecurityType = SecurityType #市場タイプ（=1（株式））
        self.Side = Side #売買区分（=2（買））
        self.CashMargin = CashMargin #信用区分（=1（現物））
        self.DelivType = DelivType #受渡区分
        self.FundType = FundType #資産区分（預り区分）（="AA"（信用代用））
        self.AccountType = AccountType #口座種別（=4（特定））
        self.Qty = Qty #数量
        self.FrontOrderType = FrontOrderType #執行条件
        self.Price = Price #注文価格
        self.ExpireDay = ExpireDay #注文有効期限
        self.ReverseLimitOrder = ReverseLimitOrder or ReverseLimitOrder() #逆指値条件
	# 注文文字列化
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
            "ReverseLimitOrder": self.ReverseLimitOrder.to_dict()
        }
	# 注文送信
	def Send(self):
		json_data = json.dumps(self.to_dict()).encode('utf-8')

		url = 'http://localhost:18080/kabusapi/sendorder'
		req = urllib.request.Request(url, json_data, method='POST')
		req.add_header('Content-Type', 'application/json')
		req.add_header('X-API-KEY', 'ed94b0d34f9441c3931621e55230e402')

		try:
			with urllib.request.urlopen(req) as res:
       			print(res.status, res.reason)
      		  	for header in res.getheaders():
     		    	print(header)
				print()
		        content = json.loads(res.read())
		        pprint.pprint(content)
			except urllib.error.HTTPError as e:
    			print(e)
    			content = json.loads(e.read())
    			pprint.pprint(content)
			except Exception as e:
    			print(e)
