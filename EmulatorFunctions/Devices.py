from re import L
from UtilityFunctions.Error import *
from UtilityFunctions.Utility import *
from __init__ import Log

from EmulatorFunctions.CodeRunner import *

import json
import copy

class SlotClass:
    def Type_Any(): #Not an offical type only used to represent slots that can have anything in them
        return -1
    def Type_None():
        return 0
    def Type_Helmet():
        return 1
    def Type_Suit():
        return 2
    def Type_Back():
        return 3
    def Type_GasFilter():
        return 4
    def Type_GasCanister():
        return 5
    def Type_Motherboard():
        return 6
    def Type_Circuitboard():
        return 7
    def Type_DataDisk():
        return 8
    def Type_Organ():
        return 9
    def Type_Ore():
        return 10
    def Type_Plant():
        return 11
    def Type_Uniform():
        return 12
    def Type_Entity():
        return 13
    def Type_Battery():
        return 14
    def Type_Egg():
        return 15
    def Type_Belt():
        return 16
    def Type_Tool():
        return 17
    def Type_Appliance():
        return 18
    def Type_Ingot():
        return 19
    def Type_Torpedo():
        return 20
    def Type_Cartridge():
        return 21
    def Type_AccessCard():
        return 22
    def Type_Magazine():
        return 23
    def Type_Circuit():
        return 24
    def Type_Bottle():
        return 25
    def Type_ProgrammableChip():
        return 26
    def Type_Glasses():
        return 27
    def Type_CreditCard():
        return 28
    def Type_DirtCanister():
        return 29
    def Type_SensorProcessingUnit():
        return 30
    def Type_LiquidCanister():
        return 31
    def Type_LiquidBottle():
        return 32
    def Type_Wreckage():
        return 33
    def Type_SoundCartridge():
        return 34
    def Type_DrillHead():
        return 35
    def Type_ScanningHead():
        return 36
    def Type_Flare():
        return 37
    def Type_Blocked():
        return 38
    def Type_SuitMod():
        return 39
    def Type_Crate():
        return 40
    def Type_Portables():
        return 41

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
    def __init__(self,DeviceFile:str="Configs/Devices.json"):
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
    
    