class State:
    def __init__(self,RunningDevice,Script:str,Constants:dict,Devices:dict):
        self.Registers={f"r{X}":0 for X in range(0,18)}
        self.RegisterAliases={"sp":16,"ra":17}
        self.Stack=[0 for X in range(512)]
        self.Constants=Constants
        self.Devices=Devices

        self.Script=Script

        self.RunningDevice=RunningDevice

    def ParseScript(self):
        pass

def ParseConfigFile(Text):
    Text=Text.split("\n")

def DumpConfigFile(State:State):
    ParsedDevices={}
    Output={"Constants":State.Constants
            "Devices":{}}

if __name__ == "__main__":
    pass