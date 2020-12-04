import mysql.connector
import random
import pandas as pd
import math
import datetime
import time

mysqldb = mysql.connector.connect(host = "localhost", user = "root", password = "@Kyogre11",  database="CSMS")	#Established connection   
mycursor = mysqldb.cursor()

countries = pd.read_csv("C:\\Users\\HP\\Desktop\\LUMS\\2020-21 Junior Year\\Fall 2020\\CS 340\\Project\\Scripts\\countries.csv")
latitude = countries["latitude"].to_list()
longitude = countries["longitude"].to_list()
name = countries["name"].to_list()



sql = "insert into location values (%s, %s, %s)"
for i in range(0, len(latitude)):
	values = (name[i], latitude[i], longitude[i])
	print(values)
	mycursor.execute(sql, values)

tmp = random.randint(0, 244)
tmp1 = random.randint(0, 244)
arr = []
dist = []
for i in range(0, 400):
	while (tmp, tmp1) in arr:
		tmp = random.randint(0, 243)
		tmp1 = random.randint(0, 243)
	arr.append((tmp, tmp1))
	dist.append(int(math.sqrt(pow(longitude[tmp1] - longitude[tmp], 2) + pow(latitude[tmp1] - latitude[tmp], 2))))
	#print(tmp, tmp1, dist[i])


sql = "insert into Route values (%s, %s, %s)"
for i in range(0, 300):
	values = (name[arr[i][0]], name[arr[i][1]], dist[i])
	mycursor.execute(sql, values)
	#print(type(name[220]))

mysqldb.commit()
mysqldb.close()
