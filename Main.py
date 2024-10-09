import Devices
import json
from Error import *
import Devices
#import importlib
class State:
    def __init__(self,RunningDevice:int,Script:str,Devices:dict):
        self.Registers={f"r{X}":0 for X in range(0,18)}
        self.RegisterAliases={"sp":16,"ra":17}
        self.Stack=[0 for X in range(512)]
        self.Constants={}
        self.Devices=Devices

        self.Script=Script
        self.Lines=0

        self.RunningDevice=RunningDevice

    def ParseScript(self):
        self.Script=self.Script.split("\n")


    def DumpConfigFile(self):
        ParsedDevices={}
        for X,Y in self.Devices.items():
            DeviceName,DeviceValue=Y.GetConfig()
            ParsedDevices[X]={"Type":DeviceName,"Args":DeviceValue}
        Output={"Constants":self.Constants,
                "Devices":ParsedDevices,"RunningDevice":self.RunningDevice,"Script":self.Script}
        return Output

    
    @staticmethod
    def ParseConfigFile(Data):
        DevicesList={}
        for X,Y in Data["Devices"].items():
            DeviceClass=getattr(Devices,f'{Y["Type"]}').ParseConfigFile(Y)
            DevicesList.append(DeviceClass)
            print(DeviceClass)
    
    def Instruction_Define(self,**args):
        self.Constants[args[1],args[2]]
    
    def 



if __name__ == "__main__":
    DevicesList={69:Devices.StructureCircuitHousing(ReferenceId=69,Pins=Devices.Pins())}
    S=State(69,"",Devices=DevicesList)
    open("Test.json","w").write(json.dumps(S.DumpConfigFile(),indent=4))
    State.ParseConfigFile(json.load(open("Test.json","r")))