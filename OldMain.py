import EmulatorFunctions.Devices as Devices
import EmulatorFunctions.Network as Network
import json
from UtilityFunctions.Error import *
import UtilityFunctions.Logging as Logging
from UtilityFunctions.Utility import *
import math
#import importlib
class State:
    def __init__(self,RunningDevice:int,Script:str,Network:dict,**kwargs):
        self.Registers={f"r{X}":0 for X in range(0,18)}
        self.RegisterAliases={"sp":"r16","ra":"r17"}
        self.Stack=[0 for X in range(512)]
        self.Constants={}
        self.Devices=Devices

        self.Script=Script
        self.LineNumber=0
        self.RunningDevice=RunningDevice
        self.DevicePins=[]

        self.Log=Logging.Logging(**kwargs)

    def LoadFunctionList(self,FilePath="Functions.json"):
        self.FunctionMap=json.load(open(FilePath,"r"))
        for X,Y in self.FunctionMap.items():
            Y["Function"]=getattr(self,Y["Function"])
        

    def PrintRegisters(self):
        Output=["\n+------------+-------+\n|Registers   |       |"]
        for X,Y in self.Registers.items():
            Output.append(f"|{X:<12}|{Y:<7}|")
        self.Log.Info("\n".join(Output)+"\n+------------+-------+")

    def ParseScript(self):
        self.Script=self.Script.split("\n")
        CurrentDevice=self.Devices[self.RunningDevice]
        #Make it get device pins

    def ScriptLength(self):
        return len(self.Script)

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
            DeviceClass=getattr(DevicesOld,f'{Y["Type"]}').ParseConfigFile(Y)
            #make this work later
    
    def GetArgType(self,Value):
        #Account for indirect aliasing (remember that it can be done multiple times eg rrr1)
        if len(Value) == 0:
            return "None"
        
        if Value in self.Constants:
            return "Constant"

        if Value in self.Registers or Value in self.RegisterAliases:
            return "Register"
        
        if Value.startswith('HASH("') and Value.endswith('")'):
            return "Hash"
        
        try:
            int(Value)
            return "Number"
        except:
            pass
        
        return "String"

    def GetArgIndex(self,Value):
        #Account for indirect aliasing (remember that it can be done multiple times eg rrr1)
        if Value in self.Constants:
            return -1
        if Value[0] == "r":
            if Value in self.Registers:
                return Value
        if Value in self.RegisterAliases:
            return self.RegisterAliases[Value]
        return -1

    def GetArgValue(self,Value):
        #Account for indirect aliasing (remember that it can be done multiple times eg rrr1)
        if Value in self.Constants:
            return self.Constants[Value]
        if Value[0] == "r":
            if Value in self.Registers:
                return self.Registers[Value]
        if Value in self.RegisterAliases:
            return self.Registers[self.RegisterAliases[Value]]
        
        if Value.startswith('HASH("') and Value.endswith('")'):
            Value=Value[6:-2]
            return ComputeCRC32(Value)

        try:
            return int(Value)
        except:
            return None

    def Instruction_Define(self,*args):
        Value=int(args[2])
        self.Constants[args[1]]=Value
        if args[1] in self.RegisterAliases:
            del self.RegisterAliases[args[1]]
    
    def Instruction_Move(self,*args):
        Index1=self.GetArgIndex(args[1])
        Value2=self.GetArgValue(args[2])
        self.Registers[Index1]=Value2
        
    def Instruction_Alias(self,*args):
        if args[2][0] == "r":
            self.RegisterAliases[args[1]]=args[2]
            if args[1] in self.Constants:
                del self.Constants[args[1]]
        elif args[2][0] == "d":
            pass #ADD DEVICE SUPPORT
        else:
            self.Log.Error("Unkown alias type not caught by update")

    def Instruction_Add(self,*args):
        Index1=self.GetArgIndex(args[1])
        Value1=self.GetArgValue(args[2])
        Value2=self.GetArgValue(args[3])
        self.Registers[Index1]=Value1 + Value2

    def Instruction_Sub(self,*args):
        Index1=self.GetArgIndex(args[1])
        Value1=self.GetArgValue(args[2])
        Value2=self.GetArgValue(args[3])
        self.Registers[Index1]=Value1 - Value2

    def Instruction_Mul(self,*args):
        Index1=self.GetArgIndex(args[1])
        Value1=self.GetArgValue(args[2])
        Value2=self.GetArgValue(args[3])
        self.Registers[Index1]=Value1 * Value2

    def Instruction_Div(self,*args):
        Index1=self.GetArgIndex(args[1])
        Value1=self.GetArgValue(args[2])
        Value2=self.GetArgValue(args[3])
        self.Registers[Index1]=Value1 / Value2
        
    def Instruction_Abs(self,*args):
        Index1=self.GetArgIndex(args[1])
        Value1=self.GetArgValue(args[2])
        self.Registers[Index1]=abs(Value1)
    
    def Instruction_Ceil(self,*args):
        Index1=self.GetArgIndex(args[1])
        Value1=self.GetArgValue(args[2])
        self.Registers[Index1]=math.ceil(Value1)

    def Instruction_Floor(self,*args):
        Index1=self.GetArgIndex(args[1])
        Value1=self.GetArgValue(args[2])
        self.Registers[Index1]=math.floor(Value1)

    def Instruction_Exp(self,*args):
        Index1=self.GetArgIndex(args[1])
        Value1=self.GetArgValue(args[2])
        Value2=self.GetArgValue(args[3])
        self.Registers[Index1]=Value1 ** Value2

    def RunUpdate(self):
        CurrentLine=self.Script[self.LineNumber]
        if CurrentLine.strip() != "":
            CurrentLine=SplitNotStringSpaces(CurrentLine," ")
            if CurrentLine[0] in self.FunctionMap:

                CurrentFunction=self.FunctionMap[CurrentLine[0]]
                if len(CurrentLine) - 1 == len(CurrentFunction["Args"]):
                    
                    for X in range(0,len(CurrentFunction["Args"])):
                        if self.GetArgType(CurrentLine[X+1]) not in CurrentFunction["Args"][X].split("|"):

                            self.Log.Warning(f"Arg {X+1} of {CurrentLine[0]} must be of type {CurrentFunction['Args'][X]}",Caller=f"Script line {self.LineNumber}")
                            break
                    else:
                        self.FunctionMap[CurrentLine[0]]["Function"](*CurrentLine)
                else:
                    self.Log.Warning(f"{CurrentLine[0]} requires {len(CurrentFunction['Args'])} args",Caller=f"Script line {self.LineNumber}")
            else:
                self.Log.Warning(f"Unknown function {CurrentLine[0]}",Caller=f"Script line {self.LineNumber}")

        self.LineNumber+=1
        if self.LineNumber > len(self.Script):
            self.LineNumber=0

if __name__ == "__main__":
    Network=Network.Network()
    DeviceMaker=Devices.DeviceMaker()
    Network.AddDevice(DeviceMaker.MakeDevice("StructureCircuitHousing",69,))
    S=State(69,open("Test.ic10","r").read(),Devices=Network,LogToFile=False,LogConsoleLevel=Logging.DEBUG)
    S.ParseScript()
    S.LoadFunctionList()
    for X in range(S.ScriptLength()):
        S.RunUpdate()
    S.PrintRegisters()
    #open("Test.json","w").write(json.dumps(S.DumpConfigFile(),indent=4))
    #State.ParseConfigFile(json.load(open("Test.json","r")))