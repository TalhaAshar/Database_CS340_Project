import mysql.connector

mysqldb = mysql.connector.connect(host = "localhost", user = "root", password = "@Kyogre11",  database="CSMS")	#Established connection   
mycursor = mysqldb.cursor()

list_names = []

try:
	mycursor.execute ("select distinct Login.ID from Passenger inner join Login on Passenger.Login_ID = Login.ID where Passenger.Promotional_Consent = 1")
	result = mycursor.fetchall()

	
	
	for i in result:
		temp = i
		list_names.append(temp)
	for i in range(0, len(list_names)):
		list_names[i] = str(list_names[i])
		list_names[i] = list_names[i][1:10]

except:
	print("Error")