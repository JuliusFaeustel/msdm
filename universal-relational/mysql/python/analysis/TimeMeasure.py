import mysql
import mysql.connector
import datetime, time

# Vor DB-Connection-Aufbau einfügen
from time import process_time_ns
start = process_time_ns()

actualQuery = 0
actualDurationDB = 0
actualQueryDB = 0
 
def clear_DB_Log ():
    # Prozesszeit auf DB abfragen
    statement = "SELECT SUM(DURATION) FROM INFORMATION_SCHEMA.PROFILING"
    cursor.execute(statement)
    DurationDB = cursor.fetchone()

    # Anzahl der Queries abfragen
    statement = "SELECT Count(Query_ID) FROM INFORMATION_SCHEMA.PROFILING where State = 'end'"
    cursor.execute(statement)
    QueryCount = cursor.fetchone()

    statement = "SET @@profiling = 0"
    cursor.execute(statement)
    statement = "SET @@profiling_history_size = 0"
    cursor.execute(statement)
    statement = "SET @@profiling_history_size = 100;"
    cursor.execute(statement)
    statement = "SET @@profiling = 1"
    cursor.execute(statement)

    global actualDurationDB
    actualDurationDB = actualDurationDB + DurationDB[0]
    global actualQueryDB
    actualQueryDB = actualQueryDB + QueryCount[0] - 1

    global actualQuery
    actualQuery = 0

    return None

# Connection zu DB
connection = mysql.connector.connect(host = "127.0.0.1", user = "root", password = "demo", database = "project_2")
cursor = connection.cursor(buffered=True)

# Log in DB clearen
statement = "SET @@profiling = 0"
cursor.execute(statement)
statement = "SET @@profiling_history_size = 0"
cursor.execute(statement)
statement = "SET @@profiling_history_size = 10000000;"
cursor.execute(statement)
statement = "SET @@profiling = 1"
cursor.execute(statement)

# Abfragen + Skript ausführen
if actualQuery == 99:
    clear_DB_Log()
statement = "SELECT LINIE FROM LINIE ORDER BY LINIE"
cursor.execute(statement)
actualQuery = actualQuery + 1
Linie_List = cursor.fetchall()


# Prozesszeit auf DB abfragen
if actualQuery != 0:
    statement = "SELECT SUM(DURATION) FROM INFORMATION_SCHEMA.PROFILING"
    cursor.execute(statement)
    DurationDB = cursor.fetchone()

    # Anzahl der Queries abfragen
    statement = "SELECT Count(Query_ID) FROM INFORMATION_SCHEMA.PROFILING where State = 'end'"
    cursor.execute(statement)
    QueryCount = cursor.fetchone()
else:
    DurationDB = list()
    DurationDB.append(0)
    QueryCount = list()
    QueryCount.append(0)

connection.close()

# nach Verbindungsabbau einfügen
stop = process_time_ns()
DurationScript = (stop-start)/10**9
print("Durchlaufzeit Skript: "+str(DurationScript)+" s")

completeDurationDB = actualDurationDB + DurationDB[0]
completeQuery = actualQueryDB + QueryCount[0]

print("Durchlaufzeit DB: "+str(completeDurationDB)+" s")
print("Queries DB: "+str(completeQuery))
