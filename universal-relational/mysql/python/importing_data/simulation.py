import mysql
import mysql.connector
import glob
import datetime
import inputOne
import outputOne

# alle Inputfiles aus Ordner
filesIn = glob.glob("C:/Users/picht/Desktop/Projektseminar I-490/data/htw/in/*.txt")
# alle Outputfiles aus Ordner
filesOut = glob.glob("C:/Users/picht/Desktop/Projektseminar I-490/data/htw/out/*.txt")

ZeitdateiInput = open("C:/Users/picht/Desktop/Projektseminar I-490/universell-relational/mysql/Ergebnisse/InsertZeitInput.csv","w")
ZeitdateiOutput = open("C:/Users/picht/Desktop/Projektseminar I-490/universell-relational/mysql/Ergebnisse/InsertZeitOutput.csv","w")

for number_file in range(len(filesOut)):

    if number_file < len(filesIn):
        timeIn = inputOne.insert(filesIn[number_file])
        ZeitdateiInput.write(str(timeIn) + ';\n')
    
    timeOut = outputOne.insert(filesOut[number_file])
    ZeitdateiOutput.write(str(timeOut) + ';\n')

    print(number_file)

ZeitdateiInput.close()
ZeitdateiOutput.close()