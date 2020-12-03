import mysql
import mysql.connector
import datetime, time

# Connection zu DB
connection = mysql.connector.connect(host = "127.0.0.1", user = "root", password = "demo", database = "project_2")
cursor = connection.cursor(buffered=True)

# Ausgabe
datei = open("C:/Users/picht/Desktop/Projektseminar I-490/universell-relational/Ergebnisse/007Umrüstung/007Umrüstung.txt","w")

def convert_from_s( seconds ): 
    minutes, seconds = divmod(seconds, 60) 
    hours, minutes = divmod(minutes, 60) 
    days, hours = divmod(hours, 24) 
    string = str(int(days))+"T:"+str(int(hours))+"h:"+str(int(minutes))+"m:"+str(int(seconds))+ "s"
    return string

def find(l, elem):
    for row, i in enumerate(l):
        try:
            i.index(elem)
        except ValueError:
            continue
        return row
    return -1


# Fertigungszeiten
date_min = datetime.datetime.strptime("2100-12-31T23:59:59.000000", "%Y-%m-%dT%H:%M:%S.%f")
second_min = time.mktime(date_min.timetuple())

statement = "SELECT LINIE FROM LINIE ORDER BY LINIE"
cursor.execute(statement)
Linie_List = cursor.fetchall()

for Linie in Linie_List:
    datei.write("-------------------------------------------------------------------------------------------------------------------------------------------------------------------\n")
    datei.write("\n")
    datei.write("LINIE: "+ Linie[0])
    datei.write("\n")

    statement = "SELECT SNR.FA FROM SNR WHERE SNR.LINIE = '"+Linie[0]+"' GROUP BY FA"
    cursor.execute(statement)
    FA_List = cursor.fetchall()

    complete_list = list()
    i = 0

    for FA in FA_List:
        statement = "SELECT Ausprägung, SNR.ID, SNR.TEIL FROM SNR JOIN Objekt2Merkmalsausprägung O2MA ON (O2MA.ObjektID = SNR.ID AND o2MA.ObjektTyp = 1) JOIN Merkmalsausprägung MA ON MA.ID = O2MA.MerkmalsausprägungID WHERE MA.MerkmalID = 1 AND SNR.FA = '"+FA[0]+"' AND SNR.SNR IS NOT NULL ORDER BY Ausprägung"
        #print(statement)
        cursor.execute(statement)
        Input_List = cursor.fetchall()
        length = len(Input_List)

        complete_list.insert(i, [Input_List[0][0],Input_List[0][2],FA[0],])

        statement = "SELECT Ausprägung FROM Rückmeldung R JOIN Objekt2Merkmalsausprägung O2MA ON (O2MA.ObjektID = R.ID AND o2MA.ObjektTyp = 2) JOIN Merkmalsausprägung MA ON MA.ID = O2MA.MerkmalsausprägungID WHERE MA.MerkmalID = 39 AND R.SNR_ID = '"+str(Input_List[length-1][1])+"' ORDER BY Ausprägung DESC"
        cursor.execute(statement)
        OutputDate = cursor.fetchone()
        
        if not OutputDate:
            #print(statement)
            complete_list[i].append('NULL')
            i = i + 1
            continue
        else:
            complete_list[i].append(OutputDate[0])
        #print(complete_list)

        i = i + 1
    
    complete_list.sort()
    #print(complete_list)

    erg_list = list()

    for j in range(0, (len(complete_list)-1)):
        #print(len(complete_list))
        #print("J"+str(j))

        if complete_list[j][3] == 'NULL':
            diff = -1
        else:
            DateOutPrev = complete_list[j][3]
            #print(DateOutPrev)
            DateOutPrev_time = datetime.datetime.strptime(DateOutPrev[0:-1], "%Y-%m-%dT%H:%M:%S.%f")
            DateOutPrev_seconds = time.mktime(DateOutPrev_time.timetuple())

            DateInFoll = complete_list[j+1][0]
            #print(DateInFoll)
            DateInFoll_time = datetime.datetime.strptime(DateInFoll[0:-1], "%Y-%m-%dT%H:%M:%S.%f")
            DateInFoll_seconds = time.mktime(DateInFoll_time.timetuple())

            diff = DateInFoll_seconds - DateOutPrev_seconds
            #print(diff)

        if diff >= 0:
            pair = complete_list[j][1] + complete_list[j+1][1]
            index = find(erg_list, pair)
            if index == -1:
                position = len(erg_list)
                erg_list.insert(position, [pair, diff, diff, diff, 1])
            else:
                minTime = erg_list[index][1]
                maxTime = erg_list[index][2]
                avgTime = erg_list[index][3]
                count = erg_list[index][4]
                if minTime > diff:
                    erg_list[index][1] = diff
                if maxTime < diff:
                    erg_list[index][2] = diff
                avgTime = avgTime + diff
                count = count + 1
                erg_list[index][3] = avgTime
                erg_list[index][4] = count
    
    erg_list.sort()
    for erg in erg_list:
        avg = erg[3]/erg[4]
        datei.write("Von: " +erg[0][0]+"    Nach: "+erg[0][1]+"          MIN: "+convert_from_s(erg[1])+"         MAX: "+convert_from_s(erg[2])+"         AVG: "+convert_from_s(avg)+"\n")

datei.close()