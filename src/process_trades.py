import os
import datetime
import logging
import argparse
import decimal

from xml.dom.minidom import parseString

import wrappers.ftp as ftp
import wrappers.mysql as db
from rtm.config.rtmconfig import RTMConfig
from rtm.orderentry import factory
from rtm.orderentry import portfolio
from rtm.orderentry import cache

TWOPLACES = decimal.Decimal(10) ** -2

i_cache = None
t_cache = None
o_cache = None


def main():
    args = init_args()
    config = RTMConfig(args['config'])
    configMap = config.loadConfig()
    configMap['today'] = args['today']
    dbconn = db.init_db(configMap['dbserver'], configMap['dbuser'],
                        configMap['dbpwd'], configMap['dbname'])
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    xml = get_tradeconfirm(configMap)
    orders = get_new_orders(xml)

    if orders:
        init_caches(dbconn)
        cache_open_orders(dbconn)
        create_orders(orders)
        o_cache.process_orders(o_cache.group_orders(), t_cache)
        process_orphans(o_cache.orphans)


def init_caches(dbconn):
    global i_cache
    global t_cache
    global o_cache
    i_cache = cache.InstrumentCache(dbconn)
    t_cache = cache.TradeCache(dbconn)
    o_cache = cache.OrderCache(dbconn)


def cache_open_orders(dbconn):
    for trade in t_cache.cache:
        sql = ('SELECT '
                    'or1.date,or1.brokerOrderId,in1.name,or1.quantity,'
                    'or1.price,or1.commission,or1.openClose,or1.buySell,'
                    'or1.tradeId,or1.id '
                'FROM '
                    'Orders or1 '
                    'JOIN Instruments in1 ON in1.id = or1.instrumentId '
                    'JOIN Trades tr1 ON tr1.id = or1.tradeId '
                'WHERE tr1.id = {}').format(t_cache.cache[trade].id)
        for row in db.db_read(dbconn, sql):
            (date, b_id, i_name, qty, price, comm, o_type, action, tradeId, o_id) = row[:]
            order = portfolio.Order(date, b_id, i_cache.cache[i_name], qty, price, comm, o_type, action, tradeId, o_id)
            o_cache.add_obj(b_id, order)


def init_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--today', help="Today's Date",
                        default=datetime.datetime.now().strftime("%Y%m%d"))
    parser.add_argument('-c', '--config', help="Config filepath",
                        required=True)
    return vars(parser.parse_args())


def get_tradeconfirm(config, debug=False):
    rFile = "%s.%s.%s.%s%s" % (config['acctnum'],
                               config['filename'],
                               config['today'],
                               config['today'],
                               config['filesuffix'])
    lFile = os.path.join(config['localpath'], config['filename'])
    lFile += config['filesuffix']
    if not debug:
        conn = ftp.init_ftp(config['ftphost'],
                            config['ftpuser'],
                            config['ftppwd'])
        ftp.change_dir(conn, config['remotepath'])
        ftp.get_file(conn, lFile, rFile)
        ftp.close_ftp(conn)
    return lFile


def get_new_orders(file_):
    data = []
    with open(file_) as f:
        for line in f:
            data.append(line)
    dom = parseString(''.join(data))
    return dom.getElementsByTagName('TradeConfirm')


def create_orders(data):
    for line in data:
        desc = line.getAttribute('description')
        sym = line.getAttribute('symbol')
        oid = line.getAttribute('orderID')
        cat = line.getAttribute('assetCategory')
        itype = line.getAttribute('putCall')
        qty = int(line.getAttribute('quantity'))
        price = decimal.Decimal(line.getAttribute('price')).quantize(TWOPLACES)
        comm = decimal.Decimal(line.getAttribute('commission')).quantize(TWOPLACES)

        if desc not in i_cache.cache:
            instr = factory.create_instrument(desc, sym, factory.set_instrument_type(cat, itype))
            i_cache.add_obj(instr.name, instr, True)

        if oid in o_cache.cache:
            o_cache.cache[oid].update_quantity(qty)
            o_cache.cache[oid].update_price(price)
            o_cache.cache[oid].update_commission(comm)
        else:
            dateTime = line.getAttribute('dateTime').replace(',','')
            otype = set_type_id(line.getAttribute('code'))
            action = set_action_id(line.getAttribute('buySell'))
            order = portfolio.Order(dateTime,oid,i_cache.cache[desc],qty,price,comm,otype,action)
            o_cache.add_obj(oid, order)


def process_orphans(orders):
    for obj in orders:
        print(obj)


def set_type_id(str_):
    if 'O' in str_:
        return 1
    elif 'C' in str_:
        return 2
    else:
        return -99


def set_action_id(_str):
    if _str == 'BUY':
        return 1
    elif _str == 'SELL':
        return 2
    else:
        return -99


if __name__ == '__main__':
    main()
