from UtilityFunctions.Error import *
from UtilityFunctions.Utility import *

class Network:
    def __init__(self,DeviceList:list=[]):
        self.DeviceList={}
        for X in DeviceList:
            self.DeviceList[X.ReferenceId]=X
    
    def AddDevice(self,Device):
        if Device.ReferenceId not in self.DeviceList:
            self.DeviceList[Device.ReferenceId]=Device
        else:
            raise RefIdTaken(Device.ReferenceId)
        
    def RunScripts(self):
        for _,Y in self.DeviceList.items():
            if Y.RunsCode:
                Y.State.RunUpdate()