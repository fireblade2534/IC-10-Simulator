from UtilityFunctions.Error import *
from UtilityFunctions.Utility import *
from Main import Log

import json
import copy
import math
import random
import re


epsilon=pow(2,-23)
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

        self.DevicePins=[]

        self.ParseCode()

    def ParseCode(self):
        for X,Y in enumerate(self.Code):
            if "#" in Y:
                Location=Y.find("#")
                self.Code[X]=Y[:Location].strip()
            YTemp=self.Code[X].strip()
            if " " not in YTemp:
                if YTemp.endswith(":"):
                    if YTemp not in self.Constants:
                        self.Constants[YTemp[:-1]]=X
                    else:
                        Log.Warning("You cannot declare two lables with the same name",Caller=f"Script line {self.Parent.Fields['LineNumber'].Value}")
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
            try:
                float(Value)
                return "Number"
            except:
                pass
        
        return "String"

    def GetArgIndex(self,Value):
        #Account for indirect aliasing (remember that it can be done multiple times eg rrr1)
        if Value in self.Constants:
            Log.Warning("You cannot change a constant value",Caller=f"Script line {self.Parent.Fields['LineNumber'].Value} ")
            self.Parent.Fields["Error"].Value=1
            return None
        
        if Value in self.RegisterAliases:
            return self.RegisterAliases[Value]

        if Value[0] == "r":
            try:
                RegisterIndex=int(Value.replace("r",""))
                for X in range(Value.count("r") - 1):
                    if RegisterIndex != "NaN":
                        if RegisterIndex >= 0 and RegisterIndex < 18:
                            RegisterIndex=self.Registers[f"r{RegisterIndex}"]
                        else:
                            Log.Warning("Indirect refrences values have to be bettween 0 and 17",Caller=f"Script line {self.Parent.Fields['LineNumber'].Value}")
                            self.Parent.Fields["Error"].Value=1
                            return None
                    else:
                        Log.Warning("Indirect refrences values have to be bettween 0 and 17 not NaN",Caller=f"Script line {self.Parent.Fields['LineNumber'].Value}")
                        self.Parent.Fields["Error"].Value=1
                        return None
                return f"r{RegisterIndex}"
            except:
                pass
        Log.Warning("Unknown value",Caller=f"Script line {self.Parent.Fields['LineNumber'].Value}")
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
                    if RegisterIndex != "NaN":
                        if RegisterIndex >= 0 and RegisterIndex < 18:
                            RegisterIndex=self.Registers[f"r{RegisterIndex}"]
                        else:
                            Log.Warning("Indirect refrences values have to be bettween 0 and 17",Caller=f"Script line {self.Parent.Fields['LineNumber'].Value}")
                            self.Parent.Fields["Error"].Value=1
                            return None
                    else:
                        Log.Warning("Indirect refrences values have to be bettween 0 and 17 not NaN",Caller=f"Script line {self.Parent.Fields['LineNumber'].Value}")
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
            try:
                return float(Value)
            except:
                pass
        Log.Warning("Failed to parse arg",Caller=f"Script line {self.Parent.Fields['LineNumber'].Value}")
        self.Parent.Fields["Error"].Value=1
        return None

    def Instruction_Define(self,*args):
        Value=int(args[2])
        if args[1] not in self.Constants:
            self.Constants[args[1]]=Value
            if args[1] in self.RegisterAliases:
                del self.RegisterAliases[args[1]]
            #Check wether it should throw an error or not
        else:
            Log.Warning("You cannot change a constant value",Caller=f"Script line {self.Parent.Fields['LineNumber'].Value}")
            if self.Parent.Fields["Error"].Value == 1:return
            
    def Instruction_Move(self,*args):
        Index1=self.GetArgIndex(args[1])
        Value2=self.GetArgValue(args[2])
        if self.Parent.Fields["Error"].Value == 1:return
        self.Registers[Index1]=Value2
        
    def Instruction_Alias(self,*args):
        if self.GetArgType(args[1]) == "String":
            if args[2][0] == "r":
                if args[1] not in self.RegisterAliases:
                    self.RegisterAliases[args[1]]=args[2]
                    if args[1] in self.Constants:
                        del self.Constants[args[1]]
                        #Check wether it should throw an error or not
                else:
                    Log.Warning("Cannot overwrite an alias",Caller=f"Script line {self.Parent.Fields['LineNumber'].Value}")
                    if self.Parent.Fields["Error"].Value == 1:return
            elif args[2][0] == "d":
                pass #ADD DEVICE SUPPORT
            else:
                Log.Error("Unkown alias type not caught by update")
        else:
            Log.Warning("You cannot set a register alias to a device name or a register",Caller=f"Script line {self.Parent.Fields['LineNumber'].Value}")
            self.Parent.Fields["Error"].Value=1
    def Instruction_Add(self,*args):
        Index1=self.GetArgIndex(args[1])
        Value1=self.GetArgValue(args[2])
        Value2=self.GetArgValue(args[3])
        if self.Parent.Fields["Error"].Value == 1:return

        if Value1 == "NaN" or Value2 == "NaN":
            self.Registers[Index1]="NaN"
            return 

        self.Registers[Index1]=Value1 + Value2

    def Instruction_Sub(self,*args):
        Index1=self.GetArgIndex(args[1])
        Value1=self.GetArgValue(args[2])
        Value2=self.GetArgValue(args[3])
        if self.Parent.Fields["Error"].Value == 1:return

        if Value1 == "NaN" or Value2 == "NaN":
            self.Registers[Index1]="NaN"
            return

        self.Registers[Index1]=Value1 - Value2

    def Instruction_Mul(self,*args):
        Index1=self.GetArgIndex(args[1])
        Value1=self.GetArgValue(args[2])
        Value2=self.GetArgValue(args[3])
        if self.Parent.Fields["Error"].Value == 1:return

        if Value1 == "NaN" or Value2 == "NaN":
            self.Registers[Index1]="NaN"
            return

        self.Registers[Index1]=Value1 * Value2

    def Instruction_Div(self,*args):
        Index1=self.GetArgIndex(args[1])
        Value1=self.GetArgValue(args[2])
        Value2=self.GetArgValue(args[3])
        if self.Parent.Fields["Error"].Value == 1:return

        if Value1 == "NaN" or Value2 == "NaN":
            self.Registers[Index1]="NaN"
            return

        self.Registers[Index1]=Value1 / Value2
        
    def Instruction_Abs(self,*args):
        Index1=self.GetArgIndex(args[1])
        Value1=self.GetArgValue(args[2])
        if self.Parent.Fields["Error"].Value == 1:return

        if Value1 == "NaN":
            self.Registers[Index1]="NaN"
            return

        self.Registers[Index1]=abs(Value1)
    
    def Instruction_Ceil(self,*args):
        Index1=self.GetArgIndex(args[1])
        Value1=self.GetArgValue(args[2])
        if self.Parent.Fields["Error"].Value == 1:return

        if Value1 == "NaN":
            self.Registers[Index1]="NaN"
            return

        self.Registers[Index1]=math.ceil(Value1)

    def Instruction_Floor(self,*args):
        Index1=self.GetArgIndex(args[1])
        Value1=self.GetArgValue(args[2])
        if self.Parent.Fields["Error"].Value == 1:return

        if Value1 == "NaN":
            self.Registers[Index1]="NaN"
            return

        self.Registers[Index1]=math.floor(Value1)

    def Instruction_Exp(self,*args):
        Index1=self.GetArgIndex(args[1])
        Value1=self.GetArgValue(args[2])
        if self.Parent.Fields["Error"].Value == 1:return

        if Value1 == "NaN":
            self.Registers[Index1]="NaN"
            return

        self.Registers[Index1]=math.e ** Value1

    def Instruction_Log(self,*args):
        Index1=self.GetArgIndex(args[1])
        Value1=self.GetArgValue(args[2])
        if self.Parent.Fields["Error"].Value == 1:return

        if Value1 == "NaN":
            self.Registers[Index1]="NaN"
            return

        self.Registers[Index1]=math.log(Value1)

    def Instruction_Rand(self,*args):
        Index1=self.GetArgIndex(args[1])
        if self.Parent.Fields["Error"].Value == 1:return

        self.Registers[Index1]=random.random()

    def Instruction_Round(self,*args):
        Index1=self.GetArgIndex(args[1])
        Value1=self.GetArgValue(args[2])
        if self.Parent.Fields["Error"].Value == 1:return

        if Value1 == "NaN":
            self.Registers[Index1]="NaN"
            return
        Decimal=Value1 - math.floor(Value1)
        if Decimal >= 0.5:
            self.Registers[Index1]=math.ceil(Value1)
        else:
            self.Registers[Index1]=math.floor(Value1)

    def Instruction_Yield(self,*args):
        return

    def Instruction_Jump(self,*args):
        Line=self.GetArgValue(args[1])
        if self.Parent.Fields["Error"].Value == 1:return

        if Line == "NaN":
            Log.Warning("You cannot jump to a NaN line",Caller=f"Script line {self.Parent.Fields['LineNumber'].Value}")
            self.Parent.Fields["Error"].Value=1
            return

        self.Parent.Fields['LineNumber'].Value=Line - 1

    def Instruction_JumpAL(self,*args):
        Line=self.GetArgValue(args[1])
        if self.Parent.Fields["Error"].Value == 1:return

        if Line == "NaN":
            Log.Warning("You cannot jump to a NaN line",Caller=f"Script line {self.Parent.Fields['LineNumber'].Value}")
            self.Parent.Fields["Error"].Value=1
            return

        self.Registers[self.RegisterAliases["ra"]]=self.Parent.Fields['LineNumber'].Value + 1
        self.Parent.Fields['LineNumber'].Value=Line - 1

    def Instruction_JumpR(self,*args):
        Line=self.GetArgValue(args[1])
        if self.Parent.Fields["Error"].Value == 1:return
        
        if Line == "NaN":
            Log.Warning("You cannot jump relative to a NaN line",Caller=f"Script line {self.Parent.Fields['LineNumber'].Value}")
            self.Parent.Fields["Error"].Value=1
            return

        NewLineNumber=self.Parent.Fields['LineNumber'].Value + Line - 1
        if NewLineNumber < 0:
            NewLineNumber=self.Parent.Fields['LineNumber'].Value
        if NewLineNumber >= len(self.Code) - 1:
            NewLineNumber=self.Parent.Fields['LineNumber'].Value - 1
        self.Parent.Fields['LineNumber'].Value=NewLineNumber

    def Instruction_Branch(self,*args):
        global epsilon
        #Branch to line if device is not set and other ones like that
        FunctionName=args[0]
        if FunctionName.endswith("al"):
            StoreNextLine=True
            FunctionName=FunctionName[:-2]
        else:
            StoreNextLine=False

        if FunctionName.startswith("br"):
            Relative=True
            FunctionName=FunctionName[2:]
        else:
            Relative=False
            FunctionName=FunctionName[1:]
        
        Values=[self.GetArgValue(X) for X in args[1:]]
        if self.Parent.Fields["Error"].Value == 1:return

        Matched=False
        if FunctionName == "eq":
            JumpLine=Values[2]
            Matched=Values[0] == Values[1]

        elif FunctionName == "eqz":
            JumpLine=Values[1]
            Matched=Values[0] == 0

        elif FunctionName == "ge":
            JumpLine=Values[2]
            Matched=Values[0] >= Values[1]

        elif FunctionName == "gez":
            JumpLine=Values[1]
            Matched=Values[0] >= 0

        elif FunctionName == "gt":
            JumpLine=Values[2]
            Matched=Values[0] > Values[1]

        elif FunctionName == "gtz":
            JumpLine=Values[1]
            Matched=Values[0] > 0

        elif FunctionName == "le":
            JumpLine=Values[2]
            Matched=Values[0] <= Values[1]

        elif FunctionName == "lez":
            JumpLine=Values[1]
            Matched=Values[0] <= 0

        elif FunctionName == "lt":
            JumpLine=Values[2]
            Matched=Values[0] < Values[1]
        
        elif FunctionName == "ltz":
            JumpLine=Values[1]
            Matched=Values[0] >= 0

        elif FunctionName == "ne":
            JumpLine=Values[2]
            Matched=Values[0] != Values[1]
        
        elif FunctionName == "nez":
            JumpLine=Values[1]
            Matched=Values[0] != 0

        elif FunctionName == "nan":
            JumpLine=Values[1]
            Matched=Values[0] == "NaN"

        elif FunctionName == "dns":
            #TODO
            pass
        
        elif FunctionName == "dse":
            #TODO
            pass

        elif FunctionName == "ap":
            JumpLine=Values[3]
            Matched=abs(Values[0] - Values[1]) <= max(Values[2] * max(abs(Values[0]), abs(Values[1])),epsilon * 8)

        elif FunctionName == "apz":
            JumpLine=Values[2]
            Matched=abs(Values[0]) <= max(Values[1] * abs(Values[0]), epsilon * 8)

        elif FunctionName == "na":
            JumpLine=Values[3]
            Matched=abs(Values[0] - Values[1]) > max(Values[2] * max(abs(Values[0]), abs(Values[1])), epsilon * 8)
            

        elif FunctionName == "naz":
            JumpLine=Values[2]
            Matched=abs(Values[0]) > max (Values[1] * abs(Values[0]), epsilon * 8)
        else:
            Log.Warning("Unknown branch type",Caller=f"Script line {self.Parent.Fields['LineNumber'].Value}")
            self.Parent.Fields["Error"].Value=1
            return 
        
        if Matched == True:
            if StoreNextLine == True:
                self.Registers[self.RegisterAliases["ra"]]=self.Parent.Fields['LineNumber'].Value + 1

            if Relative == True:
                self.Parent.Fields['LineNumber'].Value+=JumpLine - 1
            else:
                self.Parent.Fields['LineNumber'].Value=JumpLine - 1

        
        

    def RunUpdate(self):
        if self.Parent.Fields['LineNumber'].Value >= len(self.Code) or self.Parent.Fields["Error"].Value != 0:
            return
        CurrentLine=self.Code[self.Parent.Fields['LineNumber'].Value].strip()
        if CurrentLine != "":
            CurrentLine=SplitNotStringSpaces(CurrentLine," ")
            for CurrentIndex,CurrentFunction in self.FunctionMap.items():
                if CurrentLine[0] in CurrentFunction["Alias"]:
                    if len(CurrentLine) - 1 == CurrentFunction["Alias"][CurrentLine[0]]:
                        
                        for X in range(0,len(CurrentLine) - 1):
                            if self.GetArgType(CurrentLine[X+1]) not in CurrentFunction["Args"][X].split("|"):

                                Log.Warning(f"Arg {X+1} of {CurrentLine[0]} must be of type {CurrentFunction['Args'][X]}",Caller=f"Script line {self.Parent.Fields['LineNumber'].Value}")
                                self.Parent.Fields["Error"].Value=1
                                break
                        else:
                            self.FunctionMap[CurrentIndex]["Function"](*CurrentLine)
                    else:
                        Log.Warning(f"{CurrentLine[0]} requires {CurrentFunction['Alias'][CurrentLine[0]]} args",Caller=f"Script line {self.Parent.Fields['LineNumber'].Value}")
                        self.Parent.Fields["Error"].Value=1
                    break
            else:
                Log.Warning(f"Unknown function {CurrentLine[0]}",Caller=f"Script line {self.Parent.Fields['LineNumber'].Value}")
                self.Parent.Fields["Error"].Value=1

        self.Parent.Fields['LineNumber'].Value+=1
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
    
    