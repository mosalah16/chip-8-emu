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



def cpu_cycle() -> None:
    intruction = fetch(ram ,reg)
    decode(instruction)


def main() -> None:
    ram = memory()
    reg = registers()

    while True:
        last_time = time.perf_counter()
        cpu_cycle()
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


