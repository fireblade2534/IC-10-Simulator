import os
import json


def Main():
    Tests=[]
    for X in list(os.walk("TestCases"))[1:]:
        TestConfig=json.dump(open(f"{X[0]}/Config.json"))
        TestConfig["Code"]=open(f"{X[0]}/Program.ic10").read()
        Tests.append(TestConfig)

    for X in Tests:
        pass

if __name__ == "__main__":
    Main()