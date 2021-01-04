import shutil, os
import time
import glob



files_in = glob.glob("C:/Users/liepe/Desktop/Projektseminar/htw/data_simulation/in_source/*.txt")
files_out = glob.glob("C:/Users/liepe/Desktop/Projektseminar/htw/data_simulation/out_source/*.txt")

i=0

while True:
    shutil.move(files_in[i], "C:/Users/liepe/Desktop/Projektseminar/htw/data_simulation/target/in_data")
    shutil.move(files_out[i], "C:/Users/liepe/Desktop/Projektseminar/htw/data_simulation/target/out_data")
    i += 1
    print(i)
    time.sleep(0.5)