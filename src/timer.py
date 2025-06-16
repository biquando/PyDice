import os
import time
import subprocess
from main import execute_from_file

def time_execution(folder):
    files = ["alarm.dice", "evidence_1.dice", "evidence_2.dice", "grass.dice", "noisy_or.dice", "two_coins.dice"]
    for filename in os.listdir(folder):
        if filename.endswith(".dice") and filename in files:
            start = time.time()
            subprocess.run(["python3", "src/PyDice.py", os.path.join(folder, filename)], stdout=subprocess.DEVNULL) 
            end = time.time()
            print(f"{filename}: {end - start} seconds with sampling")
            start = time.time()
            subprocess.run(["python3", "src/PyDice.py", "--bdd", os.path.join(folder, filename)], stdout=subprocess.DEVNULL) 
            end = time.time()
            print(f"{filename}: {end - start} seconds without sampling")
            start = time.time()
            # maybe this should be dune exec dice
            subprocess.run(["dice",  os.path.join(folder, filename)]) 
            end = time.time()
            print(f"{filename}: {end - start} seconds with Dice")


if __name__ == "__main__":
    time_execution("benchmarks")
