import EmulatorFunctions.Devices as Devices
import EmulatorFunctions.Network as Network
import json
from UtilityFunctions.Error import *
import UtilityFunctions.Logging as Logging
from UtilityFunctions.Utility import *
import math
class CodeRunner:
    def __init__(self,FilePath="Functions.json"):
        self.FunctionMap=json.load(open(FilePath,"r"))
        for X,Y in self.FunctionMap.items():
            Y["Function"]=getattr(self,Y["Function"])

    def 

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
    MNet.AddDevice(DM.MakeDevice("StructureCircuitHousing",69,Code=open("Test.ic10","r").read()))
    MM=MainManager([MNet])
    MM.RunScripts()