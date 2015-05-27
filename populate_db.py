#!/usr/bin/python
import psycopg2,csv,re

#database credentials

db = "postgres"
username = "zopper"
pswrd = "zopper"
host = "127.0.0.1"
port = "5432"


#connection to database
conn = psycopg2.connect(database=db, user=username, password=pswrd, host=host, port=port)
cur = conn.cursor()

cur.execute("CREATE TABLE Devices(Id SERIAL, Name TEXT, tRange INT)")

f = open('datafile.csv')
csv_f = csv.reader(f)
count = 0
def update_db(nam,range):
    try:
        cur.execute("INSERT INTO Devices(Name,tRange) VALUES (%s,%s)",(nam,range))
    except(psycopg2.Error):
        print(psycopg2.Error.diag.message_detail)

for row in csv_f:
    if count > 2:
        if not row[1].isdigit():
            update_db(row[0],int(re.search(r'\d+', row[1]).group()))
        else:
            update_db(row[0],int(row[1]))
    else: count = count + 1

conn.commit()
conn.close()




