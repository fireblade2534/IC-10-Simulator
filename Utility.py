import zlib
def ComputeCRC32(Input):
    Hash= zlib.crc32(bytes(Input,"utf-8"))
    if (Hash & (1 << (32 - 1))) != 0:
        Hash = Hash - (1 << 32)
    return Hash