import time
from registers import Registers
from memory import Memory
from random import randint
import pygame
import pygame_menu


def fetch(ram: int, reg: int) -> int:
    instruction = (ram[reg.pc.value] << 8) | ram[reg.pc.value + 1]
    reg.pc.value += 2
    return instruction


def decode(instruction: int) -> tuple[int, int, int, int, int, int]:
    # first nibble
    first = (instruction & 0xF000) >> 12  # 1111 0000 0000 0000

    # second nibble
    x = (instruction & 0x0F00) >> 8  # 0000 1111 0000 0000

    # third nibble
    y = (instruction & 0x00F0) >> 4  # 0000 0000 1111 0000

    # fourth nibble
    n = instruction & 0x000F  # 0000 0000 0000 1111

    nn = instruction & 0x00FF

    nnn = instruction & 0x0FFF

    return first, x, y, n, nn, nnn


def execute(first, x, y, n, nn, nnn: int, reg, ram, screen, keys):
    match first:
        case 0:
            if nn == 0xE0:  # clear screen
                for row in range(32):
                    for col in range(64):
                        screen[row][col] = 0
            elif nn == 0xEE:
                reg.pc.value = reg.pop()
        case 1:
            reg.pc.value = nnn
        case 2:
            reg.push(reg.pc.value)
            reg.pc.value = nnn
        case 3:
            if nn == reg.variable[x]:
                reg.pc.value += 2
        case 4:
            if nn != reg.variable[x]:
                reg.pc.value += 2
        case 5:
            if reg.variable[x] == reg.variable[y]:
                reg.pc.value += 2
        case 6:
            reg.variable[x] = nn
        case 7:
            result = reg.variable[x] + nn
            reg.variable[x] = result & 0xFF
        case 8:
            if n == 0:
                reg.variable[x] = reg.variable[y] & 0xFF
            elif n == 1:
                reg.variable[x] = (reg.variable[x] | reg.variable[y]) & 0xFF
            elif n == 2:
                reg.variable[x] = (reg.variable[x] & reg.variable[y]) & 0xFF
            elif n == 3:
                reg.variable[x] = (reg.variable[x] ^ reg.variable[y]) & 0xFF
            elif n == 4:
                result = (reg.variable[x] + reg.variable[y])
                if result > 255:
                    reg.variable[0xF] = 1
                else:
                    reg.variable[0xF] = 0
                reg.variable[x] = result & 0xff
            elif n == 5:
                if reg.variable[x] < reg.variable[y]:
                    reg.variable[0xF] = 0
                else:
                    reg.variable[0xF] = 1
                reg.variable[x] = (reg.variable[x] - reg.variable[y]) & 0xFF
            elif n == 6:
                reg.variable[x] = reg.variable[y] # CONFIGURABLE!
                reg.variable[0xF] = reg.variable[x] & 0x1
                reg.variable[x] >>= 1
            elif n == 7:
                if reg.variable[x] > reg.variable[y]:
                    reg.variable[0xF] = 0
                reg.variable[x] = (reg.variable[y] - reg.variable[x]) & 0xff
            elif n == 0xE:
                reg.variable[x] = reg.variable[y] # CONFIGURABLE!
                reg.variable[0xF] = (reg.variable[x] & 0x80) >> 7
                reg.variable[x] = (reg.variable[x] << 1) & 0xFF

        case 9:
            if reg.variable[x] != reg.variable[y]:
                reg.pc.value += 2
        case 0xA:
            reg.I.value = nnn
        case 0xB:
            #reg.pc.value = nnn + reg.variable[0]  # CONFIGURABLE! nnn -> xnn
            
            reg.pc.value = (x << 8) | nn + reg.variable[x]

        case 0xC:
            reg.variable[x] = randint(0, 255) & nn
        case 0xD:
            coor_x = reg.variable[x] & 63  # modulo 64 ( screen 64 pixels wide )
            coor_y = reg.variable[y] & 31  # modulo 32 ( screen 32 pixels tall )
            reg.variable[0xF] = 0  # reset flag
            for row in range(n):
                sprite_data = ram[reg.I.value + row]
                for col in range(8):
                    if (sprite_data & (0x80 >> col)) != 0:
                        screen_col = coor_x + col
                        screen_row = coor_y + row

                        if screen_col >= 64 or screen_row >= 32:
                            continue  # out of screen

                        if screen[screen_row][screen_col] == 1:  # if pixel is on
                            reg.variable[0xF] = 1  # flag

                        screen[screen_row][screen_col] ^= 1  # toggle the screen pixel
        case 0xE:
            if nn == 0x9E:
                if keys[reg.variable[x]] == 1:
                    reg.pc.value += 2
            elif nn == 0xA1:
                if keys[reg.variable[x]] == 0:
                    reg.pc.value += 2
            
        case 0xF:
            if nn == 0x07:
                reg.variable[x] = reg.delay.value & 0xFF
            elif nn == 0x15:
                reg.delay.value = reg.variable[x]
            elif nn == 0x18:
                reg.sound.value = reg.variable[x]
            elif nn == 0x1E:
                reg.I.value += reg.variable[x]
                #if reg.I.value > 0xFFF:  # CONFIGURABLE!
                #    reg.variable[0xF] = 1  # chip-8 for amiga uses this
                #else:  # spacefight 2091 relies on this
                #    reg.variable[0xF] = 0  #
            elif nn == 0x0A:
                key_pressed = False
                for i in range(16):
                    if keys[i] == 1:
                        reg.variable[x] = i
                        key_pressed = True
                        break
                if not key_pressed:
                    reg.pc.value -= 2
            elif nn == 0x29:
                last_nibble = reg.variable[x] & 0xF
                reg.I.value = 0x050 + (last_nibble * 5)  # font for character
            elif nn == 0x33:
                xdecimal = reg.variable[x]
                ram[reg.I.value] = xdecimal // 100
                ram[reg.I.value + 1] = (xdecimal // 10) % 10
                ram[reg.I.value + 2] = xdecimal % 10
            elif n == 0x55:
                for i in range(x + 1):
                    ram[reg.I.value + i] = reg.variable[i]
                reg.I.value += x + 1  # CONFIGURABLE! uncomment for original chip

            elif nn == 0x65:
                for i in range(x + 1):
                    reg.variable[i] = ram[reg.I.value + i]
                reg.I.value += x + 1  # CONFIGURABLE! uncomment for original chip


def cpu_cycle(ram, reg, screen, keys) -> None:
    instruction = fetch(ram, reg)
    first, x, y, n, nn, nnn = decode(instruction)
    execute(first, x, y, n, nn, nnn, reg, ram, screen, keys)
    print(
        f"instruction ={hex(instruction)}, I ={reg.I.value}, sp = {reg.sp.value}, pc = {reg.pc.value}"
    )


def load(ch8, ram):
    with open(ch8, "rb") as file:  # open in binary
        rom_data = file.read()  # read the file

    for i, byte in enumerate(rom_data):
        ram[0x200 + i] = byte


def render_screen(screen, window, scale, prev_screen):
    if screen == prev_screen:
        return  # skip if screen didnt change
    prev_screen[:] = [row[:] for row in screen]

    window.fill((0, 0, 0))
    for row in range(32):
        for col in range(64):
            if screen[row][col] == 1:
                pygame.draw.rect(
                    window,
                    (255, 255, 255),
                    (col * scale, row * scale, 1 * scale, 1 * scale),
                )
    pygame.display.flip()


KEYS = {
    pygame.K_1: 0x1,
    pygame.K_2: 0x2,
    pygame.K_3: 0x3,
    pygame.K_4: 0xC,
    pygame.K_a: 0x4,
    pygame.K_z: 0x5,
    pygame.K_e: 0x6,
    pygame.K_r: 0xD,
    pygame.K_q: 0x7,
    pygame.K_s: 0x8,
    pygame.K_d: 0x9,
    pygame.K_f: 0xE,
    pygame.K_w: 0xA,
    pygame.K_x: 0x0,
    pygame.K_c: 0xB,
    pygame.K_v: 0xF,
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


def start_emulation(rom_path, scale, cpu_hz, game) -> None:
    ram = Memory()
    reg = Registers()
    screen = [[0] * 64 for _ in range(32)]  # init screen array 64x32
    prev_screen = [[0] * 64 for _ in range(32)]

    pygame.init()
    # pygame.mixer.init()
    # beep = pygame.mixer.Sound("beep.wav")

    pygame.display.set_caption("CHIP8 Emulator")

    load(rom_path, ram)

    reg.sp.value = 0
    reg.pc.value = 0x200

    cpu_interval = 1 / cpu_hz
    timer_interval = 1 / 60
    last_timer_time = time.perf_counter()

    running = True

    while running:
        last_time = time.perf_counter()

        keys = key()

        cpu_cycle(ram, reg, screen, keys)

        render_screen(screen, game, scale, prev_screen)

        current_time = time.perf_counter()

        if current_time - last_timer_time >= timer_interval:
            if reg.delay.value > 0:
                reg.delay.value -= 1
            if reg.sound.value > 0:
                reg.sound.value -= 1
                # if not pygame.mixer.get_busy():
                # beep.play()
            last_timer_time = current_time

        elapsed_time = current_time - last_time

        # reduce cpu stress while still having the accuracy of perf_counter
        if elapsed_time < cpu_interval:
            sleep = cpu_interval - elapsed_time
            if sleep > 0:
                time.sleep(sleep * 0.99)

        while elapsed_time < cpu_interval:
            current_time = time.perf_counter()
            elapsed_time = current_time - last_time


def change_rom_path(value, rom_path):
    rom_path[0] = value


def change_interval(value, cpu_hz):
    cpu_hz[0] = value


def main():
    cpu_hz = [700]
    rom_path = ["roms/c8_test.c8"]
    scale = [10]

    pygame.init()
    game = pygame.display.set_mode((64 * scale[0], 32 * scale[0]))

    menu = pygame_menu.Menu(
        "CHIP-8 Emulator",
        64 * scale[0],
        32 * scale[0],
        theme=pygame_menu.themes.THEME_DEFAULT,
    )

    menu.add.selector(
        "CPU Frequency (Hz): ",
        [
            ("700 Hz", 700),
            ("900 Hz", 900),
            ("100 Hz", 100),
            ("300 Hz", 300),
            ("500 Hz", 500),
        ],
        onchange=lambda _, value: cpu_hz.__setitem__(0, value),
    )
    menu.add.text_input(
        "ROM Path: ",
        default=rom_path[0],
        onchange=lambda value: rom_path.__setitem__(0, value),
    )

    menu.add.selector(
        "Window scale: ",
        [("10", 10), ("15", 15), ("20", 20), ("25", 25), ("30", 29), ("5", 5)],
        onchange=lambda _, value: scale.__setitem__(0, value),
    )

    menu.add.button(
        "Start", lambda: start_emulation(rom_path[0], scale[0], cpu_hz[0], game)
    )

    menu.add.button("Quit", pygame_menu.events.EXIT)

    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        if menu.is_enabled():
            menu.update(events)
            menu.draw(game)

        pygame.display.flip()


if __name__ == "__main__":
    main()
