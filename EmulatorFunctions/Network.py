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
            Device.AddNetworkRef(self)
        else:
            raise RefIdTaken(Device.ReferenceId)
        
    def GetDevice(self,ReferenceId:int):
        if ReferenceId in self.DeviceList:
            return self.DeviceList[ReferenceId]
        else:
            return None

    def RunScripts(self):
        for _,Y in self.DeviceList.items():
            if Y.RunsCode:
                Y.State.RunUpdate()