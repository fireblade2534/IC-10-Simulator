from UtilityFunctions.Error import *
from UtilityFunctions.Utility import *
from Main import Log

from EmulatorFunctions.CodeRunner import *

import json
import copy


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
    
    