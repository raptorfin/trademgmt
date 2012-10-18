import os
import sys
import datetime
import logging
import argparse
import decimal

from xml.dom.minidom import parseString

import wrappers.ftp as ftp
import wrappers.mysql as db
import rtm.config.baseconfig as rtmconfig
from rtm.orderentry import factory
from rtm.orderentry import portfolio
from rtm.orderentry import cache

TWOPLACES = decimal.Decimal(10) ** -2

i_cache = None
t_cache = None
o_cache = None


def main():
    config = init()
    updates = get_new_orders(get_tradeconfirm(config))

    if updates:
        init_caches(config)
        cache_open_orders()
        create_new_orders(updates)
        o_cache.process_orders(o_cache.group_orders(), t_cache)
        process_orphans(o_cache.orphans)
    else:
        logging.info("No new trades for today")


def init():
    args = process_args()
    cfg = rtmconfig.BaseConfig(args['ini'])
    cfg.add_properties(today=args['today'], loglevel=args['loglevel'])
    log = (os.path.join(cfg['ldir'], cfg['lname']), cfg['today'], 'log')
    init_log(cfg['loglevel'], '.'.join(log))
    return cfg


def process_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--today', help="Today's Date",
                        default=datetime.datetime.now().strftime("%Y%m%d"))
    parser.add_argument('-c', '--ini', help="Config filepath",
                        default='/Users/Dan/git/trademgmt/rtm.ini')
    parser.add_argument('-l', '--loglevel', help="log verbosity",
                        default='INFO')
    return vars(parser.parse_args())


def init_log(lvl, log):
    vlevel = getattr(logging, lvl.upper(), None)
    if not isinstance(vlevel, int):
        raise ValueError('Invalid log level: %s' % vlevel)
    logging.basicConfig(level=vlevel,
                        format='%(asctime)s|%(name)s|%(levelname)s|%(message)s',
                        filename=log,
                        filemode='w')
    con = logging.StreamHandler()
    con.setLevel(logging.INFO)
    logging.getLogger('').addHandler(con)


def get_tradeconfirm(cfg):
    r_file = (cfg['acctnum'], cfg['name'], cfg['today'],
              cfg['today'], cfg['suffix'])
    r_file = '.'.join(r_file)
    l_file = (os.path.join(cfg['lpath'], cfg['name']), cfg['suffix'])
    l_file = '.'.join(l_file)
    conn = ftp.init_ftp(cfg['ftphost'], cfg['ftpuser'], cfg['ftppwd'])
    ftp.change_dir(conn, cfg['rpath'])
    got_file = ftp.get_file(conn, l_file, r_file)
    ftp.close_ftp(conn)
    if got_file:
        return l_file
    else:
        logging.info("%s not found. Exiting", r_file)
        sys.exit(0)


def get_new_orders(file_):
    data = []
    with open(file_) as f:
        [data.append(line) for line in f]
    dom = parseString(''.join(data))
    return dom.getElementsByTagName('TradeConfirm')


def init_caches(config):
    dbconn = db.init_db(config['dbserver'],
                        config['dbuser'],
                        config['dbpwd'],
                        config['dbname'])
    global i_cache
    global t_cache
    global o_cache
    i_cache = cache.InstrumentCache(dbconn)
    t_cache = cache.TradeCache(dbconn)
    o_cache = cache.OrderCache(dbconn)


def cache_open_orders():
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
        for row in db.db_read(t_cache.dbconn, sql):
            (date, b_id, i_name, qty, price, comm, o_type, action, tradeId, o_id) = row[:]
            order = portfolio.Order(date, b_id, i_cache.cache[i_name], qty, price, comm, o_type, action, tradeId, o_id)
            o_cache.add_obj(b_id, order)  


def create_new_orders(data):
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
