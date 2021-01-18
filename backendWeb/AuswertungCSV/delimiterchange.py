import pandas as pd

input = pd.read_csv("takt4.txt", delimiter=r"\s+", error_bad_lines=False)
print(input)

for line in input:
    print(line[1]+","+line[2]+" "+line[3]+","+line[4])