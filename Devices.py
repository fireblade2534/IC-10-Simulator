import Utility
class Device:
    def __init__(self,PrefabName:str,Name:str=None,ID:int=None):
        self.PrefabName=PrefabName
        self.PrefabHash=Utility.ComputeCRC32(PrefabName)
        if Name == "" or Name=None:
            Name=self.PrefabName
        self.Name=Name
        self.ID=ID

class StructureCircuitHousing(Device):
    def __init__(self, Name: str=None, ID: int = None):
        super().__init__(self.__class__.__name__,Name, ID)
