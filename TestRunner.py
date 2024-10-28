from ast import Pass
import os
import json
import EmulatorFunctions.Devices as Devices
import EmulatorFunctions.Network as Network
from UtilityFunctions.Error import *
import UtilityFunctions.Logging as Logging
from UtilityFunctions.Utility import *
import Main
from Main import Log
from Main import MainManager

class TestState:
    def __init__(self,TestIndex:str,Name:str):
        self.TestIndex=TestIndex
        self.Name=Name
        self.Passed=True
        self.Reason=[]
    
    def FailTest(self,Reason:str):
        self.Passed=False
        self.Reason.append(Reason)
        
    def TestPassed(self) -> bool:
        return self.Passed

def MainTest():
    Tests=[]
    for X in list(os.walk("TestCases"))[1:]:
        TestConfig=json.load(open(f"{X[0]}/Config.json","r"))
        TestConfig["Code"]=open(f"{X[0]}/Program.ic10","r").read()
        TestConfig["CaseName"]=X[0]
        Tests.append(TestConfig)

    Outputs=[]

    for X in Tests:
        MNet=Network.Network()
        DM=Devices.DeviceMaker()
        MNet.AddDevice(DM.MakeDevice("StructureCircuitHousing",69,Code=X["Code"]))
        MM=MainManager([MNet])

        Case=TestState(X["CaseName"],X["Name"])

        for Y in range(0,X["LoopLines"]):
            if MM.Networks[0].DeviceList[69].Fields["Error"].Value == 1:
                Case.FailTest(f"Program errored early on line {MM.Networks[0].DeviceList[69].Fields['LineNumber'].Value}")
                break
            MM.RunScripts()

        

        if Case.TestPassed():
            for A,B in MM.Networks[0].DeviceList[69].Fields.items():
                if A not in ["ReferenceId","PrefabHash"]:
                    if B.Value != X["Expected"]["Fields"][A]:
                        Case.FailTest(f'Field "{A}" expected {X["Expected"]["Fields"][A]} got {B.Value}')
                
            for A,B in MM.Networks[0].DeviceList[69].State.Registers.items():
                Failed=False
                if type(X["Expected"]["Registery"][A]) == str or type(B) == str:
                    if B != X["Expected"]["Registery"][A]:
                        Failed=True
                else:
                    if abs(B - X["Expected"]["Registery"][A]) > 0.0000001:
                        Failed=True
                if Failed:
                    Case.FailTest(f'Registery "{A}" expected {X["Expected"]["Registery"][A]} got {B}')
            
            for A,B in enumerate(MM.Networks[0].DeviceList[69].State.Stack):
                if str(A) in X["Expected"]["Stack"]:
                    Failed=False
                    if type(X["Expected"]["Stack"][str(A)]) == str or type(B) == str:
                        if B != X["Expected"]["Stack"][str(A)]:
                            Failed=True
                    else:
                        if abs(B - X["Expected"]["Stack"][str(A)]) > 0.0000001:
                            Failed=True
                    if Failed:
                        Case.FailTest(f'Stack "{A}" expected {X["Expected"]["Stack"][str(A)]} got {B}')
                else:
                    if B != 0:
                        Case.FailTest(f'Extra stack item at "{A}"')
            
            #Account for extra constants
            for A in X["Expected"]["Constant"]:
                if A not in MM.Networks[0].DeviceList[69].State.Constants:
                    Case.FailTest(f'Constant "{A}" not declared')

            for A,B in MM.Networks[0].DeviceList[69].State.Constants.items():
                if A in X["Expected"]["Constant"]:
                    if B != X["Expected"]["Constant"][A]:
                        Case.FailTest(f'Constant "{A}" expected {X["Expected"]["Constant"][A]} got {B}')
                else:
                    Case.FailTest(f'Extra constant "{A}" was defined')
                
            for A in X["Expected"]["Alias"]:
                if A not in MM.Networks[0].DeviceList[69].State.RegisterAliases:
                    Case.FailTest(f'Alias "{A}" not declared')

            #Account for not defining alias in program or extra aliases
            for A,B in MM.Networks[0].DeviceList[69].State.RegisterAliases.items():
                if A in X["Expected"]["Alias"]:
                    if B != X["Expected"]["Alias"][A]:
                        Case.FailTest(f'Alias "{A}" expected {X["Expected"]["Alias"][A]} got {B}')
                else:
                    Case.FailTest(f'Extra alias "{A}" was defined')
        Outputs.append(Case)


    NumberPassed=sum([1 for X in Outputs if X.TestPassed()])
    Total=len(Outputs)

    Log.Info("Tests Complete!")
    Log.Info(f"Tests passed: {NumberPassed}/{Total}")
    Log.Info(f"Percentage passed: {(NumberPassed/Total)*100:.0f}%")
    if NumberPassed != Total:
        Log.Info("")
        Log.Info("Tests Info:")
        for X in Outputs:
            if X.TestPassed() == False:
                Log.Info(f"{X.TestIndex} - {X.Name}:")
                for Y in X.Reason:
                    Log.Info(Y)
                Log.Info("")
                
if __name__ == "__main__":
    MainTest()