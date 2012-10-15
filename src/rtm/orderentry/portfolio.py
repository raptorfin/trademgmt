import rtm.orderentry.mappings as mappings


class Trade:    
    def __init__(self, name, type_, status, id_='NULL', open_=[], close=[]):
        self.id = id_
        self.name = name
        self.type = type_
        self.open_orders = open_
        self.close_orders = close
        self.status = status


    def append_open_orders(self, orders):
        self.open_orders.extend(orders)
        [o.set_trade_id(self.id) for o in self.open_orders if o.tradeId == 'NULL']


    def append_close_orders(self, orders):
        self.close_orders.extend(orders)
        [o.set_trade_id(self.id) for o in self.close_orders]


    def close_trade(self):
        o_qty = self.sum_values('quantity', self.open_orders)
        c_qty = self.sum_values('quantity', self.close_orders)
        if o_qty == c_qty:
            self.status = mappings.CLOSED_TRADE_ID
            return True
        else:
            return False


    def sum_values(self, value, item):
        return sum([[].append(q.value) for q in item])


class Order:
    def __init__(self,date,bOrderId,instr,quantity,price,commission,oType,oAction,oTradeId='NULL',id_='NULL'):
        self.id = id_
        self.instr = instr
        self.quantity = quantity
        self.date = date
        self.brokerOrderId = bOrderId
        self.prices = [price]
        self.commission = commission
        self.type = oType
        self.action = oAction
        self.tradeId = oTradeId
        
    def __str__(self):
        return "<id=%s, instr=%s, date=%s, brokerOrderId=%s, price=%s, commission=%s, type=%s, action=%s, tradeId=%s>" % (self.id,self.instr,self.date,self.brokerOrderId,self.prices,self.commission,self.type,self.action,self.tradeId)

    def update_order_id(self,_id):
        self._id = _id


    def set_trade_id(self, id_):
        if self.tradeId == 'NULL':
            self.tradeId = id_


    def update_quantity(self,quantity):
        self.quantity += quantity
     
    def update_price(self,price):
        self.prices.append(price)

    def update_commission(self,commission):
        self.commission += commission
 
    def get_avg_price(self):
        if len(self.prices) > 1:
            return sum(self.prices) / len(self.prices)
        else:
            return self.prices[0]
