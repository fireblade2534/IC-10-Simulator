from UtilityFunctions.Error import *
from UtilityFunctions.Utility import *

class Network:
    def __init__(self,DeviceList:list=[]):
        self.DeviceList={}
        for X in DeviceList:
            self.DeviceList[X.ReferenceId]=X
        self.NetworkChannels=["NaN" for X in range(0,6)]
    
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

    def GetBatchDevices(self,DeviceHash,DeviceNameHash:int=-1):
        Devices=[]
        for X,Y in self.DeviceList.items():
            if Y.PrefabHash == DeviceHash:
                if Y.DeviceNameHash == DeviceNameHash or DeviceNameHash == -1:
                    Devices.append(self.DeviceList[X])
        return Devices



    def RunScripts(self):
        for _,Y in self.DeviceList.items():
            if Y.RunsCode:
                Y.State.RunUpdate()