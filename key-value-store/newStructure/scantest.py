import redis
from datetime import datetime
import csv
#decode_responses, da die Rueckgabewerte von z.B. r.get(...) sonst als 'binaer' codiert
r = redis.Redis(decode_responses=True)

allCons = r.lrange("con",0,-1)
print("Cons geladen")

#print(r.smembers("TEIL"))
#print(r.bitcount("TEIL:A"))
#r.bitop("AND","opCon","FA:009004","TEIL:A")
#print(r.bitcount("opCon"))

allPos = []

pos = r.bitpos("FA:009004",1)
while not pos == -1:
    allPos.append(pos)
    pos = r.bitpos("FA:009004",1,int(pos/8)+1)
    print(pos)
print(allPos)
#conn = allCons[pos-1]
#dats = r.lrange(conn,0,-1)
#print(r.hgetall(dats[0]))


