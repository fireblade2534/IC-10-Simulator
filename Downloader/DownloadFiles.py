import requests
import json
def DeviceParser(Json):
    Output={}
    
    for X in Json["data"]:
        DeviceInfo={"Fields":{}}

        for Y in X["logics"]:



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