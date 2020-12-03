import mysql
import mysql.connector
import datetime, time

# Connection zu DB
connection = mysql.connector.connect(host = "127.0.0.1", user = "root", password = "demo", database = "project_2")
cursor = connection.cursor(buffered=True)

def convert_from_s( seconds ): 
    minutes, seconds = divmod(seconds, 60) 
    hours, minutes = divmod(minutes, 60) 
    days, hours = divmod(hours, 24) 
    string = str(int(days))+"T:"+str(int(hours))+"h:"+str(int(minutes))+"m:"+str(int(seconds))+ "s"
    return string


# Fertigungszeiten
date_min = datetime.datetime.strptime("2100-12-31T23:59:59.000000", "%Y-%m-%dT%H:%M:%S.%f")
second_min = time.mktime(date_min.timetuple())

statement = "SELECT Ausprägung FROM Merkmalsausprägung WHERE MerkmalID = 21 ORDER BY Ausprägung"
cursor.execute(statement)
LagerIn_List = cursor.fetchall()

Dauer = 0
Anzahl = 0

for LagerIn in LagerIn_List:
    statement = "SELECT COUNT(*) FROM (SELECT SNR.ID FROM SNR JOIN Objekt2Merkmalsausprägung O2MA ON (O2MA.ObjektID = SNR.ID AND o2MA.ObjektTyp = 1) JOIN Merkmalsausprägung MA ON MA.ID = O2MA.MerkmalsausprägungID WHERE MA.Ausprägung = '"+LagerIn[0]+"' AND MA.MerkmalID = 21 GROUP BY SNR) Q"
    cursor.execute(statement)
    Anzahl = cursor.fetchone()

    statement = "SELECT SNR.ID FROM SNR JOIN Objekt2Merkmalsausprägung O2MA ON (O2MA.ObjektID = SNR.ID AND o2MA.ObjektTyp = 1) JOIN Merkmalsausprägung MA ON MA.ID = O2MA.MerkmalsausprägungID WHERE MA.Ausprägung = '"+LagerIn[0]+"' AND MA.MerkmalID = 21"
    cursor.execute(statement)
    Input_List = cursor.fetchall()

    minInput = second_min
    minInputDate = ''
    maxOutput = 0
    maxOutputDate = ''

    for InputID in Input_List:
        statement = "SELECT Ausprägung FROM SNR JOIN Objekt2Merkmalsausprägung O2MA ON (O2MA.ObjektID = SNR.ID AND o2MA.ObjektTyp = 1) JOIN Merkmalsausprägung MA ON MA.ID = O2MA.MerkmalsausprägungID WHERE SNR.ID = '"+str(InputID[0])+"' AND MA.MerkmalID = 1"
        cursor.execute(statement)
        DateInput = cursor.fetchone()

        DateInput_time = datetime.datetime.strptime(DateInput[0][0:-1], "%Y-%m-%dT%H:%M:%S.%f")
        DateInput_seconds = time.mktime(DateInput_time.timetuple())

        if DateInput_seconds < minInput:
            minInput = DateInput_seconds
            minInputDate = DateInput_time

        statement = "SELECT R.ID FROM Rückmeldung R WHERE R.SNR_ID = "+str(InputID[0])
        cursor.execute(statement)
        Output_List = cursor.fetchall()

        for OutputID in Output_List:
            statement = "SELECT Ausprägung FROM Rückmeldung R JOIN Objekt2Merkmalsausprägung O2MA ON (O2MA.ObjektID = R.ID AND o2MA.ObjektTyp = 2) JOIN Merkmalsausprägung MA ON MA.ID = O2MA.MerkmalsausprägungID WHERE R.ID = '"+str(OutputID[0])+"' AND MA.MerkmalID = 39"
            cursor.execute(statement)
            DateOutput = cursor.fetchone()

            if not DateOutput:
                continue

            DateOutput_time = datetime.datetime.strptime(DateOutput[0][0:-1], "%Y-%m-%dT%H:%M:%S.%f")
            DateOutput_seconds = time.mktime(DateOutput_time.timetuple())

            if DateOutput_seconds > maxOutput:
                maxOutput = DateOutput_seconds
                maxOutputDate = DateOutput_time
    
    
    Dauer = maxOutput - minInput

    print("Ladungsträger: "+LagerIn[0]+"        Anzahl: "+str(Anzahl[0])+"        Dauer: "+convert_from_s(Dauer)+"        Start: "+minInputDate.strftime("%Y-%m-%dT%H:%M:%S")+"         Ende: "+maxOutputDate.strftime("%Y-%m-%dT%H:%M:%S"))



        


    