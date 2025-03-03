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
        
        # reduce cpu stress while still having the accuracy of perf_counter
        if elapsed_time < INTERVAL:
            sleep = INTERVAL - elapsed_time - 0.005
            if sleep > 0:
                time.sleep(sleep) 

        while elapsed_time < INTERVAL:
            current_time = time.perf_counter()
            elapsed_time = current_time - last_time

if __name__ == "__main__":
    main()


