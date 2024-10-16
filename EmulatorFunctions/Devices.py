from UtilityFunctions.Error import *
from UtilityFunctions.Utility import *
import json
import copy
class Device:
    def __init__(self,PrefabName:str,PrefabHash:int,DeviceName:str,ReferenceId:int,Fields:dict,Pins:dict,Slots:list,Varibles:dict,RunsCode:bool,StackEnabled:bool,StackLength:int):
        self.PrefabName=PrefabName
        self.PrefabHash=PrefabHash
        self.DeviceName=DeviceName
        self.ReferenceId=ReferenceId
        self.Fields=Fields
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

        return Device(DeviceType,PrefabHash,DeviceName,ReferenceId,Output["Fields"],Output["Pins"])