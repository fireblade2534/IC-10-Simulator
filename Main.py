import EmulatorFunctions.Devices as Devices
import EmulatorFunctions.Network as Network
import json
from UtilityFunctions.Error import *
import UtilityFunctions.Logging as Logging
from UtilityFunctions.Utility import *
import math

Log=Logging.Logging(LogToFile=False)
class MainManager:
    def __init__(self,Networks:list[Network.Network]=[]):
        self.Networks=Networks
        self.Log=Logging.Logging(LogToFile=False)
    
    def RunScripts(self):
        for X in self.Networks:
            X.RunScripts()

if __name__ == "__main__":
    MNet=Network.Network()
    DM=Devices.DeviceMaker()
    MNet.AddDevice(DM.MakeDevice("StructureCircuitHousing",69,Code=open("Test.ic10","r").read(),Pins={"d3":65}))
    MNet.AddDevice(DM.MakeDevice("StructureGasMixer",65))
    MM=MainManager([MNet])
    #print(MM.Networks[0].DeviceList[69].State.GetArgType("r16"))
    #exit()
    MM.Networks[0].DeviceList[69].State.PrintConstants()
    for X in range(0,7):
        MM.RunScripts()
        if MM.Networks[0].DeviceList[69].Fields["Error"].Value == 1:
            continue
        MM.Networks[0].DeviceList[69].State.PrintRegisters()
    MM.Networks[0].DeviceList[69].State.PrintStack()
    MM.Networks[0].DeviceList[69].State.PrintAlias()
    MM.Networks[0].DeviceList[69].PrintFields()