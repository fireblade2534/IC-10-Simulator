import zlib
def ComputeCRC32(Input):
    Hash= zlib.crc32(bytes(Input,"utf-8"))
    if (Hash & (1 << (32 - 1))) != 0:
        Hash = Hash - (1 << 32)
    return Hash

def SplitNotStringSpaces(String,SplitChar):
    Splits=[]
    CurrentString=""
    InBadString=False
    for X in String:
        if X == '"':
            InBadString=not InBadString
        if InBadString == False:
            if X == SplitChar:
                Splits.append(CurrentString)
                CurrentString=""
                continue
        CurrentString+=X
    Splits.append(CurrentString)
    return Splits
class Field:
    def __init__(self,StartValue:int=0,Read:bool=False,Write:bool=False):
        self.Value=StartValue
        self.Read=Read
        self.Write=Write
    def GetConfig(self):
        return "Field",{"StartValue":self.Value,"Read":self.Read,"Write":self.Write}
    
    @staticmethod
    def ParseConfigFile(Data):
        return Field(*Data["Args"])