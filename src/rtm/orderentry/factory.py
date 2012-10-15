import logging

import rtm.orderentry.instruments as instr

# InstrumentTypeIDs
CALL_OPTION_ID = 1
PUT_OPTION_ID = 2
STOCK_ID = 4


def create_instrument(name, symbol, type_, id_='NULL'):
    if type_ == CALL_OPTION_ID:
        return instr.Call(name, symbol, CALL_OPTION_ID, id_)
    elif type_ == PUT_OPTION_ID:
        return instr.Put(name, symbol, PUT_OPTION_ID, id_)
    elif type_ == STOCK_ID:
        return instr.Stock(name, symbol, STOCK_ID, id_)
    else:
        logging.critical("Unsupported Instrument Type: <name=%s, symbol=%s, type=%s, id=%s", name, symbol, type_, id)


def set_instrument_type(aCategory,aType):
    if aCategory == "OPT":
        if aType == "P":
            return PUT_OPTION_ID
        elif aType == "C":
            return CALL_OPTION_ID
        else:
            logging.error("Unknown option type: %s", aType)
    elif aCategory == "STK":
        return STOCK_ID
    else:
        logging.error("Unknown assetType: %s", aCategory)


if __name__ == '__main__':
    pass
