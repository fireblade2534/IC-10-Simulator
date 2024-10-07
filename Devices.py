import Utility
class Device:
    def __init__(self,PrefabName:str,Name:str=None,ReferenceId:int=None):
        self.PrefabName=PrefabName
        self.PrefabHash=Utility.Field(StartValue=Utility.ComputeCRC32(PrefabName),Read=True,Write=False)
        if Name == "" or Name=None:
            Name=self.PrefabName
        self.Name=Name
        self.ReferenceId=Utility.Field(StartValue=ReferenceId,Read=True,Write=False)

class StructureCircuitHousing(Device):
    def __init__(self, Name: str=None, ReferenceId: int = None,On:int=0,Power: int=1,RequiredPower:int=0,Setting:int=0):
        self.Error=Utility.Field(StartValue=0,Read=True,Write=False)
        self.LineNumber=Utility.Field(StartValue=0,Read=True,Write=True)
        self.On=Utility.Field(StartValue=On,Read=True,Write=True)
        self.Power=Utility.Field(StartValue=Power,Read=True,Write=False)
        self.RequiredPower=Utility.Field(StartValue=RequiredPower,Read=True,Write=False)
        self.Setting=Utility.Field(StartValue=Setting,Read=True,Write=True)
        
        super().__init__(self.__class__.__name__,Name, ReferenceId)
