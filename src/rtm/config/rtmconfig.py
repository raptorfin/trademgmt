from ConfigParser import SafeConfigParser


class RTMConfig:    
    def __init__(self,ini):
        self.iniFile = ini
        self.parser = SafeConfigParser()

    def __str__(self):
        return "<iniFile=%s, configMap=%s>" % (self.iniFile,RTMConfig.configMap)

    def loadConfig(self):
        _map = {}
        self.parser.read(self.iniFile)
        
        for section in self.parser.sections():
            for name,value in self.parser.items(section):
                try:
                    _map[name] = value
                except:
                    _map[name] = None
        return _map