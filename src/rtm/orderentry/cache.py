
import logging
from collections import defaultdict

import wrappers.mysql as tmdb
import rtm.orderentry as oe
import rtm.orderentry.mappings as mappings


class BaseCache():
    def __init__(self, dbconn):
        self.dbconn = dbconn
        self.cache = self.load_cache()
        self.updates = []
        self.inserts = []


    def add_obj(self, key, val, persist=False):
        self.cache[key] = val
        logging.info("Added <key=%s, val=%s> to cache", key, val)
        if persist:
            self.insert_obj(val)


    def load_cache(self):
        pass

    
    def insert_obj(self, obj):
        pass


    def update_obj(self, obj):
        pass


class TradeCache(BaseCache):
    def load_cache(self):
        sql = ('SELECT id,name,tradeTypeId,statusTypeId from Trades '
               'WHERE statusTypeId = {}').format(mappings.OPEN_TRADE_ID)
        cache = {}
        for row in tmdb.db_read(self.dbconn, sql):
            (t_id,name,type_id,status_id) = row[:]
            trade = oe.portfolio.Trade(name, type_id, status_id, t_id)
            cache[trade.name] = trade
        return cache


    def insert_obj(self, trade):
        sql = ('INSERT INTO Trades VALUES '
               '({0},"{1}",{2},{3})').format(trade.id,
                                             trade.name,
                                             trade.type,
                                             trade.status)
        trade.id = tmdb.db_modify(self.dbconn, sql)
        logging.info("Inserted %s to Trades", trade)


    def process_open_trade(self, name, action, orders):
        trade = self.get_trade(name, action, mappings.OPEN_TRADE_ID)
        trade.append_open_orders(orders)


    def process_close_trade(self, name, close, open_=None):
        trade = self.get_trade(name, open_.action, mappings.CLOSED_TRADE_ID)
        trade.append_close_orders([close])
        if open_:
            trade.append_open_orders([open_])
        self.close_trade(trade.id)


    def get_trade(self, name, type_=None, status=None):
        if self.cache.get(name):
            trade = self.cache.get(name)
        else:
            trade = oe.portfolio.Trade(name, type_, status)
            self.add_obj(name, trade, True)
        return trade


    def close_trade(self, id_):
        sql = ('UPDATE Trades set statusTypeId = {0} '
               'WHERE id = {1}').format(mappings.CLOSED_TRADE_ID, id_)
        ins = tmdb.db_modify(self.dbconn, sql)
        logging.info("Closed tradeId=%s", id_)
        return ins


class OrderCache(BaseCache):
    def __init__(self, dbconn):
        self.orphans = []
        BaseCache.__init__(self, dbconn)


    def load_cache(self):
        return {}


    def insert_obj(self, order):
        sql = ('INSERT INTO Orders VALUES '
               '({0},"{1}",{2},{3},{4},{5},'
               '{6},{7},{8},{9})').format(order.id, order.date,
                                          order.brokerOrderId,
                                          order.instr.id, order.quantity,
                                          order.get_avg_price(),
                                          order.commission, order.type,
                                          order.action, order.tradeId)
        order.id = tmdb.db_modify(self.dbconn, sql)
        logging.info("Inserted %s to Orders", order)


    def group_orders(self):
        grouped = defaultdict(lambda : defaultdict(list))
        for obj in self.cache:
            i_key = self.cache[obj].instr.name
            t_key = self.cache[obj].type
            grouped[i_key][t_key].append(self.cache[obj])
        return grouped


    def process_orders(self, orders, t_cache):
        for instr in orders:
            o_orders = orders[instr][mappings.OPEN_TRADE_ID]
            c_orders = orders[instr][mappings.CLOSED_TRADE_ID]

            if len(c_orders) == 0:
                t_cache.process_open_trade(instr, o_orders[0].action, o_orders)
                [self.insert_obj(o) for o in o_orders if o.id == 'NULL']
            elif self.quantities_are_equal(o_orders, c_orders):
                t_cache.process_close_trade(instr, c_orders[0], o_orders[0])
                allorders = o_orders + c_orders
                [self.insert_obj(o) for o in allorders if o.id == 'NULL']
            else:
                self.orphans.extend(o_orders + c_orders)


    def quantities_are_equal(self, open_, close):
        o_qty = []
        c_qty = []
        [o_qty.append(o.quantity) for o in open_]
        [c_qty.append(c.quantity) for c in close]
        return (sum(o_qty) + sum(c_qty) == 0)


class InstrumentCache(BaseCache):
    def load_cache(self):
        sql = "SELECT id,name,symbol,instrumentTypeId FROM Instruments"
        cache = {}
        for row in tmdb.db_read(self.dbconn, sql):
            (_id, name, symbol, typeId) = row[:]
            instr = oe.factory.create_instrument(name, symbol, typeId, _id)
            cache[instr.name] = instr
        return cache


    def insert_obj(self, instr):
        sql = ('INSERT INTO Instruments VALUES '
               '({0},"{1}","{2}",{3})').format(instr.id,
                                          instr.name,
                                          instr.sym,
                                          instr.type)
        instr.id = tmdb.db_modify(self.dbconn, sql)
        logging.info("Inserted %s to Instruments", instr)
