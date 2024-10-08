class BadConfigType(Exception):
    '''Raise when a config value is not a known type'''
    def __init__(self, Type, payload=None):
        self.message = f"The config file cannot save type {type(Type).__name__}"
    def __str__(self):
        return str(self.message)