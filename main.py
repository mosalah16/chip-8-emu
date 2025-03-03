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

def execute(first,x,y,n,nn,nnn: int, reg, ram, screen, keys):
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
                reg.variable[x] = reg.variable[x] + reg.variable[y]
            elif n == 5:
                if reg.variable[x] < reg.variable[y]:
                    reg.variable[0xf] = 0
                reg.variable[x] = reg.variable[x] - reg.variable[y]
            elif n == 7:
                if reg.variable[x] > reg.variable[y]:
                    reg.variable[0xf] = 0
                reg.variable[x] = reg.variable[y] - reg.variable[x]
            elif n == 6:
                reg.variable[0xf] = reg.variable[x] & 0x1
                reg.variable[x] >>= 1
            elif n == 0xe:
                reg.variable[0xf] = (reg.variable[x] & 0x80) >> 7
                reg.variable[x] = (reg.variable[x] << 1) & 0xff

        case 9:
            if reg.variable[x] != reg.variable[y]:
                reg.pc += 2
        case 0xa:
            reg.I = nnn
        case 0xb:
            reg.pc = nnn + reg.variable[0] # CONFIGURABLE! nnn -> xnn
        case 0xc:
            reg.variable[x] = randint(0, 255) & nn
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
        case 0xe:
            if nn == 0xa1:
                if keys[reg.variable[x]] == 0:
                    reg.pc += 2
            elif nn == 0x9e:
                if keys[reg.variable[x]] == 1:
                    reg.pc += 2
        case 0xf:
            if nn == 0x07:
                reg.variable[x] = reg.delay
            elif nn == 0x15:
                reg.delay = reg.variable[x]
            elif nn == 0x18:
                reg.sound = reg.variable[x]
            elif nn == 0x1e:
                reg.I += reg.variable[x]
                if reg.I > 0xFFF:            # CONFIGURABLE!
                    reg.variable[0xF] = 1    # chip-8 for amiga uses this
                else:                        # spacefight 2091 relies on this
                    reg.variable[0xF] = 0    #
                reg.I &= 0xFFF
            elif nn == 0x0a:
                Check_input = False
                for i in range(16):
                    if keys[i] == 1:
                        Check_input = True
                        reg.variable[x] = keys[i]
                        break
                if Check_input == False:
                    reg.pc -= 2 
            elif nn == 0x29:
                last_nibble = reg.variable[x] & 0xf
                reg.I = 0x050 + (last_nibble * 5) # font for character
            elif nn == 0x33:
                xdecimal = reg.variable[x]
                ram[reg.I] = xdecimal // 100
                ram[reg.I + 1] = ( xdecimal // 10) % 10
                ram[reg.I + 2] = xdecimal % 10
            elif n == 0x55:
                for i in range(x + 1):
                    ram[reg.I + i] = reg.variable[i]
                # reg.I += x + 1  # CONFIGURABLE! uncomment for original chop

            elif nn == 0x65:  
                for i in range(x + 1):
                    reg.variable[i] = ram[reg.I + i]
                # reg.I += x + 1  # CONFIGURABLE! uncomment for original chop
                    




def cpu_cycle(ram, reg, screen, keys) -> None:
    intruction = fetch(ram, reg)
    first,x,y,n,nn,nnn = decode(intruction)
    execute(first, x, y, n, nn, nnn, reg, ram, screen, keys)

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

KEYS = {
    pygame.K_1: 0x1, pygame.K_2: 0x2, pygame.K_3: 0x3, pygame.K_4: 0xC,
    pygame.K_q: 0x4, pygame.K_w: 0x5, pygame.K_e: 0x6, pygame.K_r: 0xD,
    pygame.K_a: 0x7, pygame.K_s: 0x8, pygame.K_d: 0x9, pygame.K_f: 0xE,
    pygame.K_z: 0xA, pygame.K_x: 0x0, pygame.K_c: 0xB, pygame.K_v: 0xF
}

def key():
    keys = [0] * 16  # CHIP-8 has 16 keys
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.KEYDOWN:
            if event.key in KEYS:
                keys[KEYS[event.key]] = 1
        elif event.type == pygame.KEYUP:
            if event.key in KEYS:
                keys[KEYS[event.key]] = 0
    return keys



def main() -> None:
    ram = memory()
    reg = registers()
    screen = [[0] * 64 for _ in range(32)] # init screen array 64x32

    pygame.init()
    SCALE = 20
    window = pygame.display.set_mode((64*SCALE,32*SCALE))
    pygame.display.set_caption("CHIP-8 Emulator")


    ch8 = "tetris.ch8"
    load(ch8, ram)

    reg.pc = 0x200

    while True:
        last_time = time.perf_counter()

        keys = key()

        cpu_cycle(ram, reg, screen, keys)

        render_screen(screen, window, SCALE)

        current_time = time.perf_counter()
        elapsed_time = current_time - last_time
        
        # reduce cpu stress while still having the accuracy of perf_counter
        if elapsed_time < INTERVAL:
            sleep = INTERVAL - elapsed_time
            if sleep > 0:
                time.sleep(sleep * 0.97) 

        while elapsed_time < INTERVAL:
            current_time = time.perf_counter()
            elapsed_time = current_time - last_time

if __name__ == "__main__":
    main()


