from ConfigParser import SafeConfigParser


class BaseConfig:
    def __init__(self, ini):
        self.properties = self.load_inifile(ini)


    def __getitem__(self, key):
        return self.properties[key]


    def add_properties(self, **kwargs):
        self.properties.update(kwargs)


    def load_inifile(self, inifile):
        parser = SafeConfigParser()
        parser.read(inifile)
        optmap = {}

        for section in parser.sections():
            opts = {name: value for name, value in parser.items(section)}
            optmap.update(opts)
        return optmap
