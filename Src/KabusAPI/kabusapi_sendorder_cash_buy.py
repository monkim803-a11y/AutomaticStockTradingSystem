import urllib.request
import json
import pprint

#指値注文情報
class ReverseLimitOrder:
    def __init__(self,
                 TriggerSec=3,
                 TriggerPrice=1600,
                 UnderOver=2,
                 AfterHitOrderType=1,
                 AfterHitPrice=0):
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

#指値買い注文情報
class BuyOrderRequest:
    def __init__(self,
                 Symbol,
                 Exchange,
                 SecurityType,
                 Side,
                 CashMargin,
                 DelivType,
                 FundType,
                 AccountType,
                 Qty,
                 FrontOrderType,
                 Price,
                 ExpireDay,
                 ReverseLimitOrder):

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
        self.ReverseLimitOrder = ReverseLimitOrder or ReverseLimitOrder()
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
	def SendOrder(self):
		json_data = json.dumps(obj).encode('utf-8')

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
