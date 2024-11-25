import os, sys
sys.path.insert(0, os.getcwd()) 

import requests
import json
import Configs.Constants as Constants

def DeviceParser(Json):
    Output={}
    
    for X in Json["data"]:
        DeviceInfo={"Name":X["Title"],"Fields":{},"ConnectionsNumber":len(X["connections"]), "Pins": {"Number":X["deviceConnectCount"]}, "SlotType":"Type_None", "Slots": [],"Properties": {
      "RunCode": False,
      "Stack": {
        "Enabled": False,
        "Length": 512
      }
    },"Variables": {
      "Code": "NONE"
    }}

        for Y in X["logics"]:
            if Y["name"] not in Constants.DO_NOT_DEFINE_FIELDS:
                Perms={"Value":0,"Read":"Read" in Y["permissions"],"Write":"Write" in Y["permissions"]}
                if Y["name"] in Constants.OVERRIDE_FIELD_DEFAULT:
                    Perms["Value"]=Constants.OVERRIDE_FIELD_DEFAULT[Y["name"]]
                DeviceInfo["Fields"][Y["name"]]=Perms
            
        for Y in X["slots"]:
            DeviceInfo["Slots"].append({"Type":f"Type_{Y['SlotType']}","Name":Y["SlotName"],"Index":Y["SlotIndex"]})

        if X["hasChip"]:
            DeviceInfo["Properties"]["RunCode"]=True

        if "hasLogicInstructions" in X["tags"] or X["hasChip"]:
            DeviceInfo["Properties"]["Stack"]["Enabled"]=True
        
        Output[X["PrefabName"]]=DeviceInfo
    json.dump(Output,open("Configs/Devices.json","w"),indent=4)
    return 1

def Main():
    MenuOptions={"device":{"Url":"https://assets.ic10.dev/languages/EN/devices.json","Parser":DeviceParser}}
    MenuOptionsKeys=list(MenuOptions.keys()) + ['exit']


    PrintMenuOptions='\n'.join([f'{X}. {Y.title()}' for X,Y in enumerate(MenuOptionsKeys)])

    while True:
        print(f"Options:\n{PrintMenuOptions}")
        while True:
            Input=input(f": ").lower()
            try:
                IntInput=int(Input)
                Input = MenuOptionsKeys[IntInput]
            except:
                pass
            if Input == "exit" or Input == len(MenuOptions):
                exit()

            if Input in MenuOptions:
                break
            
        print(f"\nSelected downloading {Input.title()}")
        try:
            Req=requests.get(MenuOptions[Input]["Url"])
        except:
            print("Failed to read url")
            continue
        Status=MenuOptions[Input]["Parser"](Req.json())
        if Status == 1:
            print("SUCCESS")
        else:
            print("FAILED")

if __name__ == "__main__":
    Main()