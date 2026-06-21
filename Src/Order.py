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
			self.order_id = order_id
			self.signal_id = signal_id
			self.symbol_id = symbol_id
			self.created_at = created_at
			self.side = side
			self.price = price
			self.quantity = quantity
			self.status = status
