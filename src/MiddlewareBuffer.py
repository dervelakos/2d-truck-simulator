import struct

class MiddlewareBuffer:
    def __init__(self, dataLen: int, headerLen: int):
        self.headerLen = headerLen
        self.buff = bytearray(dataLen + headerLen)
        self.dataMaxLen = dataLen
        self.dataOffset = headerLen

    # ──────────────────────────────────────────────
    # Core helpers (used by both write* and add*)
    # ──────────────────────────────────────────────

    def _write(self, fmt: str, offset: int, val):
        struct.pack_into(fmt, self.buff, offset, val)

    def _add(self, fmt: str, size: int, val):
        if (self.dataOffset - self.headerLen + size) > self.dataMaxLen:
            raise BufferError("MiddlewareBuffer overflow")

        struct.pack_into(fmt, self.buff, self.dataOffset, val)
        self.dataOffset += size

    def _read(self, fmt, offset):
        return struct.unpack_from(fmt, self.buff, offset)[0]

    def _readNext(self, read_func, size):
        if (self.dataOffset - self.headerLen + size) > self.dataMaxLen:
            raise BufferError("Read beyond buffer")
        val = read_func(self.dataOffset)
        self.dataOffset += size
        return val


    # ──────────────────────────────────────────────
    # Public API (compressed but explicit)
    # ──────────────────────────────────────────────

    def getSize(self) -> int:
        return self.dataOffset

    def getBytes(self):
        return self.buff[0:self.dataOffset]

    # write*
    def writeInt8(self, val, offset):    self._write('<b', offset, val)
    def writeInt16(self, val, offset):   self._write('<h', offset, val)
    def writeInt32(self, val, offset):   self._write('<i', offset, val)
    def writeInt64(self, val, offset):   self._write('<q', offset, val)

    def writeUInt8(self, val, offset):   self._write('<B', offset, val)
    def writeUInt16(self, val, offset):  self._write('<H', offset, val)
    def writeUInt32(self, val, offset):  self._write('<I', offset, val)
    def writeUInt64(self, val, offset):  self._write('<Q', offset, val)

    def writeFloat32(self, val, offset): self._write('<f', offset, val)
    def writeFloat64(self, val, offset): self._write('<d', offset, val)

    # add*
    def addInt8(self, val):    self._add('<b', 1, val)
    def addInt16(self, val):   self._add('<h', 2, val)
    def addInt32(self, val):   self._add('<i', 4, val)
    def addInt64(self, val):   self._add('<q', 8, val)

    def addUInt8(self, val):   self._add('<B', 1, val)
    def addUInt16(self, val):  self._add('<H', 2, val)
    def addUInt32(self, val):  self._add('<I', 4, val)
    def addUInt64(self, val):  self._add('<Q', 8, val)

    def addFloat32(self, val): self._add('<f', 4, val)
    def addFloat64(self, val): self._add('<d', 8, val)

    #read*
    def readInt8(self, offset):    return self._read('<b', offset)
    def readInt16(self, offset):   return self._read('<h', offset)
    def readInt32(self, offset):   return self._read('<i', offset)
    def readInt64(self, offset):   return self._read('<q', offset)

    def readUInt8(self, offset):   return self._read('<B', offset)
    def readUInt16(self, offset):  return self._read('<H', offset)
    def readUInt32(self, offset):  return self._read('<I', offset)
    def readUInt64(self, offset):  return self._read('<Q', offset)

    def readFloat32(self, offset): return self._read('<f', offset)
    def readFloat64(self, offset): return self._read('<d', offset)

    #readNext*
    def readNextInt8(self):    return self._readNext(self.readInt8, 1)
    def readNextInt16(self):   return self._readNext(self.readInt16, 2)
    def readNextInt32(self):   return self._readNext(self.readInt32, 4)
    def readNextInt64(self):   return self._readNext(self.readInt64, 8)

    def readNextUInt8(self):   return self._readNext(self.readUInt8, 1)
    def readNextUInt16(self):  return self._readNext(self.readUInt16, 2)
    def readNextUInt32(self):  return self._readNext(self.readUInt32, 4)
    def readNextUInt64(self):  return self._readNext(self.readUInt64, 8)

    def readNextFloat32(self): return self._readNext(self.readFloat32, 4)
    def readNextFloat64(self): return self._readNext(self.readFloat64, 8)
