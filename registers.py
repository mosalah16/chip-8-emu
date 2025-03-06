from ctypes import c_uint16, c_uint8

class Registers:
    def __init__(self) -> None:
        self.variable= bytearray([0x00] * 16) # 0 to f
        self.I = c_uint16(0x0000) # 16-bit
        self.delay = c_uint8(0x00) # 8-bit
        self.sound = c_uint8(0x00) # 8-bit
        self.pc = c_uint16(0x200) # the program starts at 0x200 ram
        self.sp = c_uint8(0x00) # 8-bit
        self.stack = [0x0000] * 16 # 16-bit * 16 lvl
    

    def push(self, value_: int) -> None:
        self.sp.value += 1
        self.stack[self.sp.value] = value_
        
    
    def pop(self) -> int:
        valeur = self.stack[self.sp.value]
        self.sp.value -= 1
        return valeur