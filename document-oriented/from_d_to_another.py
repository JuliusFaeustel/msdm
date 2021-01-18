import shutil, os
import time
import glob



files = glob.glob("C:/Users/liepe/Desktop/Projektseminar/htw/in_source/*.txt")

print(len(files))

i=1
for filename in files:
    shutil.move(filename, "C:/Users/liepe/Desktop/Projektseminar/htw/target_in")
    print(i)
    time.sleep(10)
