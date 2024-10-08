from Utility import *
from Error import *
class Device:
    def __init__(self,PrefabName:str,Name:str=None,ReferenceId:int=None):
        self.PrefabName=PrefabName
        self.PrefabHash=Field(StartValue=ComputeCRC32(PrefabName),Read=True,Write=False)
        if Name == "" or Name==None:
            Name=self.PrefabName
        self.Name=Name
        self.ReferenceId=Field(StartValue=ReferenceId,Read=True,Write=False)

    def GetConfig(self):
        Output={}
        for X,Y in self.__dict__.items():
            if type(Y) == str:
                Output[X]={"Type":"str","Args":Y}
            elif type(Y) == list:
                Output[X]={"Type":"list","Args":[]}
                for B in Y:
                    ItemName,ItemValue=B.GetConfig()
                    Output[X]["Args"].append({"Type":ItemName,"Args":ItemValue})
            elif type(Y) == int:
                Output[X]={"Type":"int","Args":Y}
            else:
                try:
                    ItemName,ItemValue=Y.GetConfig()
                    Output[X]={"Type":ItemName,"Args":ItemValue}
                except:
                    raise BadConfigType(Y)
        return self.PrefabName,Output

    @staticmethod
    def ParseConfigFile(Data):
        
        FinalArgs={}
        for X,Y in Data["Args"].items():
            print(Y["Type"])
            if Y["Type"] == "str":
                FinalArgs[X]=Y["Args"]
            elif Y["Type"] == "int":
                FinalArgs[X]=Y["Args"]
            elif Y["Type"] == "list":
                FinalArgs[X]=[]
                for A in Y["Args"]:
                    Item=globals()[f'{A["Type"]}'].ParseConfigFile(A)
                    FinalArgs[X].append(Item)
            else:
                FinalArgs[X]=globals()[f'{Y["Type"]}'].ParseConfigFile(Y)
        globals()[f'{Data["Type"]}'](*FinalArgs)

class Pins:
    def __init__(self,d0:int=0,d1:int=0,d2:int=0,d3:int=0,d4:int=0,d5:int=0):
        self.d0=d0
        self.d1=d1
        self.d2=d2
        self.d3=d3
        self.d4=d4
        self.d5=d5
    
    def GetConfig(self):
        return "Pins",{"d0":self.d0,"d1":self.d1,"d2":self.d2,"d3":self.d3,"d4":self.d4,"d5":self.d5}

    @staticmethod
    def ParseConfigFile(Data):
        return Pins(*Data["Args"])

class Slot:
    def __init__(self,Class:int=0,Damage:int=0,MaxQuantity:int=0,OccupantHash:int=0,Occupied:int=0,PrefabHash:int=0,Quantity:int=0,ReferenceId:int=0,SortingClass:int=0):
        self.Class=Field(StartValue=Class,Read=True,Write=False)
        self.Damage=Field(StartValue=Damage,Read=True,Write=False)
        self.MaxQuantity=Field(StartValue=MaxQuantity,Read=True,Write=False)
        self.OccupantHash=Field(StartValue=OccupantHash,Read=True,Write=False)
        self.Occupied=Field(StartValue=Occupied,Read=True,Write=False)
        self.PrefabHash=Field(StartValue=PrefabHash,Read=True,Write=False)
        self.Quantity=Field(StartValue=Quantity,Read=True,Write=False)
        self.ReferenceId=Field(StartValue=ReferenceId,Read=True,Write=False)
        self.SortingClass=Field(StartValue=SortingClass,Read=True,Write=False)
    
    def GetConfig(self):
        Output={}
        for X,Y in self.__dict__.items():
            try:
                ItemName,ItemValue=Y.GetConfig()
                Output[X]={"Type":ItemName,"Args":ItemValue}
            except:
                raise BadConfigType(Y)
        return "Slot",Output

    @staticmethod
    def ParseConfigFile(Data):
        return Slot(*Data["Args"])
    
class StructureCircuitHousing(Device):
    
    def __init__(self, Name: str=None, ReferenceId: int = None,On:int=0,Power: int=1,RequiredPower:int=0,Setting:int=0,Pins:Pins=None,Slots:list[Slot]=[Slot()]):
        self.Error=Field(StartValue=0,Read=True,Write=False)
        self.LineNumber=Field(StartValue=0,Read=True,Write=True)
        self.On=Field(StartValue=On,Read=True,Write=True)
        self.Power=Field(StartValue=Power,Read=True,Write=False)
        self.RequiredPower=Field(StartValue=RequiredPower,Read=True,Write=False)
        self.Setting=Field(StartValue=Setting,Read=True,Write=True)
        self.Slots=Slots
        self.Pins=Pins
        self.Pins.db=ReferenceId
        

        super().__init__(self.__class__.__name__,Name, ReferenceId)

