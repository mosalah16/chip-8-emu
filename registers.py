class registers:
    def __init__(self) -> None:
        self.variable= [0x00]*16 # 0 to f
        self.I = 0x0000 # 16-bit
        self.delay = 0x00 # 8-bit
        self.sound = 0x00 # 8-bit
        self.pc = 0x200 # the program starts at 0x200 ram
        self.sp = 0x00 # 8-bit
        self.stack = [0x0000] * 16 # 16-bit * 16 lvl 
