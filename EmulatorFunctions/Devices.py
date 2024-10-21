from UtilityFunctions.Error import *
from UtilityFunctions.Utility import *
from Main import Log

import json
import copy
import math

class CodeRunner:
    def __init__(self,Parent,FilePath="Functions.json"):
        self.FunctionMap=json.load(open(FilePath,"r"))
        for X,Y in self.FunctionMap.items():
            Y["Function"]=getattr(self,Y["Function"])
        self.Parent=Parent
        self.Code=self.Parent.Code.split("\n")
        self.Registers={f"r{X}":0 for X in range(0,18)}
        self.RegisterAliases={"sp":"r16","ra":"r17"}
        self.Stack=[0 for X in range(512)]
        self.Constants={}

        self.LineNumber=0
        self.DevicePins=[]

        self.ParseCode()

    def ParseCode(self):
        for X,Y in enumerate(self.Code):
            YTemp=Y.strip()
            if " " not in YTemp:
                if YTemp.endswith(":"):
                    if YTemp not in self.Constants:
                        self.Constants[YTemp[:-1]]=X
                    else:
                        Log.Warning("You cannot declare two lables with the same name",Caller=f"Script line {self.LineNumber}")
                        self.Parent.Fields["Error"].Value=1
                    self.Code[X]=""

    def PrintRegisters(self):
        Output=["\n+------------+-------+\n|Registers   |       |"]
        for X,Y in self.Registers.items():
            Output.append(f"|{X:<12}|{Y:<7}|")
        Log.Info("\n".join(Output)+"\n+------------+-------+") 

    def PrintConstants(self):
        Output=["\n+------------+-------+\n|Constants   |       |"]
        for X,Y in self.Constants.items():
            Output.append(f"|{X:<12}|{Y:<7}|")
        Log.Info("\n".join(Output)+"\n+------------+-------+") 

    def ScriptLength(self):
        return len(self.Script)
    
    def GetArgType(self,Value):
        #Account for indirect aliasing (remember that it can be done multiple times eg rrr1)
        if len(Value) == 0:
            return "None"
        
        if Value in self.Constants:
            return "Constant"

        if Value in self.RegisterAliases:
            return "Register"
        

        if Value[0] == "r" and len(Value) > 1:
            try:
                InValue=int(Value.replace("r",""))
                if InValue >=0 and InValue < 18:
                    return "Register"
            except:
                pass
        
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
            Log.Warning("You cannot change a constant value",Caller=f"Script line {self.LineNumber}")
            self.Parent.Fields["Error"].Value=1
            return None
        
        if Value in self.RegisterAliases:
            return self.RegisterAliases[Value]

        if Value[0] == "r":
            try:
                RegisterIndex=int(Value.replace("r",""))
                for X in range(Value.count("r") - 1):
                    if RegisterIndex >= 0 and RegisterIndex < 18:
                        RegisterIndex=self.Registers[f"r{RegisterIndex}"]
                    else:
                        Log.Warning("Indirect refrences values have to be bettween 0 and 17",Caller=f"Script line {self.LineNumber}")
                        self.Parent.Fields["Error"].Value=1
                        return None
                return f"r{RegisterIndex}"
            except:
                pass
        Log.Warning("Unknown value",Caller=f"Script line {self.LineNumber}")
        self.Parent.Fields["Error"].Value=1
        return None

    def GetArgValue(self,Value):
        #Account for indirect aliasing (remember that it can be done multiple times eg rrr1)
        if Value in self.Constants:
            return self.Constants[Value]
        if Value[0] == "r":
            try:
                RegisterIndex=int(Value.replace("r",""))
                for X in range(Value.count("r") - 1):
                    if RegisterIndex >= 0 and RegisterIndex < 18:
                        RegisterIndex=self.Registers[f"r{RegisterIndex}"]
                    else:
                        Log.Warning("Indirect refrences values have to be bettween 0 and 17",Caller=f"Script line {self.LineNumber}")
                        self.Parent.Fields["Error"].Value=1
                        return None
                return self.Registers[f"r{RegisterIndex}"]
            except:
                pass
        if Value in self.RegisterAliases:
            return self.Registers[self.RegisterAliases[Value]]
        
        if Value.startswith('HASH("') and Value.endswith('")'):
            Value=Value[6:-2]
            return ComputeCRC32(Value)

        try:
            return int(Value)
        except:
            pass
        Log.Warning("Failed to parse arg",Caller=f"Script line {self.LineNumber}")
        self.Parent.Fields["Error"].Value=1
        return None

    def Instruction_Define(self,*args):
        Value=int(args[2])
        if self.Parent.Field["Error"].Value == 1:return
        self.Constants[args[1]]=Value
        if args[1] in self.RegisterAliases:
            del self.RegisterAliases[args[1]]
            #Check wether it should throw an error or not
            
    def Instruction_Move(self,*args):
        Index1=self.GetArgIndex(args[1])
        Value2=self.GetArgValue(args[2])
        if self.Parent.Field["Error"].Value == 1:return
        self.Registers[Index1]=Value2
        
    def Instruction_Alias(self,*args):
        if self.GetArgType(args[1]) == "String":
            if args[2][0] == "r":
                self.RegisterAliases[args[1]]=args[2]
                if args[1] in self.Constants:
                    del self.Constants[args[1]]
                    #Check wether it should throw an error or not
            elif args[2][0] == "d":
                pass #ADD DEVICE SUPPORT
            else:
                Log.Error("Unkown alias type not caught by update")
        else:
            Log.Warning("You cannot set a register alias to a device name or a register",Caller=f"Script line {self.LineNumber}")
            self.Parent.Fields["Error"].Value=1
    def Instruction_Add(self,*args):
        Index1=self.GetArgIndex(args[1])
        Value1=self.GetArgValue(args[2])
        Value2=self.GetArgValue(args[3])
        if self.Parent.Field["Error"].Value == 1:return

        self.Registers[Index1]=Value1 + Value2

    def Instruction_Sub(self,*args):
        Index1=self.GetArgIndex(args[1])
        Value1=self.GetArgValue(args[2])
        Value2=self.GetArgValue(args[3])
        if self.Parent.Field["Error"].Value == 1:return

        self.Registers[Index1]=Value1 - Value2

    def Instruction_Mul(self,*args):
        Index1=self.GetArgIndex(args[1])
        Value1=self.GetArgValue(args[2])
        Value2=self.GetArgValue(args[3])
        if self.Parent.Field["Error"].Value == 1:return

        self.Registers[Index1]=Value1 * Value2

    def Instruction_Div(self,*args):
        Index1=self.GetArgIndex(args[1])
        Value1=self.GetArgValue(args[2])
        Value2=self.GetArgValue(args[3])
        if self.Parent.Field["Error"].Value == 1:return

        self.Registers[Index1]=Value1 / Value2
        
    def Instruction_Abs(self,*args):
        Index1=self.GetArgIndex(args[1])
        Value1=self.GetArgValue(args[2])
        if self.Parent.Field["Error"].Value == 1:return

        self.Registers[Index1]=abs(Value1)
    
    def Instruction_Ceil(self,*args):
        Index1=self.GetArgIndex(args[1])
        Value1=self.GetArgValue(args[2])
        if self.Parent.Field["Error"].Value == 1:return

        self.Registers[Index1]=math.ceil(Value1)

    def Instruction_Floor(self,*args):
        Index1=self.GetArgIndex(args[1])
        Value1=self.GetArgValue(args[2])
        if self.Parent.Field["Error"].Value == 1:return

        self.Registers[Index1]=math.floor(Value1)

    def Instruction_Exp(self,*args):
        Index1=self.GetArgIndex(args[1])
        Value1=self.GetArgValue(args[2])
        Value2=self.GetArgValue(args[3])
        if self.Parent.Field["Error"].Value == 1:return

        self.Registers[Index1]=Value1 ** Value2

    def Instruction_Yield(self,*args):
        return

    def Instruction_Jump(self,*args):
        Line=self.GetArgValue(args[1])
        if self.Parent.Field["Error"].Value == 1:return
        self.LineNumber=Line - 1

    def Instruction_JumpAL(self,*args):
        Line=self.GetArgValue(args[1])
        if self.Parent.Field["Error"].Value == 1:return

        self.Registers[self.RegisterAliases["ra"]]=self.LineNumber + 1
        self.LineNumber=Line - 1

    def Instruction_JumpR(self,*args):
        Line=self.GetArgValue(args[1])
        if self.Parent.Field["Error"].Value == 1:return
        
        self.LineNumber+=Line - 1

    def RunUpdate(self):
        if self.LineNumber >= len(self.Code) or self.Parent.Fields["Error"].Value != 0:
            return
        CurrentLine=self.Code[self.LineNumber].strip()
        if CurrentLine != "":
            CurrentLine=SplitNotStringSpaces(CurrentLine," ")
            if CurrentLine[0] in self.FunctionMap:

                CurrentFunction=self.FunctionMap[CurrentLine[0]]
                if len(CurrentLine) - 1 == len(CurrentFunction["Args"]):
                    
                    for X in range(0,len(CurrentFunction["Args"])):
                        if self.GetArgType(CurrentLine[X+1]) not in CurrentFunction["Args"][X].split("|"):

                            Log.Warning(f"Arg {X+1} of {CurrentLine[0]} must be of type {CurrentFunction['Args'][X]}",Caller=f"Script line {self.LineNumber}")
                            self.Parent.Fields["Error"].Value=1
                            break
                    else:
                        self.FunctionMap[CurrentLine[0]]["Function"](*CurrentLine)
                else:
                    Log.Warning(f"{CurrentLine[0]} requires {len(CurrentFunction['Args'])} args",Caller=f"Script line {self.LineNumber}")
                    self.Parent.Fields["Error"].Value=1
            else:
                Log.Warning(f"Unknown function {CurrentLine[0]}",Caller=f"Script line {self.LineNumber}")
                self.Parent.Fields["Error"].Value=1

        self.LineNumber+=1
        #if self.LineNumber >= len(self.Code):
        #    self.LineNumber=0
class Device:
    def __init__(self,PrefabName:str,PrefabHash:int,DeviceName:str,ReferenceId:int,Fields:dict,Pins:dict,Slots:list,Varibles:dict,RunsCode:bool,StackEnabled:bool,StackLength:int,Code:str):
        self.PrefabName=PrefabName
        self.PrefabHash=PrefabHash
        self.DeviceName=DeviceName
        self.ReferenceId=ReferenceId
        self.Fields=Fields
        self.Pins=Pins
        self.Slots=Slots
        self.Varibles=Varibles
        self.RunsCode=RunsCode
        self.StackEnabled=StackEnabled
        self.StackLength=StackLength
        self.Code=Code
        if RunsCode:
            self.State=CodeRunner(self)
        

class DeviceMaker:
    def __init__(self,DeviceFile:str="EmulatorFunctions/Devices.json"):
        self.Devices=json.loads(open(DeviceFile,"r").read())
    
    def MakeDevice(self,DeviceType:str,ReferenceId:int,DeviceName:str="",**kwargs):
        if DeviceType not in self.Devices:
            raise InvalidDeviceType(DeviceType)
        
        Output=copy.deepcopy(self.Devices[DeviceType])

        Output["Pins"]=[0 for X in range(Output["Pins"]["Number"])]

        PrefabHash=ComputeCRC32(DeviceType)

        for X,Y in kwargs.items():
            if X in Output["Fields"]:
                if type(Y) == int:
                    Output["Fields"][X]["Value"]=Y
                else:
                    raise TypeError
            elif X == "Pins":
                if type(Y) == list:
                    for A,B in enumerate(Y):
                        Output["Pins"][A]=B
                else:
                    raise TypeError
                
            elif X == "Slots":
                pass
                #IMPLEMENT THIS

            elif X in Output["Variables"]:
                Output["Variables"][X]=Y
            
            else:
                raise InvalidDeviceArgument(X)
        
        Output["Fields"]["ReferenceId"]={ "Value": ReferenceId, "Read": True, "Write": False }
        Output["Fields"]["PrefabHash"]={ "Value": PrefabHash, "Read": True, "Write": False }

        for X,Y in Output["Fields"].items():
            Output["Fields"][X]=Field(Y["Value"],Y["Read"],Y["Write"])

        Property=Output["Properties"]

        return Device(DeviceType,PrefabHash,DeviceName,ReferenceId,Output["Fields"],Output["Pins"],Output["Slots"],Output["Variables"],Property["RunCode"],Property["Stack"]["Enabled"],Property["Stack"]["Length"],Output["Variables"]["Code"])
    
    