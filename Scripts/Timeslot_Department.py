import mysql.connector
import random
import pandas as pd
import math
import datetime
import time

mysqldb = mysql.connector.connect(host = "localhost", user = "root", password = "@Kyogre11",  database="CSMS")	#Established connection   
mycursor = mysqldb.cursor()

'''

sql = "insert into timeslot values (%s, %s, %s, %s)"
Days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
k = 0
for i in Days:
	for j in range(0, 24):
		k = k + 1
		if(j == 23):
			tym = time.strftime('%H:%M', time.gmtime(3600 * j))
			tim = datetime.datetime.strptime(tym, '%H:%M')
			jym = time.strftime('%H:%M', time.gmtime(0))
			jim = datetime.datetime.strptime(jym, '%H:%M')
			values = (k, i, tim, jim)
			mycursor.execute(sql, values)
		else:
			tym = time.strftime('%H:%M', time.gmtime(3600 * j))
			tim = datetime.datetime.strptime(tym, '%H:%M')
			jym = time.strftime('%H:%M', time.gmtime(3600 * (j+1)))
			jim = datetime.datetime.strptime(jym, '%H:%M')
			values = (k, i, tim, jim)
			mycursor.execute(sql, values)
'''
dept = ["Cleaning", "Engine", "Security", "Supplies", "Kitchen", "Activities", "Room Service", "First Aid", "Operations", "Administration"]
sizes = [40, 20, 50, 20, 15, 5, 20, 5, 15, 10]
sql = "insert into Department values (%s, %s, %s, %s)"
j = 0
for i in dept:
	temp = random.randint(1,10) * 10000
	values = (i, 1, sizes[j], temp)
	j = j + 1
	print(values)
	mycursor.execute(sql, values)

mysqldb.commit()
mysqldb.close()