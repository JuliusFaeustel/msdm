import redis
from datetime import datetime 
import csv
#decode_responses, da die Rueckgabewerte von z.B. r.get(...) sonst als 'binaer' codiert
r = redis.Redis(decode_responses=True)

for a in r.scan_iter(match='*:'+str(313172)+':*',count=500000):
    print(a)
