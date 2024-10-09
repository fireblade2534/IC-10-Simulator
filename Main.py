import Devices
import json
from Error import *
import Devices
import Logging
#import importlib
class State:
    def __init__(self,RunningDevice:int,Script:str,Devices:dict,**kwargs):
        self.Registers={f"r{X}":0 for X in range(0,18)}
        self.RegisterAliases={"sp":16,"ra":17}
        self.Stack=[0 for X in range(512)]
        self.Constants={}
        self.Devices=Devices

        self.Script=Script
        self.LineNumber=0
        self.RunningDevice=RunningDevice

        self.Log=Logging.Logging(**kwargs)

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
            #make this work later
    
    def GetArgIndex(self,Value):
        if Value in self.Constants:
            return -2
        if Value[0] == "r":
            try:
                Index=int(Value[1:])
                if Index >= 0 and Index <= 17:
                    return Index
            except:
                pass
        if Value in self.RegisterAliases:
            return self.RegisterAliases[Value]
        return -1

    def Instruction_Define(self,**args):
        self.Constants[args[1],args[2]]
    
    def Instruction_Move(self,**args):
        Index1=self.GetArgIndex(args[1])
        Value=0
        if Index1 < 0:
            self.Log.Warning("You can not set a constant" if Index1 == -2 else "You cannot set a ",Caller=f"Script line {self.LineNumber}")
            
    def RunUpdate(self):
        FunctionMap={"define":self.Instruction_Define,"move":self.Instruction_Move}
        
        CurrentLine=self.Script[self.LineNumber].split(" ")
        if CurrentLine[0] in FunctionMap:
            pass
        else:
            self.Log.Warning(f"Unknown function on line",Caller=f"Script line {self.LineNumber}")

        self.LineNumber+=1
        if self.LineNumber > len(self.Script):
            self.LineNumber=0

if __name__ == "__main__":
    DevicesList={69:Devices.StructureCircuitHousing(ReferenceId=69,Pins=Devices.Pins())}
    S=State(69,"stuff",Devices=DevicesList,LogToFile=False,LogConsoleLevel=Logging.DEBUG)
    S.ParseScript()
    S.RunUpdate()
    #open("Test.json","w").write(json.dumps(S.DumpConfigFile(),indent=4))
    #State.ParseConfigFile(json.load(open("Test.json","r")))