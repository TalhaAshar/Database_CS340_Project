import mysql.connector
import random
import pandas as pd
import math
import datetime
import time

mysqldb = mysql.connector.connect(host = "localhost", user = "root", password = "@Kyogre11",  database="CSMS")	#Established connection   
mycursor = mysqldb.cursor()

df = pd.read_csv("C:\\Users\\HP\\Desktop\\LUMS\\2020-21 Junior Year\\Fall 2020\\CS 340\\Project\\Scripts\\Inventory.csv")
name = df["Name"].to_list()
Quantity_Present = df["Quantity"].to_list()
Weight = df["Weight"].to_list()
Status = df["Status"].to_list()
Description = df["Description"].to_list()
freight = df["Is_Freight"].to_list()
for i in freight:
	if i == 'FALSE':
		i = 0
	else:
		i = 1
Dept = df["Department_Name"]


sql = "insert into Inventory values (%s, %s, %s, %s, %s, %s, %s, %s)"
for i in range(0, len(name)):
	values = (i+1, name[i], Quantity_Present[i], Weight[i], Status[i], Description[i], freight[i], Dept[i])
	mycursor.execute(sql, values)
mysqldb.commit()

df_freight = pd.read_csv("C:\\Users\\HP\\Desktop\\LUMS\\2020-21 Junior Year\\Fall 2020\\CS 340\\Project\\Scripts\\Freight.csv")
Luggage = df_freight["Luggage"].to_list()
for i in Luggage:
	if i == 'FALSE':
		i = 0
	else:
		i = 1
Destination = df_freight["Destination"].to_list()

mycursor.execute('select ID from inventory where Is_Freight = 1')
result = mycursor.fetchall()
Freight_ID = []
for i in result:
	Freight_ID.append(i[0])
sql = 'insert into freight values (%s, %s, %s)'
for i in range(0, len(Freight_ID)):
	values = (Freight_ID[i], Luggage[i], Destination[i])
	mycursor.execute(sql, values)
mysqldb.commit()


mycursor.close()
mysqldb.close()

