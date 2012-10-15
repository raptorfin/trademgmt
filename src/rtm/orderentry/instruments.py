

class Instrument:
    def __init__(self, name, symbol, type_, multiplier, id_='NULL'):
        self.id = id_
        self.name = name
        self.sym = symbol
        self.mult = multiplier
        self.type = type_

    def __str__(self):
        return "<id=%s, name=%s, sym=%s, type=%s, mult=%s>" % (self.id,
                                                               self.name,
                                                               self.sym,
                                                               self.type,
                                                               self.mult)


class Stock(Instrument):
    def __init__(self, name, symbol, instrTypeId, id_='NULL'):
        self.multiplier = 1
        self.abbr = ''
        self.i_type = 'STK'
        Instrument.__init__(self, name, symbol, instrTypeId,
                            self.multiplier, id_)


class Option(Instrument):
    def __init__(self, name, symbol, type_, id_='NULL'):
        self.multiplier = 100
        self.i_type = 'OPT'
        Instrument.__init__(self, name, symbol, type_, self.multiplier, id_)


class Put(Option):
    def __init__(self, name, symbol, instrTypeId, id_='NULL'):
        self.abbr = 'P'
        Option.__init__(self, name, symbol, instrTypeId, id_)


class Call(Option):
    def __init__(self, name, symbol, instrTypeId, id_='NULL'):
        self.abbr = 'C'
        Option.__init__(self, name, symbol, instrTypeId, id_)
