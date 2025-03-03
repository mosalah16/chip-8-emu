import time
from registers import registers
from memory import memory

INTERVAL = 1 / 700 

current_time = 0

def fetch(ram: int, reg: int) -> int:

    instruction = (ram[reg.pc] << 8) | ram[reg.pc + 1]
    reg.pc += 2
    return instruction

def decode(instruction: int) -> int:
    #first nibble
    first = ( instruction & 0xf000 ) >> 12 #1111 0000 0000 0000

    #second nibble
    x = ( instruction & 0x0f00  ) >> 8 #0000 1111 0000 0000

    #third nibble
    y = ( instruction & 0x00f0 ) >> 4 #0000 0000 1111 0000

    #fourth nibble
    n = ( instruction & 0x000f ) #0000 0000 0000 1111

    nn = instruction & 0x00ff

    nnn = instruction & 0x0fff

    return first,x,y,n,nn,nnn

def execute(first,x,y,n,nn,nnn: int, reg):
    match first:
        case 0:
            if x==0x0 and y==0xe and n==0x0: pass #clear screen
            if x==0x0 and y==0xe and n==0xe: 
                reg.pc=reg.pop()
        case 1:
            reg.pc=nnn
        case 2:
            reg.push(reg.pc)
            reg.pc=nnn
        


def cpu_cycle(ram, reg) -> None:
    intruction = fetch(ram, reg)
    first,x,y,n,nn,nnn = decode(intruction)
    execute(first, x, y, n, nn, nnn, reg)


def main() -> None:
    ram = memory()
    reg = registers()

    while True:
        last_time = time.perf_counter()
        cpu_cycle(ram, reg)
        current_time = time.perf_counter()
        elapsed_time = current_time - last_time
        
        # reduce cpu stress while still having the accuracy of perf_counter
        if elapsed_time < INTERVAL:
            sleep = INTERVAL - elapsed_time
            if sleep > 0:
                time.sleep(sleep * 0.95) 

        while elapsed_time < INTERVAL:
            current_time = time.perf_counter()
            elapsed_time = current_time - last_time

if __name__ == "__main__":
    main()


