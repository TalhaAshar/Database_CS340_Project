from flask import Flask, render_template, json, request
from flaskext.mysql import MySQL
from json import dumps

mysql = MySQL()
app = Flask(__name__)

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '@Kyogre11'
app.config['MYSQL_DATABASE_DB'] = 'CSMS'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

@app.route("/")
def main():
    return render_template('index.html')

@app.route('/verifiedLogin', methods=['POST', 'GET'])
def verifiedLogin():
	try:
		mysqldb = mysql.connect()
		mycursor = mysqldb.cursor()
		temp = request.form
		_UserType = 'None'
		if temp.get('passenger'):
			print('true')
			_UserType = 'Passenger'
		elif temp.get('crewmate'):
			_UserType = 'Crewmate'
		elif temp.get('offshore'):
			_UserType = 'Offshore_Management'

		if _UserType == 'None':
			return render_template('error.html', error='You did not select an account type.')
		UserID = temp['User-ID']
		Password = temp['Password']

		sql = "select * from Login where ID = (%s) and Password = (%s) and Type = (%s)"
		values = (UserID, Password, _UserType)
		mycursor.execute(sql, values)
		result = mycursor.fetchall()

		if not result:
			return render_template('error.html', error='The given username and password do not match for your type of account')
		if(_UserType == 'Passenger'):
			sql = "select Name, Age, CNIC, Disability, Promotional_Consent from Passenger where Login_ID = (%s) order by ID desc"
			values = (UserID)
			mycursor.execute(sql, values)
			result = mycursor.fetchall()
			Name = result[0][0]
			Age = result[0][1]
			CNIC = result[0][2]
			Disability = result[0][3]
			Promo = result[0][4]
			mycursor.close()
			mysqldb.close()
			#print(Name, Age, CNIC, Disability, Promo, UserID)
			flag = 0
			try:
				fileHandle = open("templates\\promo.txt", "r")
				arr = fileHandle.read()
				arr = arr.split(" ")
				if UserID in arr:
					flag = 1
					fileHandle = open('templates\\promo.txt', "w")
					for i in arr:
						if UserID != i:
							fileHandle.write(str(i) + " ")
					fileHandle.close()
			except:
				flag = 0


			return render_template('passengerHome.html', username=UserID, CNIC=CNIC, name=Name, age=Age, disability=Disability, promo=Promo, flag=flag)
		#return render_template('passengerBooking.html', username=UserID, CNIC=CNIC, name=Name, age=Age, disability=Disability, promo=Promo)
		elif _UserType == 'Crewmate':
			sql = "select name, origin, dept_name, Experience, status from crewmate where Login_ID = (%s)"
			values = (UserID)
			mycursor.execute(sql, values)
			result = mycursor.fetchall()
			Name = result[0][0]
			Origin = result[0][1]
			Dept_Name = result[0][2]
			Experience = result[0][3]
			Status = result[0][4]

			mycursor.close()
			mysqldb.close()
			return render_template('crewmateGenericHome.html', username=UserID, name=Name, origin=Origin, dept=Dept_Name, exp=Experience, status=Status)
		elif _UserType == 'Offshore_Management':
			mycursor.close()
			mysqldb.close()
			return render_template('offshoreHome.html', username=UserID)
		
	except Exception as e:
		return render_template('error.html', error=e)
	


@app.route('/signUpForm')
def signUpForm():
    return render_template('signup.html')

@app.route('/validateTravelAgent', methods=['POST','GET'])
def validateTravelAgent():
	try:
		UserID = request.form['User-ID']
		Password = request.form['Password']
		UserType = 'Offshore_Management'
		mysqldb = mysql.connect()
		mycursor = mysqldb.cursor()

		sql = "select * from Login where ID = (%s) and Password = (%s) and Type = (%s)"
		values = (UserID, Password, UserType)
		mycursor.execute(sql, values)
		result = mycursor.fetchall()

		if not result:
			return render_template('error.html', error='The given username and password do not match for your type of account')
	except Exception as e:
		return render_template('error.html', error=e)
	finally:
		mycursor.close()
		mysqldb.close()

	return render_template('newPassengerInter.html')


@app.route('/committingPassenger_LoginInter', methods=['POST', 'GET'])
def committingPassenger_LoginInter():
	try:
		Year = request.form['Date'][2:4]
		Quarter = request.form['Quarter']
		cruise = Year+Quarter


		mysqldb = mysql.connect()
		mycursor = mysqldb.cursor()

		sql = "select ID, Package, Price from Room where Package != (%s)"
		values = ('Crewmate')
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		Rooms = []
		for i in result:
			Rooms.append(i)
		
		sql = "select Room_ID, count(Room_ID) from Passenger where ID like (%s) group by Room_ID"
		values = (cruise + '___1')
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		InvalidRooms = []
		for i in result:
			if int(i[0]) <= 240:
				if int(i[1]) >= 3:
					InvalidRooms.append(i[0])
			elif int(i[0]) <= 280:
				if int(i[1]) >= 4:
					InvalidRooms.append(i[0])
			elif int(i[0]) <= 300:
				if int(i[1]) >= 5:
					InvalidRooms.append(i[0])
		
		FinalRooms = []
		for i in Rooms:
			if i[0] not in InvalidRooms:
				FinalRooms.append(i)

	except Exception as e:
		return render_template('error.html', error=e)

	#print(UserID, CNIC, Name, Age, Disable, Promo)

	return render_template('newPassenger.html', year = request.form['Date'], quarter = Quarter, tables = FinalRooms)



@app.route('/committingPassenger_Login', methods=['POST', 'GET'])
def committingPassenger_Login():
	try:
		mysqldb = mysql.connect()
		mycursor = mysqldb.cursor()
		temp = request.form
		_CNIC = temp["CNIC"]
		_Room = temp['Room_ID']
		_Username = temp['User-ID']
		_Year = temp['Date'][2:4]
		_Quarter = temp['Quarter']

		_Password = temp['Password']
		_Name = temp['Name']
		_Age = temp['Age']
		_Disable = 0
		_Promo = 0
		if temp.get('disability'):
			_Disable = 1
		if temp.get('promo_campaign'):
			_Promo = 1
		_cruise = _Year+_Quarter


		mycursor.execute("select distinct CNIC from Passenger")
		_result = mycursor.fetchall()
		_registered = []
		
		for i in _result:    
			rms=i[0]
			_registered.append(rms)

		if _CNIC in _registered:
			return render_template('error.html', error ='Your input CNIC is registered with another Passenger.')

		mycursor.execute("select ID from Room")
		_result = mycursor.fetchall()
		_registered = []
		
		for i in _result:    
			rms=i[0]
			_registered.append(rms)
		#print(_registered)

		if int(_Room) not in _registered:
			return render_template('error.html', error ='The given room does not exist.')

		if(int(_Room) <= 100):
			return render_template('error.html', error='The given room is not assigned to you.')


		sql = "select ID from Passenger where Room_ID = (%s)"
		values = (_Room)
		mycursor.execute(sql, values)

		_result = mycursor.fetchall()
		_registered = []
		
		for i in _result:    
			rms=i[0]
			_registered.append(rms)
		
		curr_num = 0
		for i in range(0, len(_registered)):
			if(int(_registered[i] / 10000) == int(_cruise)):
				curr_num = curr_num + 1
				if int(_Room) <= 240:
					if curr_num >= 3:
						return render_template('error.html', error ='The given room is already full.')
				elif int(_Room) <= 280:
					if curr_num >= 4:
						return render_template('error.html', error ='The given room is already full.')
				else:
					if curr_num >= 5:
						return render_template('error.html', error ='The given room is already full.')

		sql = "select count(*) from Login where ID = (%s)"
		values = (_Username)
		mycursor.execute(sql, values)

		_result = mycursor.fetchall()
		if (_result[0][0]) > 0:
			return render_template('error.html', error ='This username is already assigned to another user.')

		sql = "select count(*) from passenger where ID like (%s)"
		values = _cruise + '___1'
		mycursor.execute(sql, values)
		_result = mycursor.fetchall()

		print("here")

		if (_result[0][0] == 680):
			return render_template('error.html', error ='The Quarter for the Cruise you have selected is at capacity.')


		sql = "select ID from passenger where ID like (%s) order by ID desc limit 1"
		values = _cruise + '____'
		mycursor.execute(sql, values)
		_result = mycursor.fetchall()


		sql = "insert into Login values (%s, %s, %s)"
		values = (_Username, _Password, 'Passenger')
		mycursor.execute(sql, values)

		new_id = 0
		print(mycursor.rowcount)
		if _result:
			new_id = int(_cruise) * 10000 + (int(str(_result[0][0])[3:6]) + 1) * 10 + 1
			
		else:
			new_id = _cruise + '0011'
			print("nein")
		print("wein")
		sql = "insert into Passenger values (%s, %s, %s, %s, %s, %s, %s, %s)"
		values = (new_id, _Name, int(_Age), _CNIC, _Room, int(_Disable), int(_Promo), _Username)
		mycursor.execute(sql, values)
		print(values)
		mysqldb.commit()

		sql = "select Package, Price from Room where ID = (%s)"
		values = (_Room)
		mycursor.execute(sql, values)
		_result = mycursor.fetchall()
		_package = _result[0][0]
		_price = str(_result[0][1])
		if _Disable == 0:
			_Disable = 'False' 
		else:
			_Disable = 'True'
		if _Promo == 0:
			_Promo = 'False'
		else:
			_Promo = 'True'

	except Exception as e:
		return render_template('error.html', error=e)

	finally:
		mycursor.close() 
		mysqldb.close()

	return render_template('bookingReceipt.html', name=_Name, cnic=_CNIC, age=_Age, room= _Room, pack=_package, price=_price, disabled=_Disable, promo=_Promo,date=temp['Date'], quarter=_Quarter, user=_Username, type='Booking Receipt')

@app.route('/returnHome')
def returnHome():
    return render_template('index.html')

@app.route('/bookingIntermediate', methods=['POST', 'GET'])
def bookingIntermediate():
	try:
		UserID = request.form['userBook']
		CNIC = request.form['CNICBook']
		Name = request.form['NameBook']
		Age = request.form['AgeBook']
		Disable = request.form['disabilityBook']
		Promo = request.form['promo_campaignBook']
	except:
		print("none")

	print(UserID, CNIC, Name, Age, Disable, Promo)

	return render_template('passengerBookingInter.html', username=UserID, CNIC=CNIC, name=Name, age=Age, disability=Disable, promo=Promo)

@app.route('/bookingPassengerRoomInter', methods=['POST', 'GET'])
def bookingPassengerRoomInter():
	try:
		UserID = request.form['user']
		CNIC = request.form['CNIC']
		Name = request.form['Name']
		Age = request.form['Age']
		Disable = request.form['disability']
		Promo = request.form['promo_campaign']
		Year = request.form['Date'][2:4]
		Quarter = request.form['Quarter']
		cruise = Year+Quarter


		mysqldb = mysql.connect()
		mycursor = mysqldb.cursor()

		sql = "select ID, Package, Price from Room where Package != (%s)"
		values = ('Crewmate')
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		Rooms = []
		for i in result:
			Rooms.append(i)
		
		sql = "select Room_ID, count(Room_ID) from Passenger where ID like (%s) group by Room_ID"
		values = (cruise + '___1')
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		InvalidRooms = []
		for i in result:
			if int(i[0]) <= 240:
				if int(i[1]) >= 3:
					InvalidRooms.append(i[0])
			elif int(i[0]) <= 280:
				if int(i[1]) >= 4:
					InvalidRooms.append(i[0])
			elif int(i[0]) <= 300:
				if int(i[1]) >= 5:
					InvalidRooms.append(i[0])
		
		FinalRooms = []
		for i in Rooms:
			if i[0] not in InvalidRooms:
				FinalRooms.append(i)

	except Exception as e:
		return render_template('error.html', error=e)

	#print(UserID, CNIC, Name, Age, Disable, Promo)

	return render_template('passengerBooking.html', username=UserID, CNIC=CNIC, name=Name, age=Age, disability=Disable, promo=Promo, year = request.form['Date'], quarter = Quarter, tables = FinalRooms)


@app.route('/bookingPassengerRoom', methods=['POST', 'GET'])
def bookingPassengerRoom():
	try:
		mysqldb = mysql.connect()
		mycursor = mysqldb.cursor()
		UserID = request.form['user']
		CNIC = request.form['CNIC']
		Room = request.form['Room_ID']
		Year = request.form['Date'][2:4]
		Quarter = request.form['Quarter']
		

		Name = request.form['Name']
		Age = request.form['Age']
		Disable = request.form['disability']
		Promo = request.form['promo_campaign']
		cruise = Year+Quarter

		mycursor.execute("select ID from Room")
		result = mycursor.fetchall()
		registered = []
		
		for i in result:    
			rms=i[0]
			registered.append(rms)

		if int(Room) not in registered:
			return render_template('error.html', error ='The given room does not exist.')

		if(int(Room) <= 100):
			return render_template('error.html', error='The given room is not assigned to you.')

		sql = "select ID from Passenger where Room_ID = (%s)"
		values = (Room)
		mycursor.execute(sql, values)

		result = mycursor.fetchall()
		registered = []

		for i in result:    
			rms=i[0]
			registered.append(rms)
		
		curr_num = 0
		for i in range(0, len(registered)):
			if(int(registered[i] / 10000) == int(cruise)):
				curr_num = curr_num + 1
				if int(Room) <= 240:
					if curr_num >= 3:
						return render_template('error.html', error ='The given room is already full.')
				elif int(Room) <= 280:
					if curr_num >= 4:
						return render_template('error.html', error ='The given room is already full.')
				else:
					if curr_num >= 5:
						return render_template('error.html', error ='The given room is already full.')

		sql = "select count(*) from passenger where ID like (%s)"
		values = cruise + '___1'
		mycursor.execute(sql, values)
		result = mycursor.fetchall()

		if (result[0][0] == 680):
			return render_template('error.html', error ='The Quarter for the Cruise you have selected is at capacity.')

		sql = "select ID from passenger where ID like (%s) order by ID desc limit 1"
		values = cruise + '____'
		mycursor.execute(sql, values)
		result = mycursor.fetchall()

		new_id = 0
		if result:
			new_id = int(cruise) * 10000 + (int(str(result[0][0])[3:6]) + 1) * 10 + 1
		else:
			new_id = cruise + '0011'
			

		if Promo == '1':
			Promo = 1
		else:
			Promo = 0

		sql = "insert into Passenger values (%s, %s, %s, %s, %s, %s, %s, %s)"
		values = (new_id, Name, Age, CNIC, Room, Disable, Promo, UserID)
		print(values)
		mycursor.execute(sql, values)
		
		mysqldb.commit()

		sql = "select Package, Price from Room where ID = (%s)"
		values = (Room)
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		package = result[0][0]
		price = str(result[0][1])
	except Exception as e:
		return render_template('error.html', error=e)

	finally:
		mycursor.close() 
		mysqldb.close()

	if Promo == 1:
		Promo = 'True'
	else:
		Promo = 'False'
	if Disable == '1':
		Disable = 'True'
	else:
		Disable = 'False'

	return render_template('bookingReceipt.html', type='Booking Receipt' ,name=Name, cnic=CNIC, age=Age, room= Room, pack=package, price=price, disabled=Disable, promo=Promo,date=request.form['Date'], quarter=Quarter, user=UserID)
	

@app.route('/deleteIntermediate', methods=['POST', 'GET'])
def deleteIntermediate():
	print("in del")
	UserID = request.form['userDel']
	CNIC = request.form['CNICDel']
	Name = request.form['NameDel']
	Age = request.form['AgeDel']
	Disable = request.form['disabilityDel']
	Promo = request.form['promo_campaignDel']

	print(UserID, CNIC, Name, Age, Disable, Promo)

	return render_template('passengerCancellationInter.html', username=UserID, CNIC=CNIC, name=Name, age=Age, disability=Disable, promo=Promo)

@app.route('/deletingPassengerRoomInter', methods=['POST', 'GET'])
def deletingPassengerRoomInter():
	try:
		UserID = request.form['user']
		CNIC = request.form['CNIC']
		Name = request.form['Name']
		Age = request.form['Age']
		Disable = request.form['disability']
		Promo = request.form['promo_campaign']
		Year = request.form['Date'][2:4]
		Quarter = request.form['Quarter']
		cruise = Year+Quarter


		mysqldb = mysql.connect()
		mycursor = mysqldb.cursor()

		sql = "select Room.ID, Room.Package, Room.Price from Room inner join Passenger on Room.ID = Passenger.Room_ID where Passenger.Login_ID = (%s) and  Passenger.ID like (%s) order by Room.ID asc"
		values = (UserID, cruise + '___1')
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		myRooms = []
		for i in result:
			myRooms.append(i)


	except Exception as e:
		return render_template('error.html', error=e)

	#print(UserID, CNIC, Name, Age, Disable, Promo)

	return render_template('passengerCancellation.html', username=UserID, CNIC=CNIC, name=Name, age=Age, disability=Disable, promo=Promo, year = request.form['Date'], quarter = Quarter, tables = myRooms)



@app.route('/deletingPassengerRoom', methods=['POST', 'GET'])
def deletingPassengerRoom():
	try:
		mysqldb = mysql.connect()
		mycursor = mysqldb.cursor()
		UserID = request.form['user']
		CNIC = request.form['CNIC']
		Room = request.form['Room_ID']
		Year = request.form['Date'][2:4]
		Quarter = request.form['Quarter']

		Name = request.form['Name']
		Age = request.form['Age']
		Disable = request.form['disability']
		Promo = request.form['promo_campaign']
		cruise = Year+Quarter

		mycursor.execute("select ID from Room")
		result = mycursor.fetchall()
		registered = []
		
		for i in result:    
			rms=i[0]
			registered.append(rms)

		if int(Room) not in registered:
			return render_template('error.html', error ='The given room does not exist.')

		sql = "select ID from Passenger where Room_ID = (%s) and ID like (%s) and Login_ID = (%s)"
		values = (Room, cruise + '___1', UserID)
		mycursor.execute(sql, values)
		result = mycursor.fetchall()

		if not result:
			return render_template('error.html', error ='You do not have any reservations for this room for the cruise quarter input.')			

		
		num = []
		for i in result:
			num.append(i[0])

		sql = "select Package, Price from Room where ID = (%s)"
		values = (Room)
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		package = result[0][0]
		price = str(-result[0][1])
		
		sql = "update Passenger set ID = (%s) where ID = (%s)"
		for i in num:
			values = (int(i)-1, i)
			mycursor.execute(sql, values)
			break
		mysqldb.commit()
	except Exception as e:
		return render_template('error.html', error=e)
	finally:
		mycursor.close()
		mysqldb.close()

	disableStr = 'False'
	promoStr = 'False'

	if Disable == '1':
		disableStr = 'True'
	if Promo == '1':
		promoStr = 'True'
	return render_template('bookingReceipt.html', type='Cancellation Receipt', name=Name, cnic=CNIC, age=Age, room= Room, pack=package, price=price, disabled=disableStr, promo=promoStr,date=request.form['Date'], quarter=Quarter, user=UserID)

@app.route('/upgradeIntermediate', methods=['POST', 'GET'])
def upgradeIntermediate():
	UserID = request.form['userUPG']
	CNIC = request.form['CNICUPG']
	Name = request.form['NameUPG']
	Age = request.form['AgeUPG']
	Disable = request.form['disabilityUPG']
	Promo = request.form['promo_campaignUPG']

	print(UserID, CNIC, Name, Age, Disable, Promo)

	return render_template('passengerUpgradeInter.html', username=UserID, CNIC=CNIC, name=Name, age=Age, disability=Disable, promo=Promo)


@app.route('/upgradingPassengerRoomInter', methods=['POST','GET'])
def upgradingPassengerRoomInter():
	try:
		UserID = request.form['user']
		CNIC = request.form['CNIC']
		Name = request.form['Name']
		Age = request.form['Age']
		Disable = request.form['disability']
		Promo = request.form['promo_campaign']
		Year = request.form['Date'][2:4]
		Quarter = request.form['Quarter']
		cruise = Year+Quarter


		mysqldb = mysql.connect()
		mycursor = mysqldb.cursor()

		sql = "select ID, Package, Price from Room where Package != (%s)"
		values = ('Crewmate')
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		Rooms = []
		for i in result:
			Rooms.append(i)
		
		sql = "select Room_ID, count(Room_ID) from Passenger where ID like (%s) group by Room_ID"
		values = (cruise + '___1')
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		InvalidRooms = []
		for i in result:
			if int(i[0]) <= 240:
				if int(i[1]) >= 3:
					InvalidRooms.append(i[0])
			elif int(i[0]) <= 280:
				if int(i[1]) >= 4:
					InvalidRooms.append(i[0])
			elif int(i[0]) <= 300:
				if int(i[1]) >= 5:
					InvalidRooms.append(i[0])
		
		FinalRooms = []
		for i in Rooms:
			if i[0] not in InvalidRooms:
				FinalRooms.append(i)

		sql = "select Room.ID, Room.Package, Room.Price from Room inner join Passenger on Room.ID = Passenger.Room_ID where Passenger.Login_ID = (%s) and  Passenger.ID like (%s) order by Room.ID asc"
		values = (UserID, cruise + '___1')
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		myRooms = []
		for i in result:
			myRooms.append(i)


	except Exception as e:
		return render_template('error.html', error=e)

	#print(UserID, CNIC, Name, Age, Disable, Promo)

	return render_template('passengerUpgrade.html', username=UserID, CNIC=CNIC, name=Name, age=Age, disability=Disable, promo=Promo, year = request.form['Date'], quarter = Quarter, tables = FinalRooms, current=myRooms)


@app.route('/upgradingPassengerRoom', methods=['POST', 'GET'])
def upgradingPassengerRoom():
	try:
		mysqldb = mysql.connect()
		mycursor = mysqldb.cursor()
		UserID = request.form['user']
		CNIC = request.form['CNIC']
		Room = request.form['Room_ID']
		NewRoom = request.form['NewRoom_ID']
		Year = request.form['Date'][2:4]
		Quarter = request.form['Quarter']

		Name = request.form['Name']
		Age = request.form['Age']
		Disable = request.form['disability']
		Promo = request.form['promo_campaign']
		cruise = Year+Quarter

		mycursor.execute("select ID from Room")
		result = mycursor.fetchall()
		registered = []
		
		for i in result:    
			rms=i[0]
			registered.append(rms)

		if int(Room) not in registered or int(NewRoom) not in registered:
			return render_template('error.html', error ='One of the given rooms does not exist.')

		if int(Room) <= 100:
			return render_template('error.html', error='The given room is not assigned to you.')

		sql = "select ID from Passenger where Room_ID = (%s) and ID like (%s) and Login_ID = (%s)"
		values = (Room, cruise + '___1', UserID)
		print(values)
		mycursor.execute(sql, values)
		result = mycursor.fetchall()

		if not result:
			return render_template('error.html', error ='You do not have any reservations for this room for the cruise quarter input.')			
	
		myID = result[0][0]
		sql = "select Package, Price from Room where ID = (%s)"
		values = (Room)
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		CurrentPackage = result[0][0]
		CurrentPrice = result[0][1]

		Package = ''
		NewPrice = 0
		if int(NewRoom) <= 240:
			Package = 'Low'
			NewPrice = 200000
		elif int(NewRoom) <= 280:
			Package = 'Medium'
			NewPrice = 400000
		else:
			Package = 'High'
			NewPrice = 600000

		if CurrentPackage == 'High':
			return render_template('error.html', error='You cannot upgrade from a "High" Package.')

		if Package == 'Low':
			return render_template('error.html', error='You cannot upgrade to a "Low" Package.')			

		if CurrentPackage == 'Medium' and Package == 'Medium':
			return render_template('error.html', error='You cannot upgrade to a room of the same package.')

		sql = "select ID from Passenger where Room_ID = (%s) and ID like (%s) and Login_ID = (%s)"
		values = (NewRoom, cruise + '___1', UserID)
		mycursor.execute(sql, values)
		result = mycursor.fetchall()

		if int(NewRoom) <= 280:
			if mycursor.rowcount == 4:
				return render_template('error.html', error='Your desired room is at capacity.')	
		elif int(NewRoom) <= 300:
			if mycursor.rowcount == 5:
				return render_template('error.html', error='Your desired room is at capacity.')	

		finalPrice = NewPrice - int(CurrentPrice)

		sql = "update Passenger set Room_ID = (%s) where ID = (%s) and Login_ID = (%s)"
		values = (NewRoom, myID, UserID)							
		mycursor.execute(sql, values)
		mysqldb.commit()
	except Exception as e:
		return render_template('error.html', error=e)
	finally:
		mycursor.close()
		mysqldb.close()
	disableStr = 'False'
	promoStr = 'False'

	if Disable == '1':
		disableStr = 'True'
	if Promo == '1':
		promoStr = 'True'
	return render_template('bookingReceipt.html', type='Upgrade Receipt', name=Name, cnic=CNIC, age=Age, room= NewRoom, pack=Package, price=finalPrice, disabled=disableStr, promo=promoStr,date=request.form['Date'], quarter=Quarter, user=UserID)

@app.route('/viewIntermediate', methods=['POST', 'GET'])
def viewIntermediate():
	UserID = request.form['userView']
	print(UserID)
	Name = request.form['NameView']
	try:
		mysqldb = mysql.connect()
		mycursor = mysqldb.cursor()
		sql = "select Passenger.ID, Room.ID, Package, Price from Passenger inner join Room on Room.ID = Passenger.Room_ID where Login_ID = (%s) and Passenger.ID like (%s) order by Room.ID"
		values = (UserID, '%1')
		mycursor.execute(sql,values)
		query = mycursor.fetchall()
		result = []
		for i in query:
			result.append(i)
		print(result)
	except Exception as e:
		return render_template('error.html', error=e)
	finally:
		mycursor.close()
		mysqldb.close()
	return render_template('viewBookings.html', username = UserID, name = Name, type = 'View Bookings', data=result)

@app.route('/promotionalCampaign')
def promotionalCampaign():
	try:
		mysqldb = mysql.connect()
		mycursor = mysqldb.cursor()
		sql = "select distinct Login_ID from Passenger where Promotional_Consent = (%s)"
		values = ('1')
		mycursor.execute(sql, values)
		result = mycursor.fetchall()

		if not result:
			return render_template('error.html', error= 'No exisiting passengers have subscribed to promotions.')

		names = []
		for i in result:
			names.append(i[0])
		#print(names)

		fileHandle = open('templates\\promo.txt', "w")
		for i in names:
			fileHandle.write(str(i) + " ")
		fileHandle.close()

	except Exception as e:
		return render_template('error.html', error=e)
	finally:
		mycursor.close()
		mysqldb.close()
	return render_template('confirm.html', result = 'Your Transaction Has Been Completed.')

@app.route('/crewmateBookChoice', methods=['POST', 'GET'])
def crewmateBookChoice():
	return render_template('crewmateBookChoice.html')

@app.route('/crewmateBookType', methods=['POST', 'GET'])
def crewmateBookType():
	try:
		if((request.form.get('new') and request.form.get('existing')) or (not(request.form.get('new')) and not(request.form.get('existing')))):
			return render_template('error.html', error='Invalid selection.')

		Year = request.form['Date'][2:4]
		Quarter = request.form['Quarter']
		cruise = Year + Quarter


		mysqldb = mysql.connect()
		mycursor = mysqldb.cursor()

		sql = "select ID from Room where Package = (%s)"
		values = ('Crewmate')
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		Rooms = []
		for i in result:
			Rooms.append(i[0])
			
		sql = "select Room_ID, count(Room_ID) from Crewmate where ID like (%s) group by Room_ID"
		values = (cruise + '___2')
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		InvalidRooms = []
		for i in result:
			if int(i[1]) >= 2:
				InvalidRooms.append(i[0])
			
		FinalRooms = []
		for i in Rooms:
			if i not in InvalidRooms:
				FinalRooms.append(i)

		mycursor.close()
		mysqldb.close()

		if(request.form.get('new')):
			return render_template('crewmateBooking.html', tables=FinalRooms, year=request.form['Date'], quarter=Quarter)
		elif (request.form.get('existing')):
			return render_template('crewmateBookingExisting.html', tables=FinalRooms, year=request.form['Date'], quarter=Quarter)



	except Exception as e:
		return render_template('error.html', error=e)
	return render_template('index.html')


@app.route('/crewmateIntermediateBook')
def crewmateIntermediateBook():
	return render_template('crewmateBooking.html')

@app.route('/committingCrewmate_Login', methods=['POST','GET'])
def committingCrewmate_Login():
	try:
		mysqldb = mysql.connect()
		mycursor = mysqldb.cursor()
		temp = request.form
		Experience = temp["Experience"]
		Room = temp['Room_ID']
		Username = temp['User-ID']
		Year = temp['Date'][2:4]
		Quarter = temp['Quarter']

		Password = temp['Password']
		Name = temp['Name']
		Origin = temp['Origin']
		Department = temp['Dept']
		
		cruise = Year+Quarter

		mycursor.execute("select Dept_Name from Department")
		result = mycursor.fetchall()
		depts = []
		for i in result:
			depts.append(i[0])
		
		if Department not in depts:
			return render_template('error.html', error='The input Department does not exist.')

		sql = "select Department.Max_Capacity, count(Crewmate.ID) from Crewmate inner join Department on Department.Dept_Name = Crewmate.Dept_Name where Crewmate.Dept_Name = (%s) and Crewmate.ID like (%s)"
		values = (Department, cruise + '___2')
		mycursor.execute(sql, values)
		result=mycursor.fetchall()
		print(result[0][0], result[0][1])
		if result:
			if result[0][0] is not None:
				print('here')
				if int(result[0][0]) <= result[0][1]:
					return render_template('error.html', error='The input Department is at capacity for this cruise quarter.')
		


		mycursor.execute("select ID from Room")
		result = mycursor.fetchall()
		registered = []
		
		for i in result:    
			rms=i[0]
			registered.append(rms)

		if int(Room) not in registered:
			return render_template('error.html', error ='The given room does not exist.')

		if(int(Room) > 100):
			return render_template('error.html', error='The given room is not assigned for crewmates.')


		sql = "select ID from Crewmate where Room_ID = (%s) and ID like (%s)"
		values = (Room, cruise + '___2')
		mycursor.execute(sql, values)

		result = mycursor.fetchall()
		registered = []
		
		for i in result:    
			rms=i[0]
			registered.append(rms)
		
		curr_num = 0
		print("ye")
		print(cruise)
		for i in range(0, len(registered)):
			if(int(registered[i] / 10000) == int(cruise)):
				curr_num = curr_num + 1
				if curr_num >= 2:
					return render_template('error.html', error ='The given room is already full.')

		sql = "select count(*) from Login where ID = (%s) and Type = (%s)"
		values = (Username, 'Crewmate')
		mycursor.execute(sql, values)

		result = mycursor.fetchall()
		if (result[0][0]) > 0:
			return render_template('error.html', error = 'This crewmate already exists.')


		sql = "select count(*) from Login where ID = (%s) and Type != (%s)"
		values = (Username, 'Crewmate')
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		if result[0][0] > 0:
			return render_template('error.html', error ='This username is already assigned to another user.')

		sql = "select count(*) from crewmate where ID like (%s)"
		values = cruise + '___2'
		mycursor.execute(sql, values)
		result = mycursor.fetchall()

		print("here")

		if (result[0][0] == 200):
			return render_template('error.html', error ='The Quarter for the Cruise you have selected is at capacity.')

		
		sql = "select ID from crewmate where ID like (%s) order by ID desc limit 1"
		values = cruise + '____'
		mycursor.execute(sql, values)
		result = mycursor.fetchall()

		
		sql = "insert into Login values (%s, %s, %s)"
		values = (Username, Password, 'Crewmate')
		mycursor.execute(sql, values)

		new_id = 0
		print(mycursor.rowcount)
		if result:
			new_id = int(cruise) * 10000 + (int(str(result[0][0])[3:6]) + 1) * 10 + 2
			
		else:
			new_id = cruise + '0012'
			print("nein")
		print("wein")

		Active = 1
		sql = "insert into Crewmate values (%s, %s, %s, %s, %s, %s, %s, %s)"
		values = (new_id, Name, Room, Origin, Department, Experience, Active, Username)
		mycursor.execute(sql, values)
		print(values)
		mysqldb.commit()

		package = 'Crewmate'
		price = 0

		

	except Exception as e:
		return render_template('error.html', error=e)

	finally:
		mycursor.close() 
		mysqldb.close()

	return render_template('crewmateReceipt.html', name=Name, origin=Origin, dept=Department, room= Room, pack=package, price=price, date=temp['Date'], quarter=Quarter, user=Username, type='Booking Receipt')


@app.route('/committingCrewmate_LoginExisting', methods=['POST','GET'])
def committingCrewmate_LoginExisting():
	try:
		mysqldb = mysql.connect()
		mycursor = mysqldb.cursor()
		temp = request.form
		#Experience = temp["Experience"]
		Room = temp['Room_ID']
		Username = temp['User-ID']
		Year = temp['Date'][2:4]
		Quarter = temp['Quarter']

		#Password = temp['Password']
		#Name = temp['Name']
		#Origin = temp['Origin']
		Department = temp['Dept']
		
		cruise = Year+Quarter

		mycursor.execute("select Dept_Name from Department")
		result = mycursor.fetchall()
		depts = []
		for i in result:
			depts.append(i[0])
		
		if Department not in depts:
			return render_template('error.html', error='The input Department does not exist.')

		sql = "select Department.Max_Capacity, count(Crewmate.ID) from Crewmate inner join Department on Department.Dept_Name = Crewmate.Dept_Name where Crewmate.Dept_Name = (%s) and Crewmate.ID like (%s)"
		values = (Department, cruise + '___2')
		mycursor.execute(sql, values)
		result=mycursor.fetchall()
		print(result[0][0], result[0][1])
		if result:
			if result[0][0] is not None:
				print('here')
				if int(result[0][0]) <= result[0][1]:
					return render_template('error.html', error='The input Department is at capacity for this cruise quarter.')
		


		mycursor.execute("select ID from Room")
		result = mycursor.fetchall()
		registered = []
		
		for i in result:    
			rms=i[0]
			registered.append(rms)

		if int(Room) not in registered:
			return render_template('error.html', error ='The given room does not exist.')

		if(int(Room) > 100):
			return render_template('error.html', error='The given room is not assigned for crewmates.')


		sql = "select ID from Crewmate where Room_ID = (%s) and ID like (%s)"
		values = (Room, cruise + '___2')
		mycursor.execute(sql, values)

		result = mycursor.fetchall()
		registered = []
		
		for i in result:    
			rms=i[0]
			registered.append(rms)
		
		curr_num = 0
		print("ye")
		print(cruise)
		for i in range(0, len(registered)):
			if(int(registered[i] / 10000) == int(cruise)):
				curr_num = curr_num + 1
				if curr_num >= 2:
					return render_template('error.html', error ='The given room is already full.')

		sql = "select count(*) from Login where ID = (%s) and Type = (%s)"
		values = (Username, 'Crewmate')
		mycursor.execute(sql, values)

		result = mycursor.fetchall()
		if (result[0][0]) <= 0:
			return render_template('error.html', error = 'This crewmate does not exist.')

		sql = "select count(*) from Crewmate where ID like (%s) and Login_ID = (%s)"
		values = (cruise + '____', Username)
		mycursor.execute(sql, values)

		result = mycursor.fetchall()
		if(result[0][0]) >= 0:
			return render_template('error.html', error='This crewmate is already a part of the given cruise. Please use the Update Tab instead.')


		sql = "select count(*) from crewmate where ID like (%s)"
		values = cruise + '___2'
		mycursor.execute(sql, values)
		result = mycursor.fetchall()

		print("here")

		if (result[0][0] == 200):
			return render_template('error.html', error ='The Quarter for the Cruise you have selected is at capacity.')

		
		sql = "select ID from crewmate where ID like (%s) order by ID desc limit 1"
		values = cruise + '____'
		mycursor.execute(sql, values)
		result = mycursor.fetchall()

		new_id = 0
		print(mycursor.rowcount)
		if result:
			new_id = int(cruise) * 10000 + (int(str(result[0][0])[3:6]) + 1) * 10 + 2
			
		else:
			new_id = cruise + '0012'
			print("nein")
		print("wein")

		sql = "select Name, Experience, Origin, Dept_Name from Crewmate where Login_ID = (%s) limit 1"
		values = (Username)
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		Name = result[0][0]
		Experience = result[0][1]
		Origin = result[0][2]
		Department = result[0][3]
		Active = 1
		sql = "insert into Crewmate values (%s, %s, %s, %s, %s, %s, %s, %s)"
		values = (new_id, Name, Room, Origin, Department, Experience, Active, Username)
		mycursor.execute(sql, values)
		print(values)
		mysqldb.commit()

		package = 'Crewmate'
		price = 0

		

	except Exception as e:
		return render_template('error.html', error=e)

	finally:
		mycursor.close() 
		mysqldb.close()

	return render_template('crewmateReceipt.html', name=Name, origin=Origin, dept=Department, room= Room, pack=package, price=price, date=temp['Date'], quarter=Quarter, user=Username, type='Booking Receipt')




@app.route('/crewmateIntermediateUpdate')
def crewmateIntermediateUpdate():
	return render_template('updateCrewmate.html')



@app.route('/updateCrewmate', methods=['POST', 'GET'])
def updateCrewmate():
	try:
		mysqldb = mysql.connect()
		mycursor = mysqldb.cursor()
		select = request.form.get('choice')
		UserID = request.form['User_ID']
		Year = request.form['Year'][2:]
		Quarter = request.form['Quarter']
		cruise = Year + Quarter

		sql = "select count(*) from crewmate where Login_ID = (%s) and ID like (%s)"
		values = (UserID, cruise + '____')
		mycursor.execute(sql, values)
		result = mycursor.fetchall()

		print(result)

		if result[0][0] == 0:
			return render_template('error.html', error='The input Crewmate is not assigned to the given cruise.')
		print(result)
		sql = "select ID from crewmate where Login_ID = (%s) and ID like (%s)"
		values = (UserID, cruise + '____')
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		CrewmateID = result[0][0]

		if select == "Dept":
			print('dept only')
			CurrentDept = request.form['CurrentDept']
			NewDept = request.form['NewDept']

			sql = "select count(*) from Crewmate where Login_ID = (%s) and ID like (%s)"
			values = (UserID, cruise + '___2')
			mycursor.execute(sql, values)
			result = mycursor.fetchall()
			print(result)

			if result[0][0] <= 0:
				return render_template('The given crewmate is currently marked as inactive. Please use the Update tab to first change their status.')

			mycursor.execute("select Dept_Name from Department")
			result = mycursor.fetchall()
			depts = []
			for i in result:
				depts.append(i[0])
			
			if CurrentDept not in depts or NewDept not in depts:
				return render_template('error.html', error='An invalid department name was input.')
			sql = "select Dept_Name from crewmate where Login_ID = (%s) and ID like (%s)"
			values = (UserID, cruise + '___2')
			mycursor.execute(sql, values)
			result = mycursor.fetchall()
			print(result)
			if CurrentDept != result[0][0]:
				return render_template('error.html', error='The crewmate is not a member of the given department for this cruise quarter.')

			print('dept only')
			if CurrentDept == NewDept:
				return render_template('error.html', error='The crewmate is already a member of the desired department.')

			sql = "select Department.Min_Capacity, count(Crewmate.ID) from Crewmate inner join Department on Department.Dept_Name = Crewmate.Dept_Name where Crewmate.Dept_Name = (%s) and Crewmate.ID like (%s)"
			values = (CurrentDept, cruise + '___2')
			mycursor.execute(sql, values)
			result=mycursor.fetchall()
			print(result[0][0], result[0][1])
			if result:
				if result[0][0] is not None:
					if int(result[0][0]) >= result[0][1]:
						return render_template('error.html', error='The input Department is already understaffed for this cruise quarter.')

			sql = "select Department.Max_Capacity, count(Crewmate.ID) from Crewmate inner join Department on Department.Dept_Name = Crewmate.Dept_Name where Crewmate.Dept_Name = (%s) and Crewmate.ID like (%s)"
			values = (NewDept, cruise + '___2')
			mycursor.execute(sql, values)
			result=mycursor.fetchall()
			print(result[0][0], result[0][1])
			if result:
				if result[0][0] is not None:
					if int(result[0][0]) <= result[0][1]:
						return render_template('error.html', error='The input Department is at capacity for this cruise quarter.')

			sql = "update crewmate set Dept_Name = (%s) where Login_ID = (%s) and ID like (%s)"
			values = (NewDept, UserID, cruise+'___2')
			mycursor.execute(sql, values)
			#mysqldb.commit()
		elif select == "Status":

			if((request.form.get('Active') and request.form.get('Inactive')) or (not(request.form.get('Active')) and not(request.form.get('Inactive')))):
				return render_template('error.html', error='Invalid selection.')


			if(request.form.get('Active')):

				sql = "select count(*) from Crewmate where Login_ID = (%s) and ID like (%s)"
				values = (UserID, cruise + '___0')
				mycursor.execute(sql, values)
				result = mycursor.fetchall()

				if result[0][0] == 0:
					return render_template('error.html', error = 'The relevant crewmate is already an active member for this cruise.')

				sql = "select Room_ID from Crewmate where ID like (%s)"
				values  = (cruise + '___2')
				mycursor.execute(sql, values)
				result = mycursor.fetchall()
				rooms = []
				for i in result:
					rooms.append(i[0])

				mycursor.execute("select ID from Room")
				temp = mycursor.fetchall()
				registered = []
				for i in temp:    
					rms=i[0]
					registered.append(rms)

				NewRoom = -1
				for i in registered:
					if rooms.count(i) < 2:
						NewRoom = i 
						break

				if NewRoom == -1:
					return render_template('error.html', error = "There are no vacancies in this cruise quarter.")

				print(NewRoom)

				sql = "select Dept_Name from Crewmate where Login_ID = (%s) and ID like (%s)"
				values = (UserID, cruise + '___0')
				mycursor.execute(sql, values)
				result = mycursor.fetchall()

				InactiveDept = result[0][0]
				print(InactiveDept)

				sql = "select Department.Max_Capacity, count(Crewmate.ID) from Crewmate inner join Department on Department.Dept_Name = Crewmate.Dept_Name where Crewmate.Dept_Name = (%s) and Crewmate.ID like (%s)"
				values = (InactiveDept, cruise + '___2')
				mycursor.execute(sql, values)
				result=mycursor.fetchall()
				print(result[0][0], result[0][1])
				if result:
					if result[0][0] is not None:
						if int(result[0][0]) <= result[0][1]:
							return render_template('error.html', error='The input Department is at capacity for this cruise quarter.')

				sql = "update Crewmate set ID = (%s) where Login_ID = (%s) and ID like (%s)"
				values = (int(CrewmateID)+2, UserID, CrewmateID)
				mycursor.execute(sql, values)

				sql = "update Crewmate set Room_ID = (%s) where Login_ID = (%s) and ID like (%s)"
				values = (NewRoom, UserID, int(CrewmateID)+2)
				mycursor.execute(sql, values)

				sql = "update Crewmate set Status = (%s) where Login_ID = (%s) and ID like (%s)"
				values = ('1', UserID, int(CrewmateID)+2)
				mycursor.execute(sql, values)

			elif request.form.get('Inactive'):

				sql = "select count(*) from Crewmate where Login_ID = (%s) and ID like (%s)"
				values = (UserID, cruise + '___2')
				mycursor.execute(sql, values)
				result = mycursor.fetchall()

				if result[0][0] == 0:
					return render_template('error.html', error = 'The relevant crewmate is already an inactive member for this cruise.')
				print("reach")
				print(CrewmateID)


				sql = "update Crewmate set ID = (%s) where Login_ID = (%s) and ID like (%s)"
				values = (int(CrewmateID)-2, UserID, CrewmateID)
				mycursor.execute(sql, values)

				sql = "update Crewmate set Status = (%s) where Login_ID = (%s) and ID like (%s)"
				values = ('0', UserID, int(CrewmateID)-2)
				mycursor.execute(sql, values)
		elif select == "Both":

			if((request.form.get('Active') and request.form.get('Inactive')) or (not(request.form.get('Active')) and not(request.form.get('Inactive')))):
				return render_template('error.html', error='Invalid selection.')


			if(request.form.get('Active')):

				sql = "select count(*) from Crewmate where Login_ID = (%s) and ID like (%s)"
				values = (UserID, cruise + '___0')
				mycursor.execute(sql, values)
				result = mycursor.fetchall()

				if result[0][0] == 0:
					return render_template('error.html', error = 'The relevant crewmate is already an active member for this cruise.')

				sql = "select Room_ID from Crewmate where ID like (%s)"
				values  = (cruise + '___2')
				mycursor.execute(sql, values)
				result = mycursor.fetchall()
				rooms = []
				for i in result:
					rooms.append(i[0])

				mycursor.execute("select ID from Room")
				temp = mycursor.fetchall()
				registered = []
				for i in temp:    
					rms=i[0]
					registered.append(rms)

				NewRoom = -1
				for i in registered:
					if rooms.count(i) < 2:
						NewRoom = i 
						break

				if NewRoom == -1:
					return render_template('error.html', error = "There are no vacancies in this cruise quarter.")

				print(NewRoom)

				sql = "select Dept_Name from Crewmate where Login_ID = (%s) and ID like (%s)"
				values = (UserID, cruise + '___0')
				mycursor.execute(sql, values)
				result = mycursor.fetchall()

				InactiveDept = result[0][0]
				print(InactiveDept)

				sql = "select Department.Max_Capacity, count(Crewmate.ID) from Crewmate inner join Department on Department.Dept_Name = Crewmate.Dept_Name where Crewmate.Dept_Name = (%s) and Crewmate.ID like (%s)"
				values = (InactiveDept, cruise + '___2')
				mycursor.execute(sql, values)
				result=mycursor.fetchall()
				print(result[0][0], result[0][1])
				if result:
					if result[0][0] is not None:
						if int(result[0][0]) <= result[0][1]:
							return render_template('error.html', error='The input Department is at capacity for this cruise quarter.')

				sql = "update Crewmate set ID = (%s) where Login_ID = (%s) and ID like (%s)"
				values = (int(CrewmateID)+2, UserID, CrewmateID)
				mycursor.execute(sql, values)

				sql = "update Crewmate set Room_ID = (%s) where Login_ID = (%s) and ID like (%s)"
				values = (NewRoom, UserID, int(CrewmateID)+2)
				mycursor.execute(sql, values)

				sql = "update Crewmate set Status = (%s) where Login_ID = (%s) and ID like (%s)"
				values = ('1', UserID, int(CrewmateID)+2)
				mycursor.execute(sql, values)

				CurrentDept = request.form['CurrentDept']
				NewDept = request.form['NewDept']

				mycursor.execute("select Dept_Name from Department")
				result = mycursor.fetchall()
				depts = []
				for i in result:
					depts.append(i[0])
			
				if CurrentDept not in depts or NewDept not in depts:
					return render_template('error.html', error='An invalid department name was input.')

				sql = "select Dept_Name from crewmate where Login_ID = (%s) and ID like (%s)"
				values = (UserID, cruise + '___2')
				mycursor.execute(sql, values)
				result = mycursor.fetchall()
				if CurrentDept != result[0][0]:
					return render_template('error.html', error='The crewmate is not a member of the given department for this cruise quarter.')


				if CurrentDept == NewDept:
					return render_template('error.html', error='The crewmate is already a member of the desired department.')

				sql = "select Department.Min_Capacity, count(Crewmate.ID) from Crewmate inner join Department on Department.Dept_Name = Crewmate.Dept_Name where Crewmate.Dept_Name = (%s) and Crewmate.ID like (%s)"
				values = (CurrentDept, cruise + '___2')
				mycursor.execute(sql, values)
				result=mycursor.fetchall()
				print(result[0][0], result[0][1])
				if result:
					if result[0][0] is not None:
						if int(result[0][0]) >= result[0][1]:
							return render_template('error.html', error='The input Department is already understaffed for this cruise quarter.')

				sql = "select Department.Max_Capacity, count(Crewmate.ID) from Crewmate inner join Department on Department.Dept_Name = Crewmate.Dept_Name where Crewmate.Dept_Name = (%s) and Crewmate.ID like (%s)"
				values = (NewDept, cruise + '___2')
				mycursor.execute(sql, values)
				result=mycursor.fetchall()
				print(result[0][0], result[0][1])
				if result:
					if result[0][0] is not None:
						if int(result[0][0]) <= result[0][1]:
							return render_template('error.html', error='The input Department is at capacity for this cruise quarter.')

				sql = "update crewmate set Dept_Name = (%s) where Login_ID = (%s) and ID like (%s)"
				values = (NewDept, UserID, cruise+'___2')
				mycursor.execute(sql, values)

			elif request.form.get('Inactive'):

				sql = "select count(*) from Crewmate where Login_ID = (%s) and ID like (%s)"
				values = (UserID, cruise + '___2')
				mycursor.execute(sql, values)
				result = mycursor.fetchall()

				if result[0][0] == 0:
					return render_template('error.html', error = 'The relevant crewmate is already an inactive member for this cruise.')
				print("reach")
				print(CrewmateID)


				sql = "update Crewmate set ID = (%s) where Login_ID = (%s) and ID like (%s)"
				values = (int(CrewmateID)-2, UserID, CrewmateID)
				mycursor.execute(sql, values)

				sql = "update Crewmate set Status = (%s) where Login_ID = (%s) and ID like (%s)"
				values = ('0', UserID, int(CrewmateID)-2)
				mycursor.execute(sql, values)
		mysqldb.commit()


	except Exception as e:
		return render_template('error.html', error=e)
	finally:
		mycursor.close()
		mysqldb.close()
	return render_template('confirm.html', result = 'Your Transaction Has Been Completed.')

@app.route('/crewmateSwapIntermediate', methods=['POST', 'GET'])
def crewmateSwapIntermediate():
	try:
		UserID = request.form['userSwap']
		print(UserID)
		return render_template('crewmateSwap.html', username=UserID)
	except Exception as e:
		return render_template('error.html', error=e)

@app.route('/crewmateSwap', methods=['POST', 'GET'])
def crewmateSwap():
	try:
		mysqldb = mysql.connect()
		mycursor = mysqldb.cursor()
		UserID = request.form['user']
		SecondUser = request.form['SecondUser']
		print(SecondUser)
		Year = request.form['Date'][2:4]
		print(Year)
		Quarter = request.form['Quarter']
		print(Quarter)
		cruise = Year + Quarter

		sql = "select count(*) from crewmate where Login_ID = (%s) and ID like (%s)"
		values = (SecondUser, cruise + '____')
		mycursor.execute(sql, values)
		result = mycursor.fetchall()

		print(result)

		if result[0][0] == 0:
			return render_template('error.html', error='The input Crewmate is not assigned to the given cruise.')

		sql = "select count(*) from Crewmate where Login_ID = (%s) and Status = (%s) and ID like (%s)"
		values = (UserID, '1', cruise + '___2')
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		print(result)

		if result[0][0] <= 0:
			return render_template('You do not have an Active Status in this Cruise.')

		sql = "select count(*) from Crewmate where Login_ID = (%s) and Status = (%s) and ID like (%s)"
		values = (SecondUser, '1', cruise + '___2')
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		print(result)

		if result[0][0] <= 0:
			return render_template('The input crewmate does not have an Active Status in this Cruise.')

		if(UserID == SecondUser):
			return render_template('error.html', error = 'You cannot swap with yourself.')

		sql = "select Room_ID from crewmate where (Login_ID = (%s) or Login_ID = (%s)) and Status = (%s) and ID like (%s)"
		values = (UserID, SecondUser, '1', cruise + '___2')
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		
		if result[0][0] == result[1][0]:
			return render_template('error.html', error = 'Both crewmates already have the same room.')

		values = UserID + " " + SecondUser + " " + cruise + "\n"

		with open("templates\\swap.txt", "a") as myfile:
			myfile.write(values)

	except Exception as e:
		return render_template('error.html', error=e)
	finally:
		mycursor.close()
		mysqldb.close()
	return render_template('confirm.html', result = 'Your Transaction is Awaiting Approval from Offshore Management.')

@app.route('/offshoreSwapInter')
def offshoreSwapInter():
	try:
		fileHandle = open("templates\\swap.txt", "r")
	except:
		return render_template('confirm.html', result='No Swap Requests.')

	try:
		arr = fileHandle.read()
		arr = arr.split("\n")
		if(len(arr) == 1):
			return render_template('confirm.html', result='No Swap Requests.')

		fileHandle.close()

		fileHandle = open("templates\\swap.txt", "w")
		for i in range(1, len(arr) - 1):
			fileHandle.write(arr[i] + "\n")
		fileHandle.close()

		UserID = arr[0].split(" ")[0]
		SecondUser = arr[0].split(" ")[1]
		cruise = arr[0].split(" ")[2]
		print(UserID, SecondUser, cruise)

	except Exception as e:
		return render_template('error.html', error=e)

	return render_template('OffshoreSwap.html', user=UserID, second=SecondUser, cruise=cruise)

@app.route('/offshoreSwap', methods=['POST', 'GET'])
def offshoreSwap():
	try:
		mysqldb = mysql.connect()
		mycursor = mysqldb.cursor()
		UserID = request.form['user']
		SecondUser = request.form['Second']
		cruise = request.form['Cruise']

		sql = "select count(*) from crewmate where Login_ID = (%s) and ID like (%s)"
		values = (SecondUser, cruise + '____')
		mycursor.execute(sql, values)
		result = mycursor.fetchall()

		print(result)

		if result[0][0] == 0:
			return render_template('error.html', error='The input Crewmate is not assigned to the given cruise.')

		sql = "select count(*) from crewmate where Login_ID = (%s) and ID like (%s)"
		values = (UserID, cruise + '____')
		mycursor.execute(sql, values)
		result = mycursor.fetchall()

		print(result)

		if result[0][0] == 0:
			return render_template('error.html', error='The input Crewmate is not assigned to the given cruise.')

		sql = "select count(*) from Crewmate where Login_ID = (%s) and Status = (%s) and ID like (%s)"
		values = (UserID, '1', cruise + '___2')
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		print(result)

		if result[0][0] <= 0:
			return render_template('The input crewmate does not have an Active Status in this Cruise.')

		sql = "select count(*) from Crewmate where Login_ID = (%s) and Status = (%s) and ID like (%s)"
		values = (SecondUser, '1', cruise + '___2')
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		print(result)

		if result[0][0] <= 0:
			return render_template('The input crewmate does not have an Active Status in this Cruise.')

		if(UserID == SecondUser):
			return render_template('error.html', error = 'You cannot swap with yourself.')

		sql = "select Room_ID from crewmate where (Login_ID = (%s) or Login_ID = (%s)) and Status = (%s) and ID like (%s)"
		values = (UserID, SecondUser, '1', cruise + '___2')
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		
		if result[0][0] == result[1][0]:
			return render_template('error.html', error = 'Both crewmates already have the same room.')

		sql = "update Crewmate set Room_ID = (%s) where Login_ID = (%s) and ID like (%s)"
		values = (result[0][0], SecondUser, cruise + '___2')
		mycursor.execute(sql, values)

		sql = "update Crewmate set Room_ID = (%s) where Login_ID = (%s) and ID like (%s)"
		values = (result[1][0], UserID, cruise + '___2')
		mycursor.execute(sql, values)
		mysqldb.commit()


	except Exception as e:
		return render_template('error.html', error=e)
	finally:
		mycursor.close()
		mysqldb.close()
	return render_template('confirm.html', result = 'Your Transaction was Completed.')



if __name__ == "__main__":
    app.run(port=5501, debug=True)