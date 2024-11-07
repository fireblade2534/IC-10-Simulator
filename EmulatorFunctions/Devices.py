from ast import Dict
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
    def __init__(self,Parent,FilePath="Functions.json",DeviceFile:str="EmulatorFunctions/Devices.json"):
        self.DevicesList=json.loads(open(DeviceFile,"r").read())

        self.FunctionMap=json.load(open(FilePath,"r"))
        for X,Y in self.FunctionMap["SpecialTypes"].items():
            Y["ConfirmFunction"]=getattr(self,Y["ConfirmFunction"])
            Y["GetArgFunction"]=getattr(self,Y["GetArgFunction"])

        for X,Y in self.FunctionMap["Functions"].items():
            Y["Function"]=getattr(self,Y["Function"])
        self.Parent=Parent
        self.Code=self.Parent.Code.split("\n")
        self.Registers={f"r{X}":0 for X in range(0,18)}
        self.RegisterAliases={"sp":"r16","ra":"r17"}

        self.PinAliases={}

        if self.Parent.StackEnabled == True:
            self.Stack=[0 for X in range(self.Parent.StackLength)]
        self.Constants={}       

        self.ParseCode()

        self.HighestSP=0

    def ParseCode(self):
        self.LogicTypesList=set()
        for X,Y in self.DevicesList.items():
            for A,B in Y["Fields"].items():
                if B["Read"] or B["Write"]:
                    self.LogicTypesList.add(A)

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

    def PrintAlias(self):
        Output=["\n+------------+-------+\n|Aliases     |       |"]
        for X,Y in self.RegisterAliases.items():
            Output.append(f"|{X:<12}|{Y:<7}|")

        for X,Y in self.PinAliases.items():
            Output.append(f"|{X:<12}|{Y:<7}|")

        Log.Info("\n".join(Output)+"\n+------------+-------+") 


    def PrintStack(self):
        Output=["\n+------------+-------+\n|Stack       |       |"]
        for X in range(self.HighestSP+1):
            Output.append(f"|{X:<12}|{self.Stack[X]:<7}|")
        Log.Info("\n".join(Output)+"\n+------------+-------+") 

    def ScriptLength(self):
        return len(self.Script)
    
    def Special_LogicTypes(self,Value,BaseType):
        return Value in self.LogicTypesList
    def Special_Get_LogicType(self,Value):
        return Value

    def Special_BatchMode(self,Value,BaseType):
        BatchList=["Average","Sum","Minimum","Maximum"]
        if BaseType == "String":
            return Value in BatchList
        return True
    def Special_Get_BatchMode(self,Value):
        BatchList={"Average":0,"Sum":1,"Minimum":2,"Maximum":3}
        if type(Value) == str:
            if str(Value) in BatchList:
                return BatchList[Value]
        RawValue= self.GetArgValue(Value)
        if RawValue >= 0 and RawValue < 4:
            return RawValue
        else:
            Log.Warning("Batch mode value must bettween greater then or euqal too 0 and less then 4",Caller=f"Script line {self.Parent.Fields['LineNumber'].Value} ")
            self.Parent.Fields["Error"].Value=1
            return None


    def Special_DeviceHash(self,Value,BaseType):
        return True
    def Special_Get_DeviceHash(self,Value):
        return Value
    
    def Special_NameHash(self,Value,BaseType):
        return True
    def Special_Get_NameHash(self,Value):
        return Value

    def GetArgBaseType(self,Value,TargetTypes=[]):
        #Account for indirect aliasing (remember that it can be done multiple times eg rrr1)
        if len(Value) == 0:
            return "None"
        
        if Value in self.Constants and "Constant" in TargetTypes:
            return "Constant"

        if Value in self.RegisterAliases and "Register" in TargetTypes:
            return "Register"
        
        if Value in self.PinAliases and "Device" in TargetTypes:
            return "Device"

        if Value[0] == "d" and len(Value) > 1 and "Device" in TargetTypes:
            if "r" in Value:
                try:
                    InValue=int(Value[1:].replace("r",""))
                    if InValue >=0 and InValue < 18:
                        return "Device"
                except:
                    pass
            else:
                try:
                    DeviceNumberList=([str(X) for X in range(self.Parent.PinsNumber)] + ["b"])
                    #print(DeviceNumberList)
                    if Value[1:] in DeviceNumberList:
                        return "Device"
                except:
                    pass

        if Value[0] == "r" and len(Value) > 1 and "Register" in TargetTypes:
            try:
                InValue=int(Value.replace("r",""))
                if InValue >=0 and InValue < 18:
                    return "Register"
            except:
                pass
        
        if Value.startswith('HASH("') and Value.endswith('")') and "Hash" in TargetTypes:
            return "Hash"
        
        if "Number" in TargetTypes:
            if Value[0] == "$":
                try:
                    int(Value[1:],16)
                    return "Number"
                except:
                    pass

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

    def GetArgType(self,Value,TargetTypes=[]):
        IsSpecialType= TargetTypes[0] in self.FunctionMap["SpecialTypes"]
        if IsSpecialType:
            SpecialType=TargetTypes[0]
            TargetTypes=self.FunctionMap["SpecialTypes"][SpecialType]["Types"].split("|")
        BaseType=self.GetArgBaseType(Value,TargetTypes)
        if IsSpecialType:
            if BaseType in TargetTypes:
                Confirmed=self.FunctionMap["SpecialTypes"][SpecialType]["ConfirmFunction"](Value,BaseType)
                if Confirmed:
                    return SpecialType
                else:
                    return "None"
        return BaseType

    def GetArgIndex(self,Value):
        #Account for indirect aliasing (remember that it can be done multiple times eg rrr1)
        if Value in self.Constants:
            Log.Warning("You cannot change a constant value",Caller=f"Script line {self.Parent.Fields['LineNumber'].Value} ")
            self.Parent.Fields["Error"].Value=1
            return None
        
        if Value in self.RegisterAliases:
            return self.GetArgIndex(self.RegisterAliases[Value])

        if Value in self.PinAliases:
            return self.GetArgIndex(self.PinAliases[Value])

        if Value[0] == "d":
            if "r" in Value:
                try:
                    TempValue=Value[1:]
                    RegisterIndex=int(TempValue.replace("r",""))
                    for X in range(TempValue.count("r")):
                        if RegisterIndex != "NaN":
                            if RegisterIndex >= 0 and RegisterIndex < 18:
                                RegisterIndex=self.Registers[f"r{RegisterIndex}"]
                            else:
                                Log.Warning("Indirect device values have to be bettween 0 and 17",Caller=f"Script line {self.Parent.Fields['LineNumber'].Value}")
                                self.Parent.Fields["Error"].Value=1
                                return None
                        else:
                            Log.Warning("Indirect device values have to be bettween 0 and 17 not NaN",Caller=f"Script line {self.Parent.Fields['LineNumber'].Value}")
                            self.Parent.Fields["Error"].Value=1
                            return None
                    RegisterIndex=f"d{RegisterIndex}"
                    if RegisterIndex in self.Parent.Pins:
                        return RegisterIndex
                    Log.Warning("Indirect device values have to be bettween 0 and 5",Caller=f"Script line {self.Parent.Fields['LineNumber'].Value}")
                    self.Parent.Fields["Error"].Value=1
                    return None
                except:
                    pass
            else:
                if Value[0] == "d" and Value[1:] in ([str(X) for X in range(self.Parent.PinsNumber)] + ["b"]):
                    return Value

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

    def GetArgValue(self,Value,TargetType=[]):
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
            return self.GetArgValue(self.RegisterAliases[Value])
        
        if Value[0] == "$":
            try:
                return int(Value[1:],16)
            except:
                pass

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
        return str(Value)
        #Log.Warning("Failed to parse arg",Caller=f"Script line {self.Parent.Fields['LineNumber'].Value}")
        #self.Parent.Fields["Error"].Value=1
        #return None

    def GetSpecialArgValue(self,Value,Type):
        if Type in self.FunctionMap["SpecialTypes"]:
            ProcessedValue=self.GetArgValue(Value,Type)

            if self.Parent.Fields["Error"].Value == 1:return
            return self.FunctionMap["SpecialTypes"][Type]["GetArgFunction"](ProcessedValue) 
        else:
            Log.Warning(f"Invalid special arg type",Caller=f"Script line {self.Parent.Fields['LineNumber'].Value}")
            self.Parent.Fields["Error"].Value=1
            


    def GetDeviceObject(self,RefID:int,DoError:bool=True):
        if self.Parent.Fields["Error"].Value == 1:return
        RefObject=self.Parent.Network.GetDevice(RefID)
        if RefObject != None:
            return RefObject
        else:
            if DoError:
                Log.Warning(f"Unknown device at reference id {RefID}",Caller=f"Script line {self.Parent.Fields['LineNumber'].Value}")
                self.Parent.Fields["Error"].Value=1
            else:
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
        if self.GetArgType(args[1],["String"]) == "String":
            if args[1] not in self.Constants and args[1] not in self.Parent.Pins and args[1] not in self.Registers:
                if args[1] in self.RegisterAliases:
                    del self.RegisterAliases[args[1]]
                if args[1] in self.PinAliases:
                    del self.PinAliases[args[1]]

                if args[2][0] == "r":
                    self.RegisterAliases[args[1]]=args[2]
                elif args[2][0] == "d":
                    self.PinAliases[args[1]]=args[2]
                else:
                    Log.Error("Unkown alias type not caught by update")
            else:
                Log.Warning("Cannot overwrite a constant/builtin register/builtin device index",Caller=f"Script line {self.Parent.Fields['LineNumber'].Value}")
                if self.Parent.Fields["Error"].Value == 1:return
            
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

    def Instruction_Sqrt(self,*args):
        Index1=self.GetArgIndex(args[1])
        Value1=self.GetArgValue(args[2])
        if self.Parent.Fields["Error"].Value == 1:return

        if Value1 == "NaN":
            self.Registers[Index1]="NaN"
            return
        self.Registers[Index1]=math.sqrt(Value1)

    def Instruction_Trunc(self,*args):
        Index1=self.GetArgIndex(args[1])
        Value1=self.GetArgValue(args[2])
        if self.Parent.Fields["Error"].Value == 1:return

        if Value1 == "NaN":
            self.Registers[Index1]="NaN"
            return
        self.Registers[Index1]=math.trunc(Value1)

    def Instruction_Asin(self,*args):
        Index1=self.GetArgIndex(args[1])
        Value1=self.GetArgValue(args[2])
        if self.Parent.Fields["Error"].Value == 1:return

        if Value1 == "NaN":
            self.Registers[Index1]="NaN"
            return
        try:
            self.Registers[Index1]=math.asin(Value1)
        except:
            self.Registers[Index1]="NaN"

    def Instruction_Acos(self,*args):
        Index1=self.GetArgIndex(args[1])
        Value1=self.GetArgValue(args[2])
        if self.Parent.Fields["Error"].Value == 1:return

        if Value1 == "NaN":
            self.Registers[Index1]="NaN"
            return
        try:
            self.Registers[Index1]=math.acos(Value1)
        except:
            self.Registers[Index1]="NaN"

    def Instruction_Atan(self,*args):
        Index1=self.GetArgIndex(args[1])
        Value1=self.GetArgValue(args[2])
        if self.Parent.Fields["Error"].Value == 1:return

        if Value1 == "NaN":
            self.Registers[Index1]="NaN"
            return
        try:
            self.Registers[Index1]=math.atan(Value1)
        except:
            self.Registers[Index1]="NaN"

    def Instruction_Atan2(self,*args):
        Index1=self.GetArgIndex(args[1])
        Value1=self.GetArgValue(args[2])
        Value2=self.GetArgValue(args[3])
        if self.Parent.Fields["Error"].Value == 1:return

        if Value1 == "NaN":
            self.Registers[Index1]="NaN"
            return
        try:
            self.Registers[Index1]=math.atan2(Value1,Value2)
        except:
            self.Registers[Index1]="NaN"

    def Instruction_Sin(self,*args):
        Index1=self.GetArgIndex(args[1])
        Value1=self.GetArgValue(args[2])
        if self.Parent.Fields["Error"].Value == 1:return

        if Value1 == "NaN":
            self.Registers[Index1]="NaN"
            return
        try:
            self.Registers[Index1]=math.sin(Value1)
        except:
            self.Registers[Index1]="NaN"

    def Instruction_Cos(self,*args):
        Index1=self.GetArgIndex(args[1])
        Value1=self.GetArgValue(args[2])
        if self.Parent.Fields["Error"].Value == 1:return

        if Value1 == "NaN":
            self.Registers[Index1]="NaN"
            return
        try:
            self.Registers[Index1]=math.cos(Value1)
        except:
            self.Registers[Index1]="NaN"

    def Instruction_Tan(self,*args):
        Index1=self.GetArgIndex(args[1])
        Value1=self.GetArgValue(args[2])
        if self.Parent.Fields["Error"].Value == 1:return

        if Value1 == "NaN":
            self.Registers[Index1]="NaN"
            return
        try:
            self.Registers[Index1]=math.tan(Value1)
        except:
            self.Registers[Index1]="NaN"

    def Instruction_Peek(self,*args):
        Index1=self.Registers[self.RegisterAliases["sp"]]
        Index2=self.GetArgIndex(args[1])
        if self.Parent.Fields["Error"].Value == 1:return

        if Index1 == "NaN":
            Log.Warning("Cannot peek at NaN index",Caller=f"Script line {self.Parent.Fields['LineNumber'].Value}")
            self.Parent.Fields["Error"].Value=1
            return

        if Index1 >= 1 and Index1 <= self.Parent.StackLength:
            self.Registers[Index2]=self.Stack[Index1 - 1]
        else:
            Log.Warning(f"Peek index must be greater then 0 and less then or equal to {self.Parent.StackLength}",Caller=f"Script line {self.Parent.Fields['LineNumber'].Value}")
            self.Parent.Fields["Error"].Value=1

    def Instruction_Push(self,*args):
        Index1=self.Registers[self.RegisterAliases["sp"]]
        Value1=self.GetArgValue(args[1])
        if self.Parent.Fields["Error"].Value == 1:return

        if Index1 == "NaN":
            Log.Warning("Cannot push at NaN index",Caller=f"Script line {self.Parent.Fields['LineNumber'].Value}")
            self.Parent.Fields["Error"].Value=1
            return

        if Index1 >= 0 and Index1 < self.Parent.StackLength:
            self.Stack[Index1]=Value1
            self.Registers[self.RegisterAliases["sp"]]+=1
        else:
            Log.Warning(f"Push index must be greater then or euqal to 0 and less then {self.Parent.StackLength}",Caller=f"Script line {self.Parent.Fields['LineNumber'].Value}")
            self.Parent.Fields["Error"].Value=1

    def Instruction_Pop(self,*args):
        Index1=self.Registers[self.RegisterAliases["sp"]]
        Index2=self.GetArgIndex(args[1])
        if self.Parent.Fields["Error"].Value == 1:return

        if Index1 == "NaN":
            Log.Warning("Cannot pop at NaN index",Caller=f"Script line {self.Parent.Fields['LineNumber'].Value}")
            self.Parent.Fields["Error"].Value=1
            return

        if Index1 > 0 and Index1 <= self.Parent.StackLength:
            self.Registers[Index2]=self.Stack[Index1 - 1]
            self.Registers[self.RegisterAliases["sp"]]-=1
        else:
            Log.Warning(f"Pop index must be greater then 0 and less then or equal to {self.Parent.StackLength}",Caller=f"Script line {self.Parent.Fields['LineNumber'].Value}")
            self.Parent.Fields["Error"].Value=1

    def Instruction_Get(self,*args):
        Index1=self.GetArgIndex(args[1])
        Index2=self.GetArgIndex(args[2]) 
        Index3=self.GetArgValue(args[3])
        if self.Parent.Fields["Error"].Value == 1:return

        if Index2 in self.Parent.Pins:
            DeviceObject=self.GetDeviceObject(self.Parent.Pins[Index2])
        else:
            Log.Warning(f"No device at {Index2}",Caller=f"Script line {self.Parent.Fields['LineNumber'].Value}")
            self.Parent.Fields["Error"].Value=1
            return

        if DeviceObject.StackEnabled == False:
            Log.Warning(f"Device does not have a stack",Caller=f"Script line {self.Parent.Fields['LineNumber'].Value}")
            self.Parent.Fields["Error"].Value=1
            return

        if Index3 == "NaN":
            Log.Warning("Cannot get at NaN index",Caller=f"Script line {self.Parent.Fields['LineNumber'].Value}")
            self.Parent.Fields["Error"].Value=1
            return

        if Index3 >= 1 and Index3 <= DeviceObject.StackLength:
            self.Registers[Index1]=self.Stack[Index3 - 1]
            Log.Warning(f"Needs further testing",Caller=f"Script line {self.Parent.Fields['LineNumber'].Value}")
        else:
            Log.Warning(f"Get must be greater then 0 and less then or equal to {DeviceObject.StackLength}",Caller=f"Script line {self.Parent.Fields['LineNumber'].Value}")
            self.Parent.Fields["Error"].Value=1

    def Instruction_GetD(self,*args):
        pass
        #TODO

    def Instruction_Poke(self,*args):
        Value1=self.GetArgValue(args[1])
        Value2=self.GetArgValue(args[2])
        if self.Parent.Fields["Error"].Value == 1:return

        if Value1 == "NaN":
            Log.Warning("Cannot poke at NaN index",Caller=f"Script line {self.Parent.Fields['LineNumber'].Value}")
            self.Parent.Fields["Error"].Value=1
            return

        if Value1 >= 0 and Value1 < self.Parent.StackLength:
            self.Stack[Value1]=Value2
        else:
            Log.Warning(f"Pop index must be greater then or equal to 0 and less then {self.Parent.StackLength}",Caller=f"Script line {self.Parent.Fields['LineNumber'].Value}")
            self.Parent.Fields["Error"].Value=1

    def Instruction_Load(self,*args):
        Index1=self.GetArgIndex(args[1])
        Index2=self.GetArgIndex(args[2])
        Value1=self.GetSpecialArgValue(args[3],"LogicType")
        if self.Parent.Fields["Error"].Value == 1:return


        if Index2 in self.Parent.Pins:
            DeviceObject=self.GetDeviceObject(self.Parent.Pins[Index2])
        else:
            Log.Warning(f"No device at {Index2}",Caller=f"Script line {self.Parent.Fields['LineNumber'].Value}")
            self.Parent.Fields["Error"].Value=1
            return
        
        if self.Parent.Fields["Error"].Value == 1:return

        FieldValue=DeviceObject.GetFieldValue(Value1)
        if FieldValue[0] == None:
            Log.Warning(FieldValue[1],Caller=f"Script line {self.Parent.Fields['LineNumber'].Value}")
            self.Parent.Fields["Error"].Value=1
            return None
        #print(Index1,Index2)
        self.Registers[Index1]=FieldValue[0]

    def ApplyBatchOperation(self,Values,BatchMode:int):
        if BatchMode == 0:
            return sum(Values) / len(Values)
        elif BatchMode == 1:
            return sum(Values)
        elif BatchMode == 2:
            return min(Values)
        elif BatchMode == 3:
            return max(Values)
        return "NaN"

    def CollectDevicesValueBatch(self,Devices,Value,BatchMode):
        NoDevicesResponse=["NaN",0,0,float('-inf')]
        
        Values=[]
        for X in Devices:
            FieldValue=X.GetFieldValue(Value)
            if FieldValue[0] != None:
                Values.append(FieldValue[0])

        if len(Values) == 0:
            return NoDevicesResponse[BatchMode]
        return MakeIntIfClose(self.ApplyBatchOperation(Values,BatchMode))

    def Instruction_LoadBatch(self,*args):
        Index1=self.GetArgIndex(args[1])
        Value1=self.GetSpecialArgValue(args[2],"DeviceHash")
        Value2=self.GetSpecialArgValue(args[3],"LogicType")
        Value3=self.GetSpecialArgValue(args[4],"BatchMode")
        if self.Parent.Fields["Error"].Value == 1:return

        Devices=self.Parent.Network.GetBatchDevices(Value1)
        Result=self.CollectDevicesValueBatch(Devices,Value2,Value3)
        self.Registers[Index1]=Result


    def Instruction_LoadBatchNamed(self,*args):
        Index1=self.GetArgIndex(args[1])
        Value1=self.GetSpecialArgValue(args[2],"DeviceHash")
        Value2=self.GetSpecialArgValue(args[3],"NameHash")
        Value3=self.GetSpecialArgValue(args[4],"LogicType")
        Value4=self.GetSpecialArgValue(args[5],"BatchMode")
        if self.Parent.Fields["Error"].Value == 1:return

        Devices=self.Parent.Network.GetBatchDevices(Value1,Value2)
        Result=self.CollectDevicesValueBatch(Devices,Value3,Value4)
        self.Registers[Index1]=Result

    def Instruction_Set(self,*args):
        Index1=self.GetArgIndex(args[1])
        Value1=self.GetSpecialArgValue(args[2],"LogicType")
        Value2=self.GetArgValue(args[3])
        if self.Parent.Fields["Error"].Value == 1:return

        if Index1 in self.Parent.Pins:
            DeviceObject=self.GetDeviceObject(self.Parent.Pins[Index1])
        else:
            Log.Warning(f"No device at {Index1}",Caller=f"Script line {self.Parent.Fields['LineNumber'].Value}")
            self.Parent.Fields["Error"].Value=1
            return
        
        if self.Parent.Fields["Error"].Value == 1:return

        Result=DeviceObject.SetFieldValue(Value1,Value2)   
        if Result[0] == None:
            Log.Warning(Result[1],Caller=f"Script line {self.Parent.Fields['LineNumber'].Value}")
            self.Parent.Fields["Error"].Value=1

    def Instruction_SetBatch(self,*args):
        Value1=self.GetSpecialArgValue(args[1],"DeviceHash")
        Value2=self.GetSpecialArgValue(args[2],"LogicType")
        Value3=self.GetArgValue(args[3])
        if self.Parent.Fields["Error"].Value == 1:return

        Devices=self.Parent.Network.GetBatchDevices(Value1)
        for X in Devices:
            X.SetFieldValue(Value2,Value3)


    def Instruction_SetBatchNamed(self,*args):
        Value1=self.GetSpecialArgValue(args[1],"DeviceHash")
        Value2=self.GetSpecialArgValue(args[2],"NameHash")
        Value3=self.GetSpecialArgValue(args[3],"LogicType")
        Value4=self.GetArgValue(args[4])
        if self.Parent.Fields["Error"].Value == 1:return

        Devices=self.Parent.Network.GetBatchDevices(Value1,Value2)
        for X in Devices:
            X.SetFieldValue(Value3,Value4)

    def Instruction_Yield(self,*args):
        return
    
    def Instruction_Hcf(self,*args):
        Log.Warning("Hcf triggered",Caller=f"Script line {self.Parent.Fields['LineNumber'].Value}")
        self.Parent.Fields["Error"].Value=1
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

    def GetBranchRoot(self,FunctionName):
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
        return FunctionName,StoreNextLine,Relative

    def Instruction_Branch(self,*args):
        global epsilon
        #Branch to line if device is not set and other ones like that
        FunctionName,StoreNextLine,Relative=self.GetBranchRoot(args[0])
        
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

    def Instruction_Branch_Devices(self,*args):
        global epsilon
        
        FunctionName,StoreNextLine,Relative=self.GetBranchRoot(args[0])

        Index1=self.GetArgIndex(args[1])
        

        JumpLine=self.GetArgValue(args[2])
        if self.Parent.Fields["Error"].Value == 1:return
        if Index1 in self.Parent.Pins:
            Matched=self.GetDeviceObject(self.Parent.Pins[Index1],DoError=False) != None
        else:
            Matched=False
        if FunctionName == "dns":
            Matched=not Matched
        elif FunctionName == "dse":
            pass
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
        
    def Instruction_Set_Conditional_Register(self,*args):
        global epsilon
        #Branch to line if device is not set and other ones like that
        FunctionName,_,_=self.GetBranchRoot(args[0])
        
        Values=[self.GetArgValue(X) for X in args[2:]]
        Index1=self.GetArgIndex(args[1])
        if self.Parent.Fields["Error"].Value == 1:return

        Matched=False
        if FunctionName == "eq":
            Matched=Values[0] == Values[1]

        elif FunctionName == "eqz":
            Matched=Values[0] == 0

        elif FunctionName == "ge":
            Matched=Values[0] >= Values[1]

        elif FunctionName == "gez":
            Matched=Values[0] >= 0

        elif FunctionName == "gt":
            Matched=Values[0] > Values[1]

        elif FunctionName == "gtz":
            Matched=Values[0] > 0

        elif FunctionName == "le":
            Matched=Values[0] <= Values[1]

        elif FunctionName == "lez":
            Matched=Values[0] <= 0

        elif FunctionName == "lt":
            Matched=Values[0] < Values[1]
        
        elif FunctionName == "ltz":
            Matched=Values[0] >= 0

        elif FunctionName == "ne":
            Matched=Values[0] != Values[1]
        
        elif FunctionName == "nez":
            Matched=Values[0] != 0

        elif FunctionName == "nan":
            Matched=Values[0] == "NaN"

        elif FunctionName == "nanz":
            Matched=Values[0] != "NaN"

        elif FunctionName == "ap":
            Matched=abs(Values[0] - Values[1]) <= max(Values[2] * max(abs(Values[0]), abs(Values[1])),epsilon * 8)

        elif FunctionName == "apz":
            Matched=abs(Values[0]) <= max(Values[1] * abs(Values[0]), epsilon * 8)

        elif FunctionName == "na":
            Matched=abs(Values[0] - Values[1]) > max(Values[2] * max(abs(Values[0]), abs(Values[1])), epsilon * 8)
            
        elif FunctionName == "naz":
            Matched=abs(Values[0]) > max (Values[1] * abs(Values[0]), epsilon * 8)
        else:
            Log.Warning("Unknown conditional type",Caller=f"Script line {self.Parent.Fields['LineNumber'].Value}")
            self.Parent.Fields["Error"].Value=1
            return 
        
        self.Registers[Index1]=int(Matched)
            #self.Registers[self.RegisterAliases["ra"]]=self.Parent.Fields['LineNumber'].Value + 1

    def Instruction_Set_Conditional_Register_Devices(self,*args):
        global epsilon
        
        FunctionName,_,_=self.GetBranchRoot(args[0])
        Index1=self.GetArgIndex(args[1])
        Index2=self.GetArgIndex(args[2])

        if self.Parent.Fields["Error"].Value == 1:return
        if Index2 in self.Parent.Pins:
            Matched=self.GetDeviceObject(self.Parent.Pins[Index2],DoError=False) != None
        else:
            Matched=False
        if FunctionName == "dns":
            Matched=not Matched
        elif FunctionName == "dse":
            pass
        else:
            Log.Warning("Unknown conditional type",Caller=f"Script line {self.Parent.Fields['LineNumber'].Value}")
            self.Parent.Fields["Error"].Value=1
            return 
        
        self.Registers[Index1]=int(Matched)

    def Instruction_Select(self,*args):
        Index1=self.GetArgIndex(args[1])
        Value1=self.GetArgValue(args[2])
        Value2=self.GetArgValue(args[3])
        Value3=self.GetArgValue(args[4])

        Output=0
        if Value1 != 0:
            Output=Value2
        else:
            Output=Value3
        self.Registers[Index1]=Output

    def RunUpdate(self):
        if self.Parent.Fields['LineNumber'].Value >= len(self.Code) or self.Parent.Fields["Error"].Value != 0:
            return
        CurrentLine=self.Code[self.Parent.Fields['LineNumber'].Value].strip()
        if CurrentLine != "":
            CurrentLine=SplitNotStringSpaces(CurrentLine," ")
            for CurrentIndex,CurrentFunction in self.FunctionMap["Functions"].items():
                if CurrentLine[0] in CurrentFunction["Alias"]:
                    if len(CurrentLine) - 1 == CurrentFunction["Alias"][CurrentLine[0]]:
                        
                        for X in range(0,len(CurrentLine) - 1):
                            TargetArgTypes=CurrentFunction["Args"][X].split("|")
                            CurrentArgTypes=self.GetArgType(CurrentLine[X+1],TargetArgTypes)
                            if CurrentArgTypes not in TargetArgTypes:
                                print(CurrentArgTypes)
                                Log.Warning(f"Arg {X+1} of {CurrentLine[0]} must be of type {CurrentFunction['Args'][X]}",Caller=f"Script line {self.Parent.Fields['LineNumber'].Value}")
                                self.Parent.Fields["Error"].Value=1
                                break
                        else:
                            self.FunctionMap["Functions"][CurrentIndex]["Function"](*CurrentLine)
                    else:
                        Log.Warning(f"{CurrentLine[0]} requires {CurrentFunction['Alias'][CurrentLine[0]]} args",Caller=f"Script line {self.Parent.Fields['LineNumber'].Value}")
                        self.Parent.Fields["Error"].Value=1
                    break
            else:
                Log.Warning(f"Unknown function {CurrentLine[0]}",Caller=f"Script line {self.Parent.Fields['LineNumber'].Value}")
                self.Parent.Fields["Error"].Value=1
        self.HighestSP=max(self.HighestSP,self.Registers[self.RegisterAliases["sp"]])
        self.Parent.Fields['LineNumber'].Value+=1
        #if self.LineNumber >= len(self.Code):
        #    self.LineNumber=0
class Device:
    def __init__(self,PrefabName:str,PrefabHash:int,DeviceName:str,DeviceNameHash:str,ReferenceId:int,Fields:dict,Pins:dict,PinsNumber:int,Slots:list,Varibles:dict,RunsCode:bool,StackEnabled:bool,StackLength:int,Code:str):
        self.PrefabName=PrefabName
        self.PrefabHash=PrefabHash
        self.DeviceName=DeviceName
        self.DeviceNameHash=DeviceNameHash
        self.ReferenceId=ReferenceId
        self.Fields=Fields
        self.Pins=Pins
        self.PinsNumber=PinsNumber
        self.Slots=Slots
        self.Varibles=Varibles
        self.RunsCode=RunsCode
        self.StackEnabled=StackEnabled
        self.StackLength=StackLength
        self.Code=Code
        if RunsCode:
            self.State=CodeRunner(self)
    
    def AddNetworkRef(self,Network):
        self.Network=Network

    def GetFieldValue(self,FieldName):
        if FieldName in self.Fields:
            if self.Fields[FieldName].Read:
                return (self.Fields[FieldName].Value,)
            else:
                return (None,f"{FieldName} cannot be read",)
        else:
            return (None,f"Unknown device value {FieldName}",)

    def SetFieldValue(self,FieldName,Value):
        if FieldName in self.Fields:
            if self.Fields[FieldName].Write:
                self.Fields[FieldName].Value=Value
                return (1,)
            else:
                return (None,f"{FieldName} cannot be written")
        else:
            return (None,f"Unknown device value {FieldName}")

    def PrintFields(self):
        Output=["\n+------------+-------+\n|Fields        |       |"]
        for X,Y in self.Fields.items():
            Output.append(f"|{X:<14}|{Y.Value:<7}|")
        Log.Info("\n".join(Output)+"\n+--------------+-------+")

class DeviceMaker:
    def __init__(self,DeviceFile:str="EmulatorFunctions/Devices.json"):
        self.Devices=json.loads(open(DeviceFile,"r").read())
    
    def MakeDevice(self,DeviceType:str,ReferenceId:int,DeviceName:str="",**kwargs):
        if DeviceType not in self.Devices:
            raise InvalidDeviceType(DeviceType)
        
        Output=copy.deepcopy(self.Devices[DeviceType])

        Output["Pins"]={"db":ReferenceId}#{(str(X),-1) for X in range(Output["Pins"]["Number"])}
        #Output["Pins"]["db"]=ReferenceId

        PrefabHash=ComputeCRC32(DeviceType)
        DeviceNameHash=ComputeCRC32(DeviceName)
        for X,Y in kwargs.items():
            if X in Output["Fields"]:
                if type(Y) == int:
                    Output["Fields"][X]["Value"]=Y
                else:
                    raise TypeError
            elif X == "Pins":
                if type(Y) == dict:
                    for A,B in Y.items():
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
        return Device(DeviceType,PrefabHash,DeviceName,DeviceNameHash,ReferenceId,Output["Fields"],Output["Pins"],self.Devices[DeviceType]["Pins"]["Number"],Output["Slots"],Output["Variables"],Property["RunCode"],Property["Stack"]["Enabled"],Property["Stack"]["Length"],Output["Variables"]["Code"])
    
    