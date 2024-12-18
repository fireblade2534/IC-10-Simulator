class BadConfigType(Exception):
    '''Raise when a config value is not a known type'''
    def __init__(self, Type, payload=None):
        self.message = f"The config file cannot save type {type(Type).__name__}"
    def __str__(self):
        return str(self.message)
    
class InvalidDeviceType(Exception):
    '''Raise when a device type is requested to be created but is not in the Configs/Devices.json file'''
    def __init__(self, Type, payload=None):
        self.message = f"Unkown device type: {Type}"
    def __str__(self):
        return str(self.message)
    
class InvalidDeviceArgument(Exception):
    '''Raise when a device property is asigned but it does not exist in the Configs/Devices.json file'''
    def __init__(self, Type, payload=None):
        self.message = f"Unkown device argument: {Type}"
    def __str__(self):
        return str(self.message)
    
class RefIdTaken(Exception):
    '''Raise when a device trys to register on a network that already has that ref Id'''
    def __init__(self, ID, payload=None):
        self.message = f"Ref Id {ID} is already in use"
    def __str__(self):
        return str(self.message)