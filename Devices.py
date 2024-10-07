import Utility
class Device:
    def __init__(self,PrefabName:str,Name:str=None,ReferenceId:int=None):
        self.PrefabName=PrefabName
        self.PrefabHash=Utility.Field(StartValue=Utility.ComputeCRC32(PrefabName),Read=True,Write=False)
        if Name == "" or Name==None:
            Name=self.PrefabName
        self.Name=Name
        self.ReferenceId=Utility.Field(StartValue=ReferenceId,Read=True,Write=False)

class Pins:
        def __init__(self,d0:int=0,d1:int=0,d2:int=0,d3:int=0,d4:int=0,d5:int=0):
            self.d0=d0
            self.d1=d1
            self.d2=d2
            self.d3=d3
            self.d4=d4
            self.d5=d5

class Slot:
     def __init__(self,Class:int=0,Damage:int=0,MaxQuantity:int=0,OccupantHash:int=0,Occupied:int=0,PrefabHash:int=0,Quantity:int=0,ReferenceId:int=0,SortingClass:int=0):
          self.Class=Utility.Field(StartValue=Class,Read=True,Write=False)
          self.Damage=Utility.Field(StartValue=Damage,Read=True,Write=False)
          self.MaxQuantity=Utility.Field(StartValue=MaxQuantity,Read=True,Write=False)
          self.OccupantHash=Utility.Field(StartValue=OccupantHash,Read=True,Write=False)
          self.Occupied=Utility.Field(StartValue=Occupied,Read=True,Write=False)
          self.PrefabHash=Utility.Field(StartValue=PrefabHash,Read=True,Write=False)
          self.Quantity=Utility.Field(StartValue=Quantity,Read=True,Write=False)
          self.ReferenceId=Utility.Field(StartValue=ReferenceId,Read=True,Write=False)
          self.SortingClass=Utility.Field(StartValue=SortingClass,Read=True,Write=False)

class StructureCircuitHousing(Device):
    
    def __init__(self, Name: str=None, ReferenceId: int = None,On:int=0,Power: int=1,RequiredPower:int=0,Setting:int=0,Pins:Pins=None,Slots:list[Slot]=[Slot()]):
        self.Error=Utility.Field(StartValue=0,Read=True,Write=False)
        self.LineNumber=Utility.Field(StartValue=0,Read=True,Write=True)
        self.On=Utility.Field(StartValue=On,Read=True,Write=True)
        self.Power=Utility.Field(StartValue=Power,Read=True,Write=False)
        self.RequiredPower=Utility.Field(StartValue=RequiredPower,Read=True,Write=False)
        self.Setting=Utility.Field(StartValue=Setting,Read=True,Write=True)
        self.Slots=Slots
        self.Pins=Pins
        self.Pins.db=ReferenceId
        

        super().__init__(self.__class__.__name__,Name, ReferenceId)
