import mysql.connector
import random
import pandas as pd
import math
import datetime
import time

mysqldb = mysql.connector.connect(host = "localhost", user = "root", password = "@Kyogre11",  database="CSMS")	#Established connection   
mycursor = mysqldb.cursor()

# ROOM INSERTIONS HERE


Package = ["Low", "Medium", "High"]
Rooms = ['First','Second','Third','Deck']
Price = [200000, 400000, 600000]

sql = "insert into room values (%s, %s, %s, %s)"
for i in range(0, 100):
	values = (i+1, "Crewmate", 0, "Ground")
	mycursor.execute(sql, values)

for i in range(100, 300):
	if i < 240:
		if i < 170:
			values = (i+1, Package[0], Price[0], Rooms[0])
		else:
			values = (i+1, Package[0], Price[0], Rooms[1])
	elif i < 280:
		values = (i+1, Package[1], Price[1], Rooms[2])
	else:
		values = (i+1, Package[2], Price[2], Rooms[3])
	mycursor.execute(sql, values)

#-----------------------------------------------------------------------------------------------------------------#


#LOGIN INSERTIONS HERE

password = "A1B2C3D4"
sql = "insert into Login values (%s, %s, %s)"
temp =  random.randint(111111111, 999999999)
arr = []
arr.append(temp)
for i in range(1, 1000):
	while temp in arr:
		temp =  random.randint(111111111, 999999999)
	arr.append(temp)

for i in range(0, 1000):
	values = (arr[i], password, "Passenger")
	mycursor.execute(sql, values)

#------------------------------------------------------------------------------------------------------------------#
'''
#INSERT PASSENGER HERE


names = pd.read_csv("C:\\Users\\HP\\Desktop\\LUMS\\2020-21 Junior Year\\Fall 2020\\CS 340\\Project\\Scripts\\baby-names.csv")
names = names["name"].to_list()
name_indexer = 0
logins = []

try:
	mycursor.execute("select ID from Login")#Execute SQL Query to select all record   
	result=mycursor.fetchall()  #fetches all the rows in a result set   
	for i in result:    
		rms=i[0]
		logins.append(rms)
except:
	print("fail")

rooms = []

try:
	mycursor.execute("select ID from Room where Package != 'Crewmate'")#Execute SQL Query to select all record   
	result=mycursor.fetchall()  #fetches all the rows in a result set   
	for i in result:    
		rms=i[0]
		rooms.append(rms)
except:
	print("fail")

sql = "insert into Passenger values (%s, %s, %s, %s, %s, %s, %s, %s)"
room_distribute = []

for i in range(0, len(rooms)):
	if i < 140:
		for j in range(0, 2):
			room_distribute.append(rooms[i])
	elif i < 180:
		for j in range(0, 3):
			room_distribute.append(rooms[i])
	else:
		for j in range(0, 5):
			room_distribute.append(rooms[i])

year = 1900000
cruise_indexer = 0
room_checker = 0
login_checker  = 0
j = 0

for i in range(0, 2000):
	cruise_indexer = (cruise_indexer + 1) % 501
	if i < 500:
		j = 1
	elif i < 1000:
		j = 2
	elif i < 1500:
		j = 3
	else:
		j = 4
	values = (year+j*10000+cruise_indexer*10+1, names[name_indexer], random.randint(10, 75), str(random.randint(1111111111111, 9999999999999)), room_distribute[room_checker], random.randint(0,1),random.randint(0,1), logins[login_checker])
	#print(values)
	name_indexer = name_indexer + 1
	room_checker = (room_checker + 1) % 500
	login_checker = (login_checker + 1) % 1000
	mycursor.execute(sql, values)

year = 2000000
cruise_indexer = 1
room_checker = 40
login_checker = 0

for i in range(0, 1000):
	if(cruise_indexer == 0):
		cruise_indexer = cruise_indexer + 1
	if i < 250:
		j = 1
	elif i < 500:
		j = 2
	elif i < 750:
		j = 3
	else:
		j = 4
	values = (year+j*10000+cruise_indexer*10+1, names[name_indexer], random.randint(10, 75), str(random.randint(1111111111111, 9999999999999)), room_distribute[room_checker], random.randint(0,1),random.randint(0,1), logins[login_checker])

	name_indexer = name_indexer + 1
	room_checker = (room_checker + 1) % 250
	login_checker = (login_checker + 1) % 1000
	cruise_indexer = (cruise_indexer + 1) % 251
	mycursor.execute(sql, values)


#----------------------------------------------------------------------------------------------------------------------------------------



mysqldb.commit()
mysqldb.close()