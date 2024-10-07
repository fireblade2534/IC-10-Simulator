import Devices
class State:
    def __init__(self,RunningDevice:int,Script:str,Devices:dict):
        self.Registers={f"r{X}":0 for X in range(0,18)}
        self.RegisterAliases={"sp":16,"ra":17}
        self.Stack=[0 for X in range(512)]
        self.Constants={}
        self.Devices=Devices

        self.Script=Script

        self.RunningDevice=RunningDevice

    def ParseScript(self):
        pass

    def DumpConfigFile(self):
        ParsedDevices={}
        for X,Y in self.Devices.items():
            print(dir(Y))
        self.
        Output={"Constants":self.Constants,
                "Devices":{}}

    
    @staticmethod
    def ParseConfigFile(Text):
        Text=Text.split("\n")


if __name__ == "__main__":
    Devices={69:Devices.StructureCircuitHousing(ReferenceId=69,Pins=Devices.Pins())}
    S=State(69,"",Devices=Devices)
    S.DumpConfigFile()