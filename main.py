import time
from registers import registers
from memory import memory
from random import randint
import pygame

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

def execute(first,x,y,n,nn,nnn: int, reg, ram, screen):
    match first:
        case 0:
            if nn == 0xe0: # clear screen
                for row in range(32):
                    for col in range(64):
                        screen[row][col] = 0
            if nn == 0xee: 
                reg.pc=reg.pop()
        case 1:
            reg.pc=nnn
        case 2:
            reg.push(reg.pc)
            reg.pc=nnn
        case 3:
            if nn == reg.variable[x]:
                reg.pc += 2
        case 4:
            if nn != reg.variable[x]:
                reg.pc += 2 
        case 5:
            if reg.variable[x] == reg.variable[y]:
                reg.pc += 2
        case 6:
            reg.variable[x]=nn
        case 7:
            reg.variable[x] += nn
        case 8:
            if n == 0:
                reg.variable[x] = reg.variable[y]
            elif n == 1:
                reg.variable[x] = reg.variable[x] | reg.variable[y]
            elif n == 2:
                reg.variable[x] = reg.variable[x] & reg.variable[y]
            elif n == 3:
                reg.variable[x] = reg.variable[x] ^ reg.variable[y]
            elif n == 4:
                if reg.variable[x] + reg.variable[y] > 255:
                    reg.variable[0xf] = 1
                reg.variable[x] = reg.variable(x) + reg.variable[y]
            elif n == 5:
                if reg.variable[x] < reg.variable[y]:
                    reg.variable[0xf] = 0
                reg.variable[x] = reg.variable[x] - reg.variable[y]
            elif n == 7:
                if reg.variable[x] > reg.variable[y]:
                    reg.variable[0xf] = 0
                reg.variable[x] = reg.variable[y] - reg.variable[x]
            elif n == 6 or n == 0xe:
                reg.variable[x] = reg.variable[y] # CONFIGURABLE! skip this lign
                if n == 6:
                    if reg.variable[x] & 0x1 == 1:
                        shifted_out=1
                    elif reg.variable[x] & 0x1 == 0:
                        shifted_out=0
                    reg.variable[x] = reg.variable[x] >> 1
                    if shifted_out == 1:
                        reg.variable[0xf] = 1
                    elif shifted_out == 0:
                        reg.variable[0xf] = 0
                    
                elif n == 0xe:
                    if reg.variable[x] & 0x80 == 1:
                        shifted_out=1
                    elif reg.variable[x] & 0x80 == 0:
                        shifted_out=0
                    reg.variable[x] = reg.variable[x] << 1
                    if shifted_out == 1:
                        reg.variable[0xf] = 1
                    elif shifted_out == 0:
                        reg.variable[0xf] = 0

        case 9:
            if reg.variable[x] != reg.variable[y]:
                reg.pc += 2
        case 0xa:
            reg.I = nnn
        case 0xb:
            reg.pc = nnn + reg.variable[0] # CONFIGURABLE! nnn -> xnn
        case 0xc:
            reg.variable[x] = randint(0, nn) & nn
        case 0xd:
            coor_x = reg.variable[x] & 63 # modulo 64 ( screen 64 pixels wide )
            coor_y = reg.variable[y] & 31 # modulo 32 ( screen 32 pixels tall )
            reg.variable[0xf] = 0 # reset flag
            for row in range(n) :
                sprite_data = ram[reg.I + row]
                for col in range(8):
                    if (sprite_data & (0x80 >> col)) != 0:
                        screen_col = coor_x + col
                        screen_row = coor_y + row
                    
                        if screen_col >= 64 or screen_row >= 32: continue # out of screen

                        if screen[screen_row][screen_col] == 1:  # if pixel is on
                            reg.variable[0xf] = 1  # flag

                        
                        screen[screen_row][screen_col] ^= 1 # toggle the screen pixel





def cpu_cycle(ram, reg, screen) -> None:
    intruction = fetch(ram, reg)
    first,x,y,n,nn,nnn = decode(intruction)
    execute(first, x, y, n, nn, nnn, reg, ram, screen)

def load(ch8, ram):
    with open(ch8, "rb") as file: # open in binary
        rom_data = file.read()  # read the file
    
    for i, byte in enumerate(rom_data):
        ram[0x200 + i] = byte


def render_screen(screen, window, SCALE):
    window.fill((0, 0, 0))
    for row in range(32):
        for col in range(64):
            if screen[row][col] == 1:
                pygame.draw.rect(window, (255,255,255),(col * SCALE, row * SCALE, 1 * SCALE, 1 * SCALE) )
    pygame.display.flip()


def main() -> None:
    ram = memory()
    reg = registers()
    screen = [[0] * 64 for _ in range(32)] # init screen array 64x32

    pygame.init()
    SCALE = 20
    window = pygame.display.set_mode((64*SCALE,32*SCALE))
    pygame.display.set_caption("CHIP-8 Emulator")


    ch8 = "IBM Logo.ch8"
    load(ch8, ram)

    reg.pc = 0x200

    while True:
        last_time = time.perf_counter()
        cpu_cycle(ram, reg, screen)

        #render_screen(screen)
        #print("\n")~

        render_screen(screen, window, SCALE)

        current_time = time.perf_counter()
        elapsed_time = current_time - last_time
        
        # reduce cpu stress while still having the accuracy of perf_counter
        if elapsed_time < INTERVAL:
            sleep = INTERVAL - elapsed_time
            if sleep > 0:
                time.sleep(sleep * 0.9) 

        while elapsed_time < INTERVAL:
            current_time = time.perf_counter()
            elapsed_time = current_time - last_time

if __name__ == "__main__":
    main()


