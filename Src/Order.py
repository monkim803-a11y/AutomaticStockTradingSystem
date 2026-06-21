#注文クラス
class Order:
    def __init__(self,
                 order_id, #注文ID
                 signal_id, #シグナルID
                 symbol_id, #
                 created_at, #
                 side, #売買（1：売り、2:買い）
                 price, #価格
                 quantity, #数量
                 stasus, #ステータス（未約定・約定完了）
                ):
          
	
	# 注文文字列化
    def to_dict(self):
        return {
            "TriggerSec": self.TriggerSec,
            "TriggerPrice": self.TriggerPrice,
            "UnderOver": self.UnderOver,
            "AfterHitOrderType": self.AfterHitOrderType,
            "AfterHitPrice": self.AfterHitPrice
        }
