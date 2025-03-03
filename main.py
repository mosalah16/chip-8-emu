import time

INTERVAL = 1 / 700 

current_time = 0

def cpu_cycle() -> None:
    pass

def main() -> None:
    while True:
        last_time = time.perf_counter()
        cpu_cycle()
        current_time = time.perf_counter()
        elapsed_time = current_time - last_time
        while elapsed_time < INTERVAL:
            pass

if __name__ == "__main__":
    main()


