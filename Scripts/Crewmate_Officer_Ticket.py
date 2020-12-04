import mysql.connector
import random
import pandas as pd
import math
import datetime
import time

mysqldb = mysql.connector.connect(host = "localhost", user = "root", password = "@Kyogre11",  database="CSMS")	#Established connection   
mycursor = mysqldb.cursor()
'''
names = pd.read_csv("C:\\Users\\HP\\Desktop\\LUMS\\2020-21 Junior Year\\Fall 2020\\CS 340\\Project\\Scripts\\baby-names.csv")
names = names["name"].to_list()

origins = pd.read_csv("C:\\Users\\HP\\Desktop\\LUMS\\2020-21 Junior Year\\Fall 2020\\CS 340\\Project\\Scripts\\countries.csv")
origins = origins["name"].to_list()
origins_len = len(origins)

name_indexer = 0
logins = []
arr = []

try:
	mycursor.execute("select ID from Login where Type = 'Crewmate'")#Execute SQL Query to select all record   
	result=mycursor.fetchall()  #fetches all the rows in a result set   
	for i in result:    
		rms=i[0]
		logins.append(rms)
except:
	print("fail")

rooms = []

try:
	mycursor.execute("select ID from Room where Package = 'Crewmate'")#Execute SQL Query to select all record   
	result=mycursor.fetchall()  #fetches all the rows in a result set   
	for i in result:    
		rms=i[0]
		rooms.append(rms)
except:
	print("fail")

sql = "insert into Crewmate values (%s, %s, %s, %s, %s, %s, %s, %s)"
room_distribute = []

for i in range(0, len(rooms)):
	for j in range(0, 2):
		room_distribute.append(rooms[i])

year = 1900000
cruise_indexer = 0
room_checker = 0
login_checker  = 0
j = 0
k = 0

for i in range(0, 800):
	cruise_indexer = (cruise_indexer + 1) % 201
	if cruise_indexer == 0:
		cruise_indexer = cruise_indexer + 1
	if i < 200:
		j = 1
	elif i < 400:
		j = 2
	elif i < 600:
		j = 3
	else:
		j = 4

	if i % 200 < 40:
		dept = "Cleaning"
	elif i % 200 < 60:
		dept = "Engine"
	elif i % 200 < 110:
		dept = "Security"
	elif i % 200 < 130:
		dept = "Supplies"
	elif i % 200 < 145:
		dept = "Kitchen"
	elif i % 200 < 150:
		dept = "Activities"
	elif i % 200 < 170:
		dept = "Room Service"
	elif i % 200 < 175:
		dept = "First Aid"
	elif i % 200 < 190:
		dept = "Operations"
	else:
		dept = "Administration"
	
	temp = random.randint(0, origins_len-1)
	values = (year+j*10000+cruise_indexer*10+2, names[name_indexer], room_distribute[room_checker], origins[temp], dept, random.randint(0,40), random.randint(0,1), logins[login_checker])
	#print(values)
	name_indexer = name_indexer + 1
	room_checker = (room_checker + 1) % 200
	login_checker = (login_checker + 1)

	mycursor.execute(sql, values)
	
year = 2000000
cruise_indexer = 1
room_checker = 0

for i in range(0, 760):
	cruise_indexer = (cruise_indexer + 1) % 191
	if cruise_indexer == 0:
		cruise_indexer = cruise_indexer + 1
	if i < 190:
		j = 1
	elif i < 380:
		j = 2
	elif i < 570:
		j = 3
	else:
		j = 4

	if i % 190 < 50:
		dept = "Security"
	elif i % 190 < 90:
		dept = "Cleaning"
	elif i % 190 < 110:
		dept = "Engine"
	elif i % 190 < 125:
		dept = "Supplies"
	elif i % 190 < 145:
		dept = "Room Service"
	elif i % 190 < 160:
		dept = "Kitchen"
	elif i % 190 < 175:
		dept = "Operations"
	elif i % 190 < 185:
		dept = "Administration"
	elif i % 190 < 186:
		dept = "First Aid"
	else:
		dept = "Activities"
	
	
	temp = random.randint(0, origins_len-1)
	values = (year+j*10000+cruise_indexer*10+2, names[name_indexer], room_distribute[room_checker], origins[temp], dept, random.randint(0,65), 1, logins[login_checker])
	#print(values)
	name_indexer = name_indexer + 1
	room_checker = (room_checker + 1) % 190
	login_checker = (login_checker + 1)

	mycursor.execute(sql, values)

mysqldb.commit()

'''

sql = "select * from Crewmate "



mysqldb.close()