class InternalState:
    def __init__(self):
        self.Registers={f"r{X}":0 for X in range(0,18)}
        self.RegisterAliases={"sp":16,"ra":17}
        self.Stack=[0 for X in range(512)]
        self.Constants={}
        self.Devices={}



print(InternalState().Registers)