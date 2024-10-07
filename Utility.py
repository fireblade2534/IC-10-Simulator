import zlib
def ComputeCRC32(Input):
    Hash= zlib.crc32(bytes(Input,"utf-8"))
    if (Hash & (1 << (32 - 1))) != 0:
        Hash = Hash - (1 << 32)
    return Hash

class Field:
    def __init__(self,StartValue:int=0,Read:bool=False,Write:bool=False):
        self.Value=StartValue