import EmulatorFunctions.Devices as Devices
import EmulatorFunctions.Network as Network
import json
from UtilityFunctions.Error import *
import UtilityFunctions.Logging as Logging
from UtilityFunctions.Utility import *
import math

class MainManager:
    def __init__(self,Networks:list[Network.Network]=[]):
        self.Networks=Networks
    
    def RunScripts(self):
        pass

if __name__ == "__main__":
    MNet=Network.Network()
    DM=Devices.DeviceMaker()
    MNet.AddDevice(DM.MakeDevice("StructureCircuitHousing",69))
    MM=MainManager()