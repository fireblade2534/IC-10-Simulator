from UtilityFunctions.Error import *
from UtilityFunctions.Utility import *

class Network:
    def __init__(self,DeviceList:list):
        self.DeviceList={}
        for X in DeviceList:
            self.DeviceList[X.ReferenceId]=X
    
    