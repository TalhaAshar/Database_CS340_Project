from flask import Flask, render_template, json, request
from flaskext.mysql import MySQL
from json import dumps
import math

mysql = MySQL()
app = Flask(__name__)

app.config['MYSQL_DATABASE_USER'] = 'b4cd8dd4fe5d0a'
app.config['MYSQL_DATABASE_PASSWORD'] = '03233985'
app.config['MYSQL_DATABASE_DB'] = 'heroku_8b24389f4313f76'
app.config['MYSQL_DATABASE_HOST'] = 'us-cdbr-east-02.cleardb.com'
mysql.init_app(app)

#countryCoord = open('default_country.txt', "r")
#Lat = float(next(countryCoord).split()[0])
#Lon = float(next(countryCoord).split()[0])
cruise_dest = [133.775136, -25.274398]
print("global", cruise_dest)
#countryCoord.close()

def setCountry(lat, lon):
	#countryCoord = open('default_country.txt', "r")
	Lat = lat#float(next(countryCoord).split()[0])
	Lon = lon#float(next(countryCoord).split()[0])
	global cruise_dest
	cruise_dest = [Lon, Lat]
	print(cruise_dest)
	#countryCoord.close()

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

			if(temp.get('offshore') or (temp.get('crewmate'))):
				return render_template('error.html', error='Please select a single type of account.')

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
			print(Name, Age, CNIC, Disability, Promo, UserID)
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


			return render_template('passengerHome.html', username=UserID, CNIC=CNIC, name=Name, age=Age, disability=Disability, promo=Promo, flag=flag, dest=cruise_dest)
		#return render_template('passengerBooking.html', username=UserID, CNIC=CNIC, name=Name, age=Age, disability=Disability, promo=Promo)
		elif _UserType == 'Crewmate':
			if(temp.get('offshore') or (temp.get('passenger'))):
				return render_template('error.html', error='Please select a single type of account.')

			mycursor.execute("select ID from crewmate where ID like '______2' order by ID desc LIMIT 1")
			result = mycursor.fetchall()

			Current_Year = str(result[0][0])[0:2]
			Current_Quarter = str(result[0][0])[2]
			Current_Cruise =Current_Year + Current_Quarter

			sql = "select name, origin, dept_name, Experience, status, ID from crewmate where Login_ID = (%s) and ID like (%s)"
			values = (UserID, Current_Cruise + '___' + '2')
			mycursor.execute(sql, values)
			result = mycursor.fetchall()

			print(result)

			if not result:
				return render_template('error.html', error='You are not an Active Member of the Current Cruise.')

			Name = result[0][0]
			Origin = result[0][1]
			Dept_Name = result[0][2]
			Experience = result[0][3]
			Status = result[0][4]
			ID = result[0][5]
			print(result)

			sql = "select count(*) from highest_ranking_officer where Crewmate_ID = (%s)"
			values = (ID)
			mycursor.execute(sql, values)
			result = mycursor.fetchall()

			if(result[0][0] == 0):
				mycursor.close()
				mysqldb.close()
				if(Dept_Name == 'Supplies'):
					return render_template('crewmateInventoryHome.html', username=UserID, name=Name, origin=Origin, dept=Dept_Name, exp=Experience, status=Status, dest=cruise_dest)
				elif(Dept_Name == 'Administration'):
					return render_template('crewmateAdminHome.html', username=UserID, name=Name, origin=Origin, dept=Dept_Name, exp=Experience, status=Status, dest=cruise_dest)
				elif(Dept_Name == 'Cleaning'):
					return render_template('crewmateCleaningHome.html', username=UserID, name=Name, origin=Origin, dept=Dept_Name, exp=Experience, status=Status, dest=cruise_dest)
				elif(Dept_Name == 'Engine'):
					return render_template('crewmateEngineHome.html', username=UserID, name=Name, origin=Origin, dept=Dept_Name, exp=Experience, status=Status, dest=cruise_dest)
				elif(Dept_Name == 'First Aid'):
					return render_template('crewmateFirstAidHome.html', username=UserID, name=Name, origin=Origin, dept=Dept_Name, exp=Experience, status=Status, dest=cruise_dest)
				elif(Dept_Name == 'Kitchen'):
					return render_template('crewmateKitchenHome.html', username=UserID, name=Name, origin=Origin, dept=Dept_Name, exp=Experience, status=Status, dest=cruise_dest)
				elif(Dept_Name == 'Security'):
					return render_template('crewmateSecurityHome.html', username=UserID, name=Name, origin=Origin, dept=Dept_Name, exp=Experience, status=Status, dest=cruise_dest)
				elif(Dept_Name == 'Room Service'):
					return render_template('crewmateRoomServiceHome.html', username=UserID, name=Name, origin=Origin, dept=Dept_Name, exp=Experience, status=Status, dest=cruise_dest)
				else:
					return render_template('crewmateGenericHome.html', username=UserID, name=Name, origin=Origin, dept=Dept_Name, exp=Experience, status=Status, dest=cruise_dest)
			else:
				sql = "select Officer_Rank, Designation from highest_ranking_officer where Crewmate_ID = (%s)"
				values = (ID)
				mycursor.execute(sql, values)
				result = mycursor.fetchall()
				Rank = result[0][0]
				mycursor.close()
				mysqldb.close()
				if(Dept_Name == 'Supplies'):
					return render_template('rankingInventoryHome.html', username=UserID, name=Name, rank=Rank, origin=Origin, dept=Dept_Name, exp=Experience, status=Status, dest=cruise_dest)
				elif(Dept_Name == 'Administration'):
					return render_template('rankingAdminHome.html', username=UserID, name=Name, rank=Rank, origin=Origin, dept=Dept_Name, exp=Experience, status=Status, dest=cruise_dest)
				elif(Dept_Name == 'Cleaning'):
					return render_template('rankingCleaningHome.html', username=UserID, name=Name, rank=Rank, origin=Origin, dept=Dept_Name, exp=Experience, status=Status, dest=cruise_dest)
				elif(Dept_Name == 'Engine'):
					return render_template('rankingEngineHome.html', username=UserID, name=Name, rank=Rank, origin=Origin, dept=Dept_Name, exp=Experience, status=Status, dest=cruise_dest)
				elif(Dept_Name == 'First Aid'):
					return render_template('rankingFirstAidHome.html', username=UserID, name=Name, rank=Rank, origin=Origin, dept=Dept_Name, exp=Experience, status=Status, dest=cruise_dest)
				elif(Dept_Name == 'Kitchen'):
					return render_template('rankingKitchenHome.html', username=UserID, name=Name, rank=Rank, origin=Origin, dept=Dept_Name, exp=Experience, status=Status, dest=cruise_dest)
				elif(Dept_Name == 'Security'):
					return render_template('rankingSecurityHome.html', username=UserID, name=Name, rank=Rank, origin=Origin, dept=Dept_Name, exp=Experience, status=Status, dest=cruise_dest)
				elif(Dept_Name == 'Room Service'):
					return render_template('rankingRoomServiceHome.html', username=UserID, name=Name, rank=Rank, origin=Origin, dept=Dept_Name, exp=Experience, status=Status, dest=cruise_dest)
				elif(Dept_Name == 'Operations'):
					return render_template('rankingOperationsHome.html', username=UserID, name=Name, rank=Rank, origin=Origin, dept=Dept_Name, exp=Experience, status=Status, dest=cruise_dest)
				elif(Dept_Name == 'Acitivities'):
					return render_template('rankingActivitiesHome.html', username=UserID, name=Name, rank=Rank, origin=Origin, dept=Dept_Name, exp=Experience, status=Status, dest=cruise_dest)
		elif _UserType == 'Offshore_Management':

			mycursor.close()
			mysqldb.close()

			if(temp.get('passenger') or (temp.get('crewmate'))):
				return render_template('error.html', error='Please select a single type of account.')

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

		mycursor.execute("select ID from crewmate where ID like '______2' order by ID desc LIMIT 1")
		result = mycursor.fetchall()

		Current_Year = str(result[0][0])[0:2]
		Current_Quarter = str(result[0][0])[2]
		Current_Cruise =Current_Year + Current_Quarter

		if(int(Year) < int(Current_Year)):
			return render_template('error.html', error="You cannot make a booking for a previous cruise.")

		if(int(Quarter) < int(Current_Quarter)):
			return render_template('error.html', error="You cannot make a booking for a previous cruise.") 

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

	return render_template('bookingReceiptTravel.html', name=_Name, cnic=_CNIC, age=_Age, room= _Room, pack=_package, price=_price, disabled=_Disable, promo=_Promo,date=temp['Date'], quarter=_Quarter, user=_Username, type='Booking Receipt')

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
		return render_template('passengerError.html', error=e, username=UserID)

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

		mycursor.execute("select ID from crewmate where ID like '______2' order by ID desc LIMIT 1")
		result = mycursor.fetchall()

		Current_Year = str(result[0][0])[0:2]
		Current_Quarter = str(result[0][0])[2]
		Current_Cruise =Current_Year + Current_Quarter

		if(int(Year) < int(Current_Year)):
			return render_template('passengerError.html', error="You cannot make a booking for a previous cruise.", username=UserID)

		if(int(Quarter) < int(Current_Quarter)):
			return render_template('passengerError.html', error="You cannot make a booking for a previous cruise.", username=UserID)

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
		return render_template('passengerError.html', error=e, username=UserID)

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
			return render_template('passengerError.html', error ='The given room does not exist.', username=UserID)

		if(int(Room) <= 100):
			return render_template('passengerError.html', error='The given room is not assigned to you.', username=UserID)

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
						return render_template('passengerError.html', error ='The given room is already full.', username=UserID)
				elif int(Room) <= 280:
					if curr_num >= 4:
						return render_template('passengerError.html', error ='The given room is already full.', username=UserID)
				else:
					if curr_num >= 5:
						return render_template('passengerError.html', error ='The given room is already full.', username=UserID)

		sql = "select count(*) from passenger where ID like (%s)"
		values = cruise + '___1'
		mycursor.execute(sql, values)
		result = mycursor.fetchall()

		if (result[0][0] == 680):
			return render_template('passengerError.html', error ='The Quarter for the Cruise you have selected is at capacity.', username=UserID)

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
		return render_template('passengerError.html', error=e, username=UserID)

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
	try:
		UserID = request.form['userDel']
		CNIC = request.form['CNICDel']
		Name = request.form['NameDel']
		Age = request.form['AgeDel']
		Disable = request.form['disabilityDel']
		Promo = request.form['promo_campaignDel']
	except Exception as e:
		return render_template('passengerError.html', error=e, username=UserID)

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

		mycursor.execute("select ID from crewmate where ID like '______2' order by ID desc LIMIT 1")
		result = mycursor.fetchall()

		Current_Year = str(result[0][0])[0:2]
		Current_Quarter = str(result[0][0])[2]
		Current_Cruise =Current_Year + Current_Quarter

		if(int(Year) < int(Current_Year)):
			return render_template('passengerError.html', error="You cannot make a cancellation for a previous cruise.", username=UserID)

		if(int(Quarter) < int(Current_Quarter)):
			return render_template('passengerError.html', error="You cannot make a cancellation for a previous cruise.", username=UserID)


		sql = "select Room.ID, Room.Package, Room.Price from Room inner join Passenger on Room.ID = Passenger.Room_ID where Passenger.Login_ID = (%s) and  Passenger.ID like (%s) order by Room.ID asc"
		values = (UserID, cruise + '___1')
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		myRooms = []
		for i in result:
			myRooms.append(i)


	except Exception as e:
		return render_template('passengerError.html', error=e, username=UserID)

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
			return render_template('passengerError.html', error ='The given room does not exist.', username=UserID)

		sql = "select ID from Passenger where Room_ID = (%s) and ID like (%s) and Login_ID = (%s)"
		values = (Room, cruise + '___1', UserID)
		mycursor.execute(sql, values)
		result = mycursor.fetchall()

		if not result:
			return render_template('passengerError.html', error ='You do not have any reservations for this room for the cruise quarter input.', username=UserID)			

		
		num = []
		for i in result:
			num.append(i[0])

		sql = "select Package, Price from Room where ID = (%s)"
		values = (Room)
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		package = result[0][0]
		price = str(-result[0][1])

		sql = "update Ticket set Status = (%s) where Passenger_ID = (%s)"
		values = ('0', num[0])
		mycursor.execute(sql, values)

		sql = "update Passenger set ID = (%s) where ID = (%s)"
		for i in num:
			values = (int(i)-1, i)
			mycursor.execute(sql, values)
			break
		mysqldb.commit()
	except Exception as e:
		return render_template('passengerError.html', error=e, username=UserID)
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
	try:
		UserID = request.form['userUPG']
		CNIC = request.form['CNICUPG']
		Name = request.form['NameUPG']
		Age = request.form['AgeUPG']
		Disable = request.form['disabilityUPG']
		Promo = request.form['promo_campaignUPG']
	except Exception as e:
		return render_template('passengerError.html', error=e, username=UserID)

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

		mycursor.execute("select ID from crewmate where ID like '______2' order by ID desc LIMIT 1")
		result = mycursor.fetchall()

		Current_Year = str(result[0][0])[0:2]
		Current_Quarter = str(result[0][0])[2]
		Current_Cruise =Current_Year + Current_Quarter

		if(int(Year) < int(Current_Year)):
			return render_template('passengerError.html', error="You cannot make an upgrade for a previous cruise.", username=UserID)

		if(int(Quarter) < int(Current_Quarter)):
			return render_template('passengerError.html', error="You cannot make an upgrade for a previous cruise.", username=UserID)

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
		return render_template('passengerError.html', error=e, username=UserID)

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
			return render_template('passengerError.html', error ='One of the given rooms does not exist.', username=UserID)

		if int(Room) <= 100:
			return render_template('passengerError.html', error='The given room is not assigned to you.', username=UserID)

		sql = "select ID from Passenger where Room_ID = (%s) and ID like (%s) and Login_ID = (%s)"
		values = (Room, cruise + '___1', UserID)
		print(values)
		mycursor.execute(sql, values)
		result = mycursor.fetchall()

		if not result:
			return render_template('passengerError.html', error ='You do not have any reservations for this room for the cruise quarter input.', username=UserID)			
	
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
			return render_template('passengerError.html', error='You cannot upgrade from a "High" Package.', username=UserID)

		if Package == 'Low':
			return render_template('passengerError.html', error='You cannot upgrade to a "Low" Package.', username=UserID)			

		if CurrentPackage == 'Medium' and Package == 'Medium':
			return render_template('passengerError.html', error='You cannot upgrade to a room of the same package.', username=UserID)

		sql = "select ID from Passenger where Room_ID = (%s) and ID like (%s) and Login_ID = (%s)"
		values = (NewRoom, cruise + '___1', UserID)
		mycursor.execute(sql, values)
		result = mycursor.fetchall()

		if int(NewRoom) <= 280:
			if mycursor.rowcount == 4:
				return render_template('passengerError.html', error='Your desired room is at capacity.', username=UserID)	
		elif int(NewRoom) <= 300:
			if mycursor.rowcount == 5:
				return render_template('passengerError.html', error='Your desired room is at capacity.', username=UserID)	

		finalPrice = NewPrice - int(CurrentPrice)

		sql = "update Passenger set Room_ID = (%s) where ID = (%s) and Login_ID = (%s)"
		values = (NewRoom, myID, UserID)							
		mycursor.execute(sql, values)
		mysqldb.commit()
	except Exception as e:
		return render_template('passengerError.html', error=e, username=UserID)
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
		return render_template('passengerError.html', error=e, username=UserID)
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
		return render_template('offshoreError.html', error=e)
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
			return render_template('offshoreError.html', error='Invalid selection.')

		Year = request.form['Date'][2:4]
		Quarter = request.form['Quarter']
		cruise = Year + Quarter


		mysqldb = mysql.connect()
		mycursor = mysqldb.cursor()

		mycursor.execute("select ID from crewmate where ID like '______2' order by ID desc LIMIT 1")
		result = mycursor.fetchall()

		Current_Year = str(result[0][0])[0:2]
		Current_Quarter = str(result[0][0])[2]
		Current_Cruise =Current_Year + Current_Quarter

		if(int(cruise) < int(Current_Cruise)):
			return render_template('offshoreError.html', error='Insertion of Crewmate into a previous quarter is not allowed.')


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
		return render_template('offshoreError.html', error=e)
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
			return render_template('offshoreError.html', error='The input Department does not exist.')

		sql = "select Department.Max_Capacity, count(Crewmate.ID) from Crewmate inner join Department on Department.Dept_Name = Crewmate.Dept_Name where Crewmate.Dept_Name = (%s) and Crewmate.ID like (%s)"
		values = (Department, cruise + '___2')
		mycursor.execute(sql, values)
		result=mycursor.fetchall()
		print(result[0][0], result[0][1])
		if result:
			if result[0][0] is not None:
				print('here')
				if int(result[0][0]) <= result[0][1]:
					return render_template('offshoreError.html', error='The input Department is at capacity for this cruise quarter.')
		


		mycursor.execute("select ID from Room")
		result = mycursor.fetchall()
		registered = []
		
		for i in result:    
			rms=i[0]
			registered.append(rms)

		if int(Room) not in registered:
			return render_template('offshoreError.html', error ='The given room does not exist.')

		if(int(Room) > 100):
			return render_template('offshoreError.html', error='The given room is not assigned for crewmates.')


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
					return render_template('offshoreError.html', error ='The given room is already full.')

		sql = "select count(*) from Login where ID = (%s) and Type = (%s)"
		values = (Username, 'Crewmate')
		mycursor.execute(sql, values)

		result = mycursor.fetchall()
		if (result[0][0]) > 0:
			return render_template('offshoreError.html', error = 'This crewmate already exists.')


		sql = "select count(*) from Login where ID = (%s) and Type != (%s)"
		values = (Username, 'Crewmate')
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		if result[0][0] > 0:
			return render_template('offshoreError.html', error ='This username is already assigned to another user.')

		sql = "select count(*) from crewmate where ID like (%s)"
		values = cruise + '___2'
		mycursor.execute(sql, values)
		result = mycursor.fetchall()

		print("here")

		if (result[0][0] == 200):
			return render_template('offshoreError.html', error ='The Quarter for the Cruise you have selected is at capacity.')

		
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

		temp = request.form
		Officer = 0
		if temp.get('Officer'):
			mycursor.execute('select count(*) from highest_ranking_officer')
			result = mycursor.fetchall()
			rank = result[0][0] + 1
			sql = "insert into highest_ranking_officer values (%s, %s, %s)"
			values = (rank, new_id, Department)
			mycursor.execute(sql, values)

		mysqldb.commit()

		package = 'Crewmate'
		price = 0

		

	except Exception as e:
		return render_template('offshoreError.html', error=e)

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
			return render_template('offshoreError.html', error='The input Department does not exist.')

		sql = "select Department.Max_Capacity, count(Crewmate.ID) from Crewmate inner join Department on Department.Dept_Name = Crewmate.Dept_Name where Crewmate.Dept_Name = (%s) and Crewmate.ID like (%s)"
		values = (Department, cruise + '___2')
		mycursor.execute(sql, values)
		result=mycursor.fetchall()
		print(result[0][0], result[0][1])
		if result:
			if result[0][0] is not None:
				print('here')
				if int(result[0][0]) <= result[0][1]:
					return render_template('offshoreError.html', error='The input Department is at capacity for this cruise quarter.')
		


		mycursor.execute("select ID from Room")
		result = mycursor.fetchall()
		registered = []
		
		for i in result:    
			rms=i[0]
			registered.append(rms)

		if int(Room) not in registered:
			return render_template('offshoreError.html', error ='The given room does not exist.')

		if(int(Room) > 100):
			return render_template('offshoreError.html', error='The given room is not assigned for crewmates.')


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
					return render_template('offshoreError.html', error ='The given room is already full.')

		sql = "select count(*) from Login where ID = (%s) and Type = (%s)"
		values = (Username, 'Crewmate')
		mycursor.execute(sql, values)

		result = mycursor.fetchall()
		if (result[0][0]) <= 0:
			return render_template('offshoreError.html', error = 'This crewmate does not exist.')

		sql = "select count(*) from Crewmate where ID like (%s) and Login_ID = (%s)"
		values = (cruise + '____', Username)
		mycursor.execute(sql, values)

		result = mycursor.fetchall()
		print(result)
		if(result[0][0]) > 0:
			return render_template('offshoreError.html', error='This crewmate is already a part of the given cruise. Please use the Update Tab instead.')


		sql = "select count(*) from crewmate where ID like (%s)"
		values = cruise + '___2'
		mycursor.execute(sql, values)
		result = mycursor.fetchall()

		print("here")

		if (result[0][0] == 200):
			return render_template('offshoreError.html', error ='The Quarter for the Cruise you have selected is at capacity.')

		
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

		temp = request.form
		Officer = 0
		if temp.get('Officer'):
			mycursor.execute('select count(*) from highest_ranking_officer')
			result = mycursor.fetchall()
			rank = result[0][0] + 1
			sql = "insert into highest_ranking_officer values (%s, %s, %s)"
			values = (rank, new_id, Department)
			mycursor.execute(sql, values)

		mysqldb.commit()

		package = 'Crewmate'
		price = 0

		

	except Exception as e:
		return render_template('offshoreError.html', error=e)

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

		mycursor.execute("select ID from crewmate where ID like '______2' order by ID desc LIMIT 1")
		result = mycursor.fetchall()

		Current_Year = str(result[0][0])[0:2]
		Current_Quarter = str(result[0][0])[2]
		Current_Cruise =Current_Year + Current_Quarter

		if(int(cruise) < int(Current_Cruise)):
			return render_template('offshoreError.html', error='Updating of Crewmate from a previous quarter is not allowed.')

		sql = "select count(*) from crewmate where Login_ID = (%s) and ID like (%s)"
		values = (UserID, cruise + '____')
		mycursor.execute(sql, values)
		result = mycursor.fetchall()

		print(result)

		if result[0][0] == 0:
			return render_template('offshoreError.html', error='The input Crewmate is not assigned to the given cruise.')
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
				return render_template('offshoreError.html', error='The given crewmate is currently marked as inactive. Please use the Update tab to first change their status.')

			mycursor.execute("select Dept_Name from Department")
			result = mycursor.fetchall()
			depts = []
			for i in result:
				depts.append(i[0])
			
			if CurrentDept not in depts or NewDept not in depts:
				return render_template('offshoreError.html', error='An invalid department name was input.')
			sql = "select Dept_Name from crewmate where Login_ID = (%s) and ID like (%s)"
			values = (UserID, cruise + '___2')
			mycursor.execute(sql, values)
			result = mycursor.fetchall()
			print(result)
			if CurrentDept != result[0][0]:
				return render_template('offshoreError.html', error='The crewmate is not a member of the given department for this cruise quarter.')

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
						return render_template('offshoreError.html', error='The input Department is already understaffed for this cruise quarter.')

			sql = "select Department.Max_Capacity, count(Crewmate.ID) from Crewmate inner join Department on Department.Dept_Name = Crewmate.Dept_Name where Crewmate.Dept_Name = (%s) and Crewmate.ID like (%s)"
			values = (NewDept, cruise + '___2')
			mycursor.execute(sql, values)
			result=mycursor.fetchall()
			print(result[0][0], result[0][1])
			if result:
				if result[0][0] is not None:
					if int(result[0][0]) <= result[0][1]:
						return render_template('offshoreError.html', error='The input Department is at capacity for this cruise quarter.')

			sql = "update crewmate set Dept_Name = (%s) where Login_ID = (%s) and ID like (%s)"
			values = (NewDept, UserID, cruise+'___2')
			mycursor.execute(sql, values)
			#mysqldb.commit()
		elif select == "Status":

			if((request.form.get('Active') and request.form.get('Inactive')) or (not(request.form.get('Active')) and not(request.form.get('Inactive')))):
				return render_template('offshoreError.html', error='Invalid selection.')


			if(request.form.get('Active')):

				sql = "select count(*) from Crewmate where Login_ID = (%s) and ID like (%s)"
				values = (UserID, cruise + '___0')
				mycursor.execute(sql, values)
				result = mycursor.fetchall()

				if result[0][0] == 0:
					return render_template('offshoreError.html', error = 'The relevant crewmate is already an active member for this cruise.')

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
					return render_template('offshoreError.html', error = "There are no vacancies in this cruise quarter.")

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
							return render_template('offshoreError.html', error='The input Department is at capacity for this cruise quarter.')

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
					return render_template('offshoreError.html', error = 'The relevant crewmate is already an inactive member for this cruise.')
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
				return render_template('offshoreError.html', error='Invalid selection.')


			if(request.form.get('Active')):

				sql = "select count(*) from Crewmate where Login_ID = (%s) and ID like (%s)"
				values = (UserID, cruise + '___0')
				mycursor.execute(sql, values)
				result = mycursor.fetchall()

				if result[0][0] == 0:
					return render_template('offshoreError.html', error = 'The relevant crewmate is already an active member for this cruise.')

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
					return render_template('offshoreError.html', error = "There are no vacancies in this cruise quarter.")

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
							return render_template('offshoreError.html', error='The input Department is at capacity for this cruise quarter.')

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
					return render_template('offshoreError.html', error='An invalid department name was input.')

				sql = "select Dept_Name from crewmate where Login_ID = (%s) and ID like (%s)"
				values = (UserID, cruise + '___2')
				mycursor.execute(sql, values)
				result = mycursor.fetchall()
				if CurrentDept != result[0][0]:
					return render_template('offshoreError.html', error='The crewmate is not a member of the given department for this cruise quarter.')


				if CurrentDept == NewDept:
					return render_template('offshoreError.html', error='The crewmate is already a member of the desired department.')

				sql = "select Department.Min_Capacity, count(Crewmate.ID) from Crewmate inner join Department on Department.Dept_Name = Crewmate.Dept_Name where Crewmate.Dept_Name = (%s) and Crewmate.ID like (%s)"
				values = (CurrentDept, cruise + '___2')
				mycursor.execute(sql, values)
				result=mycursor.fetchall()
				print(result[0][0], result[0][1])
				if result:
					if result[0][0] is not None:
						if int(result[0][0]) >= result[0][1]:
							return render_template('offshoreError.html', error='The input Department is already understaffed for this cruise quarter.')

				sql = "select Department.Max_Capacity, count(Crewmate.ID) from Crewmate inner join Department on Department.Dept_Name = Crewmate.Dept_Name where Crewmate.Dept_Name = (%s) and Crewmate.ID like (%s)"
				values = (NewDept, cruise + '___2')
				mycursor.execute(sql, values)
				result=mycursor.fetchall()
				print(result[0][0], result[0][1])
				if result:
					if result[0][0] is not None:
						if int(result[0][0]) <= result[0][1]:
							return render_template('offshoreError.html', error='The input Department is at capacity for this cruise quarter.')

				sql = "update crewmate set Dept_Name = (%s) where Login_ID = (%s) and ID like (%s)"
				values = (NewDept, UserID, cruise+'___2')
				mycursor.execute(sql, values)

			elif request.form.get('Inactive'):

				sql = "select count(*) from Crewmate where Login_ID = (%s) and ID like (%s)"
				values = (UserID, cruise + '___2')
				mycursor.execute(sql, values)
				result = mycursor.fetchall()

				if result[0][0] == 0:
					return render_template('offshoreError.html', error = 'The relevant crewmate is already an inactive member for this cruise.')
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
		return render_template('offshoreError.html', error=e)
	finally:
		mycursor.close()
		mysqldb.close()
	return render_template('confirm.html', result = 'Your Transaction Has Been Completed.')

@app.route('/crewmateSwapIntermediate', methods=['POST', 'GET'])
def crewmateSwapIntermediate():
	try:
		UserID = request.form['userSwap']
		Dept = request.form['DeptSwap']
		print(UserID)
		return render_template('crewmateSwap.html', username=UserID, dept=Dept)
	except Exception as e:
		return render_template('crewmateError.html', error=e, username=UserID, dept= Dept)

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
		Dept = request.form['dept']

		mycursor.execute("select ID from crewmate where ID like '______2' order by ID desc LIMIT 1")
		result = mycursor.fetchall()

		Current_Year = str(result[0][0])[0:2]
		Current_Quarter = str(result[0][0])[2]
		Current_Cruise =Current_Year + Current_Quarter

		if(int(cruise) < int(Current_Cruise)):
			return render_template('offshoreError.html', error='Swapping is only allowed for current or future cruises.')

		sql = "select count(*) from crewmate where Login_ID = (%s) and ID like (%s)"
		values = (SecondUser, cruise + '____')
		mycursor.execute(sql, values)
		result = mycursor.fetchall()

		print(result)

		if result[0][0] == 0:
			return render_template('crewmateError.html', error='The input Crewmate is not assigned to the given cruise.', username=UserID, dept=Dept)

		sql = "select count(*) from Crewmate where Login_ID = (%s) and Status = (%s) and ID like (%s)"
		values = (UserID, '1', cruise + '___2')
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		print(result)

		if result[0][0] <= 0:
			return render_template('crewmateError.html', error='You do not have an Active Status in this Cruise.', username=UserID, dept=Dept)

		sql = "select count(*) from Crewmate where Login_ID = (%s) and Status = (%s) and ID like (%s)"
		values = (SecondUser, '1', cruise + '___2')
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		print(result)

		if result[0][0] <= 0:
			return render_template('crewmateError.html', error='The input crewmate does not have an Active Status in this Cruise.', username=UserID, dept=Dept)

		if(UserID == SecondUser):
			return render_template('crewmateError.html', error = 'You cannot swap with yourself.', username=UserID, dept=Dept)

		sql = "select Room_ID from crewmate where (Login_ID = (%s) or Login_ID = (%s)) and Status = (%s) and ID like (%s)"
		values = (UserID, SecondUser, '1', cruise + '___2')
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		
		if result[0][0] == result[1][0]:
			return render_template('crewmateError.html', error = 'Both crewmates already have the same room.', username=UserID, dept=Dept)

		values = UserID + " " + SecondUser + " " + cruise + "\n"

		with open("templates\\swap.txt", "a") as myfile:
			myfile.write(values)

	except Exception as e:
		return render_template('crewmateError.html', error=e, username=UserID, dept=Dept)
	finally:
		mycursor.close()
		mysqldb.close()
	return render_template('confirmCrew.html', result = 'Your Transaction is Awaiting Approval from Offshore Management.', username=UserID, dept=Dept)

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

		mysqldb = mysql.connect()
		mycursor = mysqldb.cursor()
		sql = "select Crewmate.Name, Room.ID, Crewmate.Login_ID from Crewmate inner join Room on Room.ID = Crewmate.Room_ID  where  Crewmate.ID like (%s) and (Crewmate.Login_ID = (%s) or Crewmate.Login_ID = (%s))"
		values = (cruise + '___2', UserID, SecondUser)
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		print(result)

		arr = []
		arr.append(result[0])
		arr.append(result[1])

		mycursor.close()
		mysqldb.close()

	except Exception as e:
		return render_template('offshoreError.html', error=e)
	print("here")
	return render_template('offshoreSwap.html', user=UserID, second=SecondUser, cruise=cruise, result=arr)

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
			return render_template('offshoreError.html', error='The input Crewmate is not assigned to the given cruise.')

		sql = "select count(*) from crewmate where Login_ID = (%s) and ID like (%s)"
		values = (UserID, cruise + '____')
		mycursor.execute(sql, values)
		result = mycursor.fetchall()

		print(result)

		if result[0][0] == 0:
			return render_template('offshoreError.html', error='The input Crewmate is not assigned to the given cruise.')

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
			return render_template('offshoreError.html', error = 'You cannot swap with yourself.')

		sql = "select Room_ID from crewmate where (Login_ID = (%s) or Login_ID = (%s)) and Status = (%s) and ID like (%s)"
		values = (UserID, SecondUser, '1', cruise + '___2')
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		
		if result[0][0] == result[1][0]:
			return render_template('offshoreError.html', error = 'Both crewmates already have the same room.')

		sql = "update Crewmate set Room_ID = (%s) where Login_ID = (%s) and ID like (%s)"
		values = (result[0][0], SecondUser, cruise + '___2')
		mycursor.execute(sql, values)

		sql = "update Crewmate set Room_ID = (%s) where Login_ID = (%s) and ID like (%s)"
		values = (result[1][0], UserID, cruise + '___2')
		mycursor.execute(sql, values)
		mysqldb.commit()


	except Exception as e:
		return render_template('offshoreError.html', error=e)
	finally:
		mycursor.close()
		mysqldb.close()
	return render_template('confirm.html', result = 'Your Transaction was Completed.')

@app.route('/returnPassengerHome', methods=['POST', 'GET'])
def returnPassengerHome():
	try:
		mysqldb = mysql.connect()
		mycursor = mysqldb.cursor()

		UserID = request.form['user']

		sql = "select Name, Age, CNIC, Disability, Promotional_Consent from Passenger where Login_ID = (%s) order by ID desc"
		values = (UserID)
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		Name = result[0][0]
		Age = result[0][1]
		CNIC = result[0][2]
		Disability = result[0][3]
		Promo = result[0][4]
		flag = 0
	except Exception as e:
		return render_template('error.html', error=e)
	finally:
		mycursor.close()
		mysqldb.close()
	return render_template('passengerHome.html', username=UserID, CNIC=CNIC, name=Name, age=Age, disability=Disability, promo=Promo, flag=flag, dest=cruise_dest)

@app.route('/returnCrewmateHome', methods=['POST', 'GET'])
def returnCrewmateHome():
	try:
		mysqldb = mysql.connect()
		mycursor = mysqldb.cursor()

		UserID = request.form['user']
		Dept = request.form['dept']

		mycursor.execute("select ID from crewmate where ID like '______2' order by ID desc LIMIT 1")
		result = mycursor.fetchall()

		Current_Year = str(result[0][0])[0:2]
		Current_Quarter = str(result[0][0])[2]
		Current_Cruise =Current_Year + Current_Quarter

		sql = "select ID, name, origin, Experience, status, Dept_Name from crewmate where Login_ID = (%s) and ID like (%s)"
		values = (UserID, Current_Cruise + '___' + '2')
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		ID = result[0][0]
		Name = result[0][1]
		Origin = result[0][2]
		Experience = result[0][3]
		Status = result[0][4]
		Dept_Name = result[0][5]

	except Exception as e:
		return render_template('crewmateError.html', error=e, username=UserID, dept = Dept)

	sql = "select count(*) from highest_ranking_officer where Crewmate_ID = (%s)"
	values = (ID)
	mycursor.execute(sql, values)
	result = mycursor.fetchall()

	if(result[0][0] == 0):
		if(Dept_Name == 'Supplies'):
			return render_template('crewmateInventoryHome.html', username=UserID, name=Name, origin=Origin, dept=Dept_Name, exp=Experience, status=Status, dest=cruise_dest)
		elif(Dept_Name == 'Administration'):
			return render_template('crewmateAdminHome.html', username=UserID, name=Name, origin=Origin, dept=Dept_Name, exp=Experience, status=Status, dest=cruise_dest)
		elif(Dept_Name == 'Cleaning'):
			return render_template('crewmateCleaningHome.html', username=UserID, name=Name, origin=Origin, dept=Dept_Name, exp=Experience, status=Status, dest=cruise_dest)
		elif(Dept_Name == 'Engine'):
			return render_template('crewmateEngineHome.html', username=UserID, name=Name, origin=Origin, dept=Dept_Name, exp=Experience, status=Status, dest=cruise_dest)
		elif(Dept_Name == 'First Aid'):
			return render_template('crewmateFirstAidHome.html', username=UserID, name=Name, origin=Origin, dept=Dept_Name, exp=Experience, status=Status, dest=cruise_dest)
		elif(Dept_Name == 'Kitchen'):
			return render_template('crewmateKitchenHome.html', username=UserID, name=Name, origin=Origin, dept=Dept_Name, exp=Experience, status=Status, dest=cruise_dest)
		elif(Dept_Name == 'Security'):
			return render_template('crewmateSecurityHome.html', username=UserID, name=Name, origin=Origin, dept=Dept_Name, exp=Experience, status=Status, dest=cruise_dest)
		elif(Dept_Name == 'Room Service'):
			return render_template('crewmateRoomServiceHome.html', username=UserID, name=Name, origin=Origin, dept=Dept_Name, exp=Experience, status=Status, dest=cruise_dest)
		else:
			return render_template('crewmateGenericHome.html', username=UserID, name=Name, origin=Origin, dept=Dept_Name, exp=Experience, status=Status, dest=cruise_dest)
	else:
		sql = "select Officer_Rank, Designation from highest_ranking_officer where Crewmate_ID = (%s)"
		values = (ID)
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		Rank = result[0][0]
		if(Dept_Name == 'Supplies'):
			return render_template('rankingInventoryHome.html', username=UserID, name=Name, rank=Rank, origin=Origin, dept=Dept_Name, exp=Experience, status=Status, dest=cruise_dest)
		elif(Dept_Name == 'Administration'):
			return render_template('rankingAdminHome.html', username=UserID, name=Name, rank=Rank, origin=Origin, dept=Dept_Name, exp=Experience, status=Status, dest=cruise_dest)
		elif(Dept_Name == 'Cleaning'):
			return render_template('rankingCleaningHome.html', username=UserID, name=Name, rank=Rank, origin=Origin, dept=Dept_Name, exp=Experience, status=Status, dest=cruise_dest)
		elif(Dept_Name == 'Engine'):
			return render_template('rankingEngineHome.html', username=UserID, name=Name, rank=Rank, origin=Origin, dept=Dept_Name, exp=Experience, status=Status, dest=cruise_dest)
		elif(Dept_Name == 'First Aid'):
			return render_template('rankingFirstAidHome.html', username=UserID, name=Name, rank=Rank, origin=Origin, dept=Dept_Name, exp=Experience, status=Status, dest=cruise_dest)
		elif(Dept_Name == 'Kitchen'):
			return render_template('rankingKitchenHome.html', username=UserID, name=Name, rank=Rank, origin=Origin, dept=Dept_Name, exp=Experience, status=Status, dest=cruise_dest)
		elif(Dept_Name == 'Security'):
			return render_template('rankingSecurityHome.html', username=UserID, name=Name, rank=Rank, origin=Origin, dept=Dept_Name, exp=Experience, status=Status, dest=cruise_dest)
		elif(Dept_Name == 'Room Service'):
			return render_template('rankingRoomServiceHome.html', username=UserID, name=Name, rank=Rank, origin=Origin, dept=Dept_Name, exp=Experience, status=Status, dest=cruise_dest)
		elif(Dept_Name == 'Operations'):
			return render_template('rankingOperationsHome.html', username=UserID, name=Name, rank=Rank, origin=Origin, dept=Dept_Name, exp=Experience, status=Status, dest=cruise_dest)
		elif(Dept_Name == 'Acitivities'):
			return render_template('rankingActivitiesHome.html', username=UserID, name=Name, rank=Rank, origin=Origin, dept=Dept_Name, exp=Experience, status=Status, dest=cruise_dest)

@app.route('/complaintIntermediate', methods=['POST', 'GET'])
def complaintIntermediate():
	try:
		UserID = request.form['userComplain']
	except Exception as e:
		return render_template('passengerError.html', error=e, username=UserID)
	return render_template('passengerComplain.html', username=UserID)

@app.route('/passengerComplaint', methods=['POST', 'GET'])
def passengerComplaint():
	try:

		mysqldb = mysql.connect()
		mycursor = mysqldb.cursor()

		Year = request.form['Date'][2:4]
		Quarter = request.form['Quarter']
		UserID = request.form['user']
		complain = request.form['myTextArea']
		cruise = Year + Quarter

		mycursor.execute("select ID from crewmate where ID like '______2' order by ID desc LIMIT 1")
		result = mycursor.fetchall()

		Current_Year = str(result[0][0])[0:2]
		Current_Quarter = str(result[0][0])[2]
		Current_Cruise =Current_Year + Current_Quarter

		if(int(Year) != int(Current_Year)):
			return render_template('passengerError.html', error="You cannot make a complaint for a previous or future cruise.", username=UserID)

		if(int(Quarter) != int(Current_Quarter)):
			return render_template('passengerError.html', error="You cannot make a complaint for a previous or future cruise.", username=UserID)

		sql = "select ID from passenger where Login_ID = (%s) and ID like (%s)"
		values = (UserID, cruise + '___1')
		mycursor.execute(sql, values)
		result = mycursor.fetchall()

		mycursor.execute("select count(*) from Ticket")
		temp = mycursor.fetchall()


		if not result:
			return render_template('passengerError.html', error='You are not an active member of the input cruise.', username=UserID)
		
		sql = "insert into Ticket (ID, Crewmate_ID, Passenger_ID, Type, Status) values (%s, %s, %s, %s, %s)"
		values = (temp[0][0]+1,None, result[0][0], 'General Complaint', '1')
		print(values)
		mycursor.execute(sql, values)
		mysqldb.commit()

		fileHandle = open('templates\\complaints.txt', "a")
		fileHandle.write(str(result[0][0]) + " " +  str(temp[0][0]+1) + " " + complain + "\n")
		fileHandle.close()

	except Exception as e:
		return render_template('passengerError.html', error=e, username=UserID)
	finally:
		mycursor.close()
		mysqldb.close()
	return render_template('confirmPassenger.html', username=UserID, result='Your Complaint has been Registered.')

@app.route('/returnOffshoreHome', methods=['POST', 'GET'])
def returnOffshoreHome():
	return render_template('offshoreHome.html')

@app.route('/complaintInterAdmin', methods=['POST', 'GET'])
def complaintInterAdmin():
	try:
		UserID = request.form['userComp']
		Dept = request.form['DeptComp']
	except Exception as e:
		return render_template('crewmateError', error=e, username=UserID, dept=Dept)
	return render_template('complaintService.html', username=UserID, dept=Dept)

@app.route('/complaintAdminDisplay', methods=['POST', 'GET'])
def complaintAdminDisplay():
	try:
		mysqldb = mysql.connect()
		mycursor = mysqldb.cursor()
		UserID = request.form['user']
		Dept = request.form['dept']
		Year = request.form['Date'][2:4]
		Quarter = request.form['Quarter']
		cruise = Year+Quarter

		sql = "select ID, Passenger_ID from ticket where Passenger_ID like (%s) and Status = (%s) and Type = (%s)"
		values = (cruise + '___1', '1', 'General Complaint')
		mycursor.execute(sql, values)
		result = mycursor.fetchall()

		if not result:
			return render_template('confirmCrew.html', result='No Complaints to Process.', username=UserID, dept=Dept)

		listID = []

		for i in result:
			listID.append(i[0])
		print(listID)


		fileHandle = open("templates\\complaints.txt", "r")	
		lines = fileHandle.read()
		arr = lines.split("\n")

		last = []

		for i in arr:
			temp = i.split(" ")
			if len(temp) >= 3:
				print(temp)
				if int(temp[1]) in listID:
					complain = ''
					for j in range(2, len(temp)):
						complain = complain + " " + temp[j]
						if j == 6:
							break
					last.append((temp[1], temp[0], complain))
		fileHandle.close()
		print(last)

	except Exception as e:
		return render_template('crewmateError.html', error=e, username=UserID, dept=Dept)
	finally:
		mycursor.close()
		mysqldb.close()

	return render_template('complaintInter.html', tables=last, username=UserID, dept=Dept, date=request.form['Date'], quarter=Quarter)

@app.route('/complaintAdmin', methods=['POST', 'GET'])
def complaintAdmin():
	try:
		mysqldb = mysql.connect()
		mycursor = mysqldb.cursor()
		UserID = request.form['user']
		Dept = request.form['dept']
		Year = request.form['Date'][2:4]
		Quarter = request.form['Quarter']
		cruise = Year+Quarter
		Ticket = request.form['ticket']

		sql = "select ID, Passenger_ID from ticket where Passenger_ID like (%s) and Status = (%s) and Type = (%s)"
		values = (cruise + '___1', '1', 'General Complaint')
		mycursor.execute(sql, values)
		result = mycursor.fetchall()

		listID = []

		for i in result:
			listID.append(i[0])


		
		if int(Ticket) not in listID:
			return render_template('crewmateError.html', error='Invalid Ticket Number input.', username=UserID, dept=Dept)

		sql = "select ID from crewmate where Login_ID = (%s) and ID like (%s)"
		values = (UserID, cruise + '___2')
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		
		if not result:
			return render_template('crewmateError.html', error='You are not authorized to handle this request.', username=UserID, dept=Dept)

		sql = "update Ticket set Crewmate_ID = (%s) where ID = (%s)"
		values = (result[0][0], Ticket)
		mycursor.execute(sql, values)

		sql = "update Ticket set Status = (%s) where ID = (%s)"
		values = ('0', Ticket)
		mycursor.execute(sql, values)



		fileHandle = open("templates\\complaints.txt", "r")	
		lines = fileHandle.read()
		fileHandle.close()

		fileHandle = open('templates\\complaints.txt', "w")
		arr = lines.split("\n")

		for i in arr:
			temp = i.split(" ")
			if len(temp) >= 3:
				if int(temp[1]) == int(Ticket):
					continue
				else:
					fileHandle.write(i + "\n")
		fileHandle.close()
		mysqldb.commit()

	except Exception as e:
		return render_template('crewmateError.html', error=e, username=UserID, dept=Dept)
	finally:
		mycursor.close()
		mysqldb.close()

	return render_template('confirmCrew.html', result='Your Transaction has been Completed.', username=UserID, dept=Dept)

@app.route('/roomServiceIntermediate', methods=['POST', 'GET'])
def roomServiceIntermediate():
	try:
		UserID = request.form['userService']
		Name = request.form['NameService']
	except Exception as e:
		return render_template('passengerError.html', error=e, username=UserID)
	return render_template('passengerRoomServiceInter.html', username=UserID, name=Name)

@app.route('/passengerRoomServiceDisplay', methods=['POST', 'GET'])
def passengerRoomServiceDisplay():
	try:
		mysqldb = mysql.connect()
		mycursor = mysqldb.cursor()

		UserID = request.form['user']
		Name = request.form['Name']
		Year = request.form['Date'][2:4]
		Quarter = request.form['Quarter']
		cruise = Year + Quarter

		mycursor.execute("select ID from crewmate where ID like '______2' order by ID desc LIMIT 1")
		result = mycursor.fetchall()

		Current_Year = str(result[0][0])[0:2]
		Current_Quarter = str(result[0][0])[2]
		Current_Cruise =Current_Year + Current_Quarter

		if(int(Year) != int(Current_Year)):
			return render_template('passengerError.html', error="You cannot make a room service request for a cruise other than the current cruise.", username=UserID)

		if(int(Quarter) != int(Current_Quarter)):
			return render_template('passengerError.html', error="You cannot make a room service request for a cruise other than the current cruise.", username=UserID)

		sql = "select count(*) from Passenger where Login_ID = (%s) and ID like (%s)"
		values = (UserID, cruise + '___1')
		mycursor.execute(sql, values)
		result = mycursor.fetchall()

		if result[0][0] == 0:
			return render_template('passengerError.html', error='You are not an Active Member for the given Cruise.', username=UserID)

		sql = "select Room.ID, Room.Package, Room.Price from Room inner join Passenger on Room.ID = Passenger.Room_ID where Passenger.Login_ID = (%s) and  Passenger.ID like (%s) order by Room.ID asc"
		values = (UserID, cruise + '___1')
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		myRooms = []
		for i in result:
			myRooms.append(i)

	except Exception as e:
		return render_template('passengerError.html', error=e, username=UserID)
	finally:
		mycursor.close()
		mysqldb.close()
	return render_template('passengerRoomService.html', username=UserID, tables=myRooms, year=Year, quarter=Quarter)

@app.route('/passengerRoomService', methods=['POST', 'GET'])
def passengerRoomService():
	try:
		mysqldb = mysql.connect()
		mycursor = mysqldb.cursor()

		UserID = request.form['user']
		Year = request.form['Date']
		Quarter = request.form['Quarter']
		Room = request.form['Room_ID']
		cruise = Year + Quarter

		mycursor.execute("select ID from Room")
		result = mycursor.fetchall()
		registered = []
		
		for i in result:    
			rms=i[0]
			registered.append(rms)

		if int(Room) not in registered:
			return render_template('passengerError.html', error ='The given room does not exist.', username=UserID)

		sql = "select ID from Passenger where Room_ID = (%s) and ID like (%s) and Login_ID = (%s)"
		values = (Room, cruise + '___1', UserID)
		mycursor.execute(sql, values)
		result = mycursor.fetchall()

		if not result:
			return render_template('passengerError.html', error='The Input Room is not Assigned to you.', username=UserID)

		PassengerID = result[0][0]

		sql = "select count(*) from Ticket where Passenger_ID like (%s) and Type = (%s) and Status =(%s)"
		values = (result[0][0], 'Room Service', '1')
		mycursor.execute(sql, values)
		result = mycursor.fetchall()

		if result[0][0] != 0:
			return render_template('passengerError.html', error='You already have an Outstanding Room Service Request.', username=UserID)

		mycursor.execute("select count(*) from Ticket")
		temp = mycursor.fetchall()


		sql = "insert into Ticket values (%s, %s, %s, %s, %s)"
		values = (temp[0][0] + 1, None, PassengerID, 'Room Service', '1')
		mycursor.execute(sql, values)
		mysqldb.commit()
		

	except Exception as e:
		return render_template('passengerError.html', error=e, username=UserID)
	finally:
		mycursor.close()
		mysqldb.close()
	return render_template('confirmPassenger.html', result='Your Request has been Registered.' ,username=UserID)

@app.route('/crewmateRoomServiceIntermediate', methods=['POST', 'GET'])
def crewmateRoomServiceIntermediate():
	try:
		mysqldb = mysql.connect()
		mycursor = mysqldb.cursor()

		UserID = request.form['userService']
		Dept = request.form['DeptService']

		print(UserID, Dept)

		mycursor.execute("select ID from crewmate where ID like '______2' order by ID desc LIMIT 1")
		result = mycursor.fetchall()

		Current_Year = str(result[0][0])[0:2]
		Current_Quarter = str(result[0][0])[2]
		Current_Cruise =Current_Year + Current_Quarter

		sql = "select Ticket.ID, Ticket.Passenger_ID, Passenger.Room_ID from Ticket inner join Passenger on Ticket.Passenger_ID = Passenger.ID where Ticket.Passenger_ID like (%s) and Ticket.Type = (%s) and Ticket.Status = (%s)"
		values = (Current_Cruise + '___' + '1', 'Room Service', '1')
		mycursor.execute(sql, values)
		result = mycursor.fetchall()

		if not result:
			return render_template('confirmCrew.html', result='No Room Service Requests to Process.', username=UserID, dept=Dept)

		requests = []
		for i in result:
			requests.append(i)

	except Exception as e:
		return render_template('crewmateError.html', error=e, username=UserID, dept=Dept)
	finally:
		mycursor.close()
		mysqldb.close()

	return render_template('crewmateRoomServiceHandle.html', username=UserID, dept=Dept, tables = requests)

@app.route('/crewmateRoomServiceHandle', methods=['POST', 'GET'])
def crewmateRoomServiceHandle():
	try:
		mysqldb = mysql.connect()
		mycursor = mysqldb.cursor()
		UserID = request.form['user']
		Dept = request.form['dept']
		print(UserID, Dept)

		mycursor.execute("select ID from crewmate where ID like '______2' order by ID desc LIMIT 1")
		result = mycursor.fetchall()

		Current_Year = str(result[0][0])[0:2]
		Current_Quarter = str(result[0][0])[2]
		Current_Cruise =Current_Year + Current_Quarter

		Ticket = request.form['ticket']

		sql = "select Ticket.ID, Ticket.Passenger_ID, Passenger.Room_ID from Ticket inner join Passenger on Ticket.Passenger_ID = Passenger.ID where Ticket.Passenger_ID like (%s) and Ticket.Type = (%s) and Ticket.Status = (%s)"
		values = (Current_Cruise + '___1', 'Room Service', '1')
		mycursor.execute(sql, values)
		result = mycursor.fetchall()

		listID = []

		for i in result:
			listID.append(i[0])
		
		if int(Ticket) not in listID:
			return render_template('crewmateError.html', error='Invalid Ticket Number input.', username=UserID, dept=Dept)

		sql = "select ID from crewmate where Login_ID = (%s) and ID like (%s)"
		values = (UserID, Current_Cruise + '___2')
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		
		if not result:
			return render_template('crewmateError.html', error='You are not authorized to handle this request.', username=UserID, dept=Dept)

		sql = "update Ticket set Crewmate_ID = (%s) where ID = (%s)"
		values = (result[0][0], Ticket)
		mycursor.execute(sql, values)

		sql = "update Ticket set Status = (%s) where ID = (%s)"
		values = ('0', Ticket)
		mycursor.execute(sql, values)
		mysqldb.commit()

	except Exception as e:
		return render_template('crewmateError.html', error=e, username=UserID, dept=Dept)
	finally:
		mycursor.close()
		mysqldb.close()

	return render_template('confirmCrew.html', result='Your Transaction has been Completed.', username=UserID, dept=Dept)

@app.route('/insertInventoryInter', methods=['POST', 'GET']) #MY SHIT STARTS FROM HERE.
def insertInventoryInter():
	try:
		mysqldb = mysql.connect()
		mycursor = mysqldb.cursor()

		UserID = request.form['userBook']
		Dept = request.form['DeptBook']


		mycursor.execute('select count(*) from inventory')	#Takes count of item in inventory and increments by 1. Passes this to Insertion page.
		result = mycursor.fetchall()

		numitem = result[0][0] + 1

		mycursor.execute('select * from inventory') #Takes all the display data for the table and passes it on.
		result = mycursor.fetchall()

		itemList = []
		for i in result:
			itemList.append(i)

	except Exception as e:
		return render_template('crewmateError.html', error=e, username=UserID, dept=Dept)

	finally:
		mycursor.close() 
		mysqldb.close()
	return render_template('insertInventory.html', username=UserID, dept=Dept, itemnum=numitem, tables=itemList)

@app.route('/insertInventory', methods=['POST', 'GET'])
def insertInventory():
	try:
		mysqldb = mysql.connect()
		mycursor = mysqldb.cursor()

		UserID = request.form['user']
		UserDept = request.form['dept']

		ItemNum = request.form['itemnum']

		Name = request.form['Name']
		Quantity = request.form['Quantity']
		Weight = request.form['Weight']
		Status = request.form['Status']
		Description = request.form['Description']

		temp = request.form
		Freight = 0
		if temp.get('Freight'):
			Freight = 1

		Department = request.form['Department']
		sql = "select count(*) from inventory where Name = (%s)"
		values = (Name)
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		if(result[0][0] == 0):
			sql = "insert into inventory values (%s, %s, %s, %s, %s, %s, %s, %s)"
			values = (ItemNum, Name, Quantity, Weight, Status, Description, Freight, Department)
			mycursor.execute(sql, values)
			mysqldb.commit()
		elif(result[0][0] > 0):
			return render_template('crewmateError.html', error ='The item already exists. Use the Update menu instead.', username=UserID,dept=UserDept)

	except Exception as e:
		return render_template('crewmateError.html', error=e, username=UserID, dept=UserDept)

	finally:
		mycursor.close() 
		mysqldb.close()
	return render_template('confirmCrew.html', result='Your Transaction has been Completed.', username=UserID, dept=UserDept)

@app.route('/deleteInventoryInter', methods=['POST', 'GET'])
def deleteInventoryInter():
	try:
		mysqldb = mysql.connect()
		mycursor = mysqldb.cursor()

		UserID = request.form['userDel']
		Dept = request.form['DeptDel']

		mycursor.execute('select count(*) from inventory')	#Takes count of item in inventory and increments by 1. Passes this to Insertion page.
		result = mycursor.fetchall()

		numitem = result[0][0] + 1

		mycursor.execute('select * from inventory')
		result = mycursor.fetchall()

		itemList = []
		for i in range(0, numitem - 1):
			itemList.append(result[i])

	except Exception as e:
		return render_template('crewmateError.html', error=e, username=UserID, dept=Dept)

	finally:
		mycursor.close() 
		mysqldb.close()
	return render_template('deleteInventory.html', username=UserID, dept=Dept, tables=itemList)

@app.route('/deleteInventory', methods=['POST', 'GET'])
def deleteInventory():
	try:
		mysqldb = mysql.connect()
		mycursor = mysqldb.cursor()

		UserID = request.form['user']
		UserDept = request.form['dept']

		ItemID = request.form['ID']

		sql = "select count(*) from inventory where ID = (%s)"
		values = (ItemID)
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		if(result[0][0] == 1):
			sql = "update inventory set Quantity_Present = 0 where ID = (%s)"
			mycursor.execute(sql, ItemID)
			mysqldb.commit()
		elif(result[0][0] == 0):
			return render_template('crewmateError.html', error ='The item does not exist in the inventory.', username=UserID, dept=UserDept)

	except Exception as e:
		return render_template('crewmateError.html', error=e, username = UserID, dept=UserDept)

	finally:
		mycursor.close() 
		mysqldb.close()
	return render_template('confirmCrew.html', result='Your Transaction has been Completed.', username=UserID, dept=UserDept)

@app.route('/updateInventoryInter', methods=['POST', 'GET'])
def updateInventoryInter():
	try:
		mysqldb = mysql.connect()
		mycursor = mysqldb.cursor()

		UserID = request.form['userUPG']
		Dept = request.form['DeptUPG']

		mycursor.execute('select count(*) from inventory')	#Takes count of item in inventory and increments by 1. Passes this to Insertion page.
		result = mycursor.fetchall()

		numitem = result[0][0] + 1

		mycursor.execute('select * from inventory')
		result = mycursor.fetchall()

		itemList = []
		for i in range(0, numitem):
			itemList.append(result[i])

	except Exception as e:
		return render_template('error.html', error=e)

	finally:
		mycursor.close() 
		mysqldb.close()
		return render_template('updateInventory.html', username=UserID, dept=Dept, tables=itemList)

@app.route('/updateInventory', methods=['POST', 'GET'])
def updateInventory():
	try:
		mysqldb = mysql.connect()
		mycursor = mysqldb.cursor()

		UserID = request.form['user']
		UserDept = request.form['dept']

		ItemID = request.form['ID']
		Name = request.form['Name']
		Quantity = request.form['Quantity']
		Weight = request.form['Weight']
		Status = request.form['Status']
		Description = request.form['Description']

		temp = request.form
		Freight = 0
		if temp.get('Freight'):
			Freight = 1

		Department = request.form['Department']

		sql = "select count(*), ID from inventory where Name = (%s)"
		values = (Name)
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		if(result[0][0] == 1):
			if(result[0][1] != int(ItemID)):
				return render_template('crewmateError.html', error ='The item already exists in the inventory.', username=UserID, dept=UserDept)

		sql = "select count(*) from inventory where ID = (%s)"
		values = (ItemID)
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		if(result[0][0] == 1):
			sql = "update inventory set Name = (%s), Quantity_Present = (%s), Weight = (%s), Status = (%s), Description = (%s), Is_Freight = (%s), Dept_name = (%s)  where ID = (%s)"
			values = (Name, Quantity, Weight, Status, Description, Freight, Department, ItemID)
			mycursor.execute(sql, values)
			mysqldb.commit()
		elif(result[0][0] == 0):
			return render_template('crewmateError.html', error ='The item does not exist in the inventory.', username=UserID, dept=UserDept)

	except Exception as e:
		return render_template('crewmateError.html', error=e, username=UserID, dept=UserDept)

	finally:
		mycursor.close()
		mysqldb.close()
	return render_template('confirmCrew.html', result='Your Transaction has been Completed.', username=UserID, dept=UserDept)

@app.route('/insertInventoryInterDept', methods=['POST', 'GET']) #MY SHIT STARTS FROM HERE.
def insertInventoryInterDept():
	try:
		mysqldb = mysql.connect()
		mycursor = mysqldb.cursor()

		UserID = request.form['userBook']
		Dept = request.form['DeptBook']


		mycursor.execute('select count(*) from inventory')	#Takes count of item in inventory and increments by 1. Passes this to Insertion page.
		result = mycursor.fetchall()

		numitem = result[0][0] + 1

		sql = "select ID, Name, Quantity_Present, Weight, Status, Description from inventory where Dept_name = (%s)" #Takes all the display data for the table and passes it on.
		values = (Dept)
		mycursor.execute(sql, values)
		result = mycursor.fetchall()

		itemList = []
		for i in result:
			itemList.append(i)

	except Exception as e:
		return render_template('crewmateError.html', error=e, username=UserID, dept=Dept)

	finally:
		mycursor.close() 
		mysqldb.close()
	return render_template('insertInventoryDept.html', username=UserID, dept=Dept, itemnum=numitem, tables=itemList)

@app.route('/insertInventoryDept', methods=['POST', 'GET'])
def insertInventoryDept():
	try:
		mysqldb = mysql.connect()
		mycursor = mysqldb.cursor()

		UserID = request.form['user']
		UserDept = request.form['dept']

		ItemNum = request.form['itemnum']

		Name = request.form['Name']
		Quantity = request.form['Quantity']
		Weight = request.form['Weight']
		Status = request.form['Status']
		Description = request.form['Description']

		sql = "select count(*) from inventory where Name = (%s)"
		values = (Name)
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		if(result[0][0] == 0):
			sql = "insert into inventory values (%s, %s, %s, %s, %s, %s, %s, %s)"
			values = (ItemNum, Name, Quantity, Weight, Status, Description, 0, UserDept)
			mycursor.execute(sql, values)
			mysqldb.commit()
		elif(result[0][0] > 0):
			return render_template('crewmateError.html', error ='The item already exists. Use the Update menu instead.', username=UserID,dept=UserDept)

	except Exception as e:
		return render_template('crewmateError.html', error=e, username=UserID, dept=UserDept)

	finally:
		mycursor.close() 
		mysqldb.close()
	return render_template('confirmCrew.html', result='Your Transaction has been Completed.', username=UserID, dept=UserDept)

@app.route('/deleteInventoryInterDept', methods=['POST', 'GET'])
def deleteInventoryInterDept():
	try:
		mysqldb = mysql.connect()
		mycursor = mysqldb.cursor()

		UserID = request.form['userDel']
		Dept = request.form['DeptDel']

		mycursor.execute('select count(*) from inventory')	#Takes count of item in inventory and increments by 1. Passes this to Insertion page.
		result = mycursor.fetchall()

		numitem = result[0][0] + 1

		sql = "select ID, Name, Quantity_Present, Weight, Status, Description from inventory where Dept_name = (%s)" #Takes all the display data for the table and passes it on.
		values = (Dept)
		mycursor.execute(sql, values)
		result = mycursor.fetchall()

		itemList = []
		for i in result:
			itemList.append(i)

	except Exception as e:
		return render_template('crewmateError.html', error=e, username=UserID, dept=Dept)

	finally:
		mycursor.close() 
		mysqldb.close()
	return render_template('deleteInventoryDept.html', username=UserID, dept=Dept, tables=itemList)

@app.route('/deleteInventoryDept', methods=['POST', 'GET'])
def deleteInventoryDept():
	try:
		mysqldb = mysql.connect()
		mycursor = mysqldb.cursor()

		UserID = request.form['user']
		UserDept = request.form['dept']

		ItemID = request.form['ID']

		sql = "select count(ID) from inventory where Dept_name = (%s) and ID = (%s)"
		values = (UserDept, ItemID)
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		print(result[0][0])
		if(result[0][0] == 0):
			return render_template('crewmateError.html', error ='The provided item ID does not belong to your department.', username=UserID, dept=UserDept)

		sql = "select count(*) from inventory where ID = (%s)"
		values = (ItemID)
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		if(result[0][0] == 1):
			sql = "update inventory set Quantity_Present = 0 where ID = (%s)"
			mycursor.execute(sql, ItemID)
			mysqldb.commit()
		elif(result[0][0] == 0):
			return render_template('crewmateError.html', error ='The item does not exist in the inventory.', username=UserID, dept=UserDept)

	except Exception as e:
		return render_template('crewmateError.html', error=e, username = UserID, dept=UserDept)

	finally:
		mycursor.close() 
		mysqldb.close()
	return render_template('confirmCrew.html', result='Your Transaction has been Completed.', username=UserID, dept=UserDept)

@app.route('/updateInventoryInterDept', methods=['POST', 'GET'])
def updateInventoryInterDept():
	try:
		mysqldb = mysql.connect()
		mycursor = mysqldb.cursor()

		UserID = request.form['userUPG']
		Dept = request.form['DeptUPG']

		mycursor.execute('select count(*) from inventory')	#Takes count of item in inventory and increments by 1. Passes this to Insertion page.
		result = mycursor.fetchall()

		numitem = result[0][0] + 1

		sql = "select ID, Name, Quantity_Present, Weight, Status, Description from inventory where Dept_name = (%s)" #Takes all the display data for the table and passes it on.
		values = (Dept)
		mycursor.execute(sql, values)
		result = mycursor.fetchall()

		itemList = []
		for i in result:
			itemList.append(i)

	except Exception as e:
		return render_template('error.html', error=e)

	finally:
		mycursor.close() 
		mysqldb.close()
		return render_template('updateInventoryDept.html', username=UserID, dept=Dept, tables=itemList)

@app.route('/updateInventoryDept', methods=['POST', 'GET'])
def updateInventoryDept():
	try:
		mysqldb = mysql.connect()
		mycursor = mysqldb.cursor()

		UserID = request.form['user']
		UserDept = request.form['dept']

		ItemID = request.form['ID']
		Name = request.form['Name']
		Quantity = request.form['Quantity']
		Weight = request.form['Weight']
		Status = request.form['Status']
		Description = request.form['Description']
		
		sql = "select count(ID) from inventory where Dept_name = (%s) and ID = (%s)"
		values = (UserDept, ItemID)
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		print(result[0][0])
		if(result[0][0] == 0):
			return render_template('crewmateError.html', error ='The provided item ID does not belong to your department.', username=UserID, dept=UserDept)

		sql = "select count(*), ID from inventory where Name = (%s)"
		values = (Name)
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		if(result[0][0] == 1):
			if(result[0][1] != int(ItemID)):
				return render_template('crewmateError.html', error ='The item already exists in the inventory.', username=UserID, dept=UserDept)

		sql = "select count(*) from inventory where ID = (%s)"
		values = (ItemID)
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		if(result[0][0] == 1):
			sql = "update inventory set Name = (%s), Quantity_Present = (%s), Weight = (%s), Status = (%s), Description = (%s) where ID = (%s)"
			values = (Name, Quantity, Weight, Status, Description, ItemID)
			mycursor.execute(sql, values)
			mysqldb.commit()
		elif(result[0][0] == 0):
			return render_template('crewmateError.html', error ='The item does not exist in the inventory.', username=UserID, dept=UserDept)

	except Exception as e:
		return render_template('crewmateError.html', error=e, username=UserID, dept=UserDept)

	finally:
		mycursor.close()
		mysqldb.close()
	return render_template('confirmCrew.html', result='Your Transaction has been Completed.', username=UserID, dept=UserDept)

@app.route('/insertFreightInter', methods=['POST', 'GET']) #MY SHIT STARTS FROM HERE.
def insertFreightInter():
	try:
		mysqldb = mysql.connect()
		mycursor = mysqldb.cursor()

		UserID = request.form['userFBook']
		Dept = request.form['DeptFBook']

		mycursor.execute('select count(*) from inventory')	#Takes count of item in inventory and increments by 1. Passes this to Insertion page.
		result = mycursor.fetchall()

		numitem = result[0][0] + 1

		mycursor.execute('select ID, Name, Quantity_Present, Weight, Status, Description, Luggage, Destination from inventory, freight where inventory.ID = freight.Inventory_ID') #Takes all the display data for the table and passes it on.
		result = mycursor.fetchall()

		itemList = []
		for i in result:
			itemList.append(i)

	except Exception as e:
		return render_template('crewmateError.html', error=e, username=UserID, dept=Dept)

	finally:
		mycursor.close() 
		mysqldb.close()
	return render_template('insertFreight.html', username=UserID, dept=Dept, itemnum=numitem, tables=itemList)

@app.route('/insertFreight', methods=['POST', 'GET'])
def insertFreight():
	try:
		mysqldb = mysql.connect()
		mycursor = mysqldb.cursor()

		UserID = request.form['user']
		UserDept = request.form['dept']

		ItemNum = request.form['itemnum']

		Name = request.form['Name']
		Quantity = request.form['Quantity']
		Weight = request.form['Weight']
		Status = request.form['Status']
		Description = request.form['Description']


		temp = request.form
		Luggage = 0
		if temp.get('Luggage'):
			Luggage = 1

		Destination = request.form['Destination']
		mycursor.execute("select Name from Location")
		result = mycursor.fetchall()
		countries = []
		for i in result:
			countries.append(i[0])
		if Destination not in countries:
			return render_template('crewmateError.html', error='The input Location is invalid.', username=UserID, dept=UserDept)


		sql = "select count(*) from inventory where Name = (%s)"
		values = (Name)
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		print(ItemNum, Name, Quantity, Weight, Status, Description, 1, UserDept, Luggage, Destination)
		if(result[0][0] == 0):
			sql = "insert into inventory values (%s, %s, %s, %s, %s, %s, %s, %s)"
			values = (ItemNum, Name, Quantity, Weight, Status, Description, 1, UserDept)
			mycursor.execute(sql, values)
			#mysqldb.commit()
			sql = "insert into freight values (%s, %s, %s)"
			values = (ItemNum, Luggage, Destination)
			mycursor.execute(sql, values)
			mysqldb.commit()
		elif(result[0][0] > 0):
			return render_template('crewmateError.html', error ='The item already exists. Use the Update menu instead.', username=UserID,dept=UserDept)

	except Exception as e:
		return render_template('crewmateError.html', error=e, username=UserID, dept=UserDept)

	finally:
		mycursor.close() 
		mysqldb.close()
	return render_template('confirmCrew.html', result='Your Transaction has been Completed.', username=UserID, dept=UserDept)

@app.route('/deleteFreightInter', methods=['POST', 'GET'])
def deleteFreightInter():
	try:
		mysqldb = mysql.connect()
		mycursor = mysqldb.cursor()

		UserID = request.form['userFDel']
		Dept = request.form['DeptFDel']

		mycursor.execute('select count(*) from inventory')	#Takes count of item in inventory and increments by 1. Passes this to Insertion page.
		result = mycursor.fetchall()

		numitem = result[0][0] + 1

		mycursor.execute('select ID, Name, Quantity_Present, Weight, Status, Description, Luggage, Destination from inventory, freight where inventory.ID = freight.Inventory_ID')
		result = mycursor.fetchall()

		itemList = []
		for i in result:
			itemList.append(i)

	except Exception as e:
		return render_template('crewmateError.html', error=e, username=UserID, dept=Dept)

	finally:
		mycursor.close() 
		mysqldb.close()
	return render_template('deleteFreight.html', username=UserID, dept=Dept, tables=itemList)

@app.route('/deleteFreight', methods=['POST', 'GET'])
def deleteFreight():
	try:
		mysqldb = mysql.connect()
		mycursor = mysqldb.cursor()

		UserID = request.form['user']
		UserDept = request.form['dept']

		ItemID = request.form['ID']

		sql = "select count(ID) from inventory where Dept_name = (%s) and Is_Freight = 1 and ID = (%s)"
		values = (UserDept, ItemID)
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		print(result[0][0])
		if(result[0][0] == 0):
			return render_template('crewmateError.html', error ='The provided item ID is not a freight item.', username=UserID, dept=UserDept)

		sql = "select count(*) from inventory where ID = (%s)"
		values = (ItemID)
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		if(result[0][0] == 1):
			sql = "update inventory set Quantity_Present = 0 where ID = (%s)"
			mycursor.execute(sql, ItemID)
			mysqldb.commit()
		elif(result[0][0] == 0):
			return render_template('crewmateError.html', error ='The item does not exist in the inventory.', username=UserID, dept=UserDept)

	except Exception as e:
		return render_template('crewmateError.html', error=e, username = UserID, dept=UserDept)

	finally:
		mycursor.close() 
		mysqldb.close()
	return render_template('confirmCrew.html', result='Your Transaction has been Completed.', username=UserID, dept=UserDept)

@app.route('/updateFreightInter', methods=['POST', 'GET'])
def updateFreightInter():
	try:
		mysqldb = mysql.connect()
		mycursor = mysqldb.cursor()

		UserID = request.form['userFUPG']
		Dept = request.form['DeptFUPG']

		mycursor.execute('select count(*) from inventory')	#Takes count of item in inventory and increments by 1. Passes this to Insertion page.
		result = mycursor.fetchall()

		numitem = result[0][0] + 1

		mycursor.execute('select ID, Name, Quantity_Present, Weight, Status, Description, Luggage, Destination from inventory, freight where inventory.ID = freight.Inventory_ID')
		result = mycursor.fetchall()

		itemList = []
		for i in result:
			itemList.append(i)

	except Exception as e:
		return render_template('error.html', error=e)

	finally:
		mycursor.close() 
		mysqldb.close()
		return render_template('updateFreight.html', username=UserID, dept=Dept, tables=itemList)

@app.route('/updateFreight', methods=['POST', 'GET'])
def updateFreight():
	try:
		mysqldb = mysql.connect()
		mycursor = mysqldb.cursor()

		UserID = request.form['user']
		UserDept = request.form['dept']

		ItemID = request.form['ID']
		Name = request.form['Name']
		Quantity = request.form['Quantity']
		Weight = request.form['Weight']
		Status = request.form['Status']
		Description = request.form['Description']
		Destination = request.form['Destination']
		Destination = request.form['Destination']
		mycursor.execute("select Name from Location")
		result = mycursor.fetchall()
		countries = []
		for i in result:
			countries.append(i[0])
		if Destination not in countries:
			return render_template('crewmateError.html', error='The input Location is invalid.', username=UserID, dept=UserDept)


		temp = request.form
		Luggage = 0
		if temp.get('Luggage'):
			Luggage = 1

		sql = "select count(ID) from inventory where Dept_name = (%s) and Is_Freight = 1 and ID = (%s)"
		values = (UserDept, ItemID)
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		print(result[0][0])
		if(result[0][0] == 0):
			return render_template('crewmateError.html', error ='The provided item ID is not a freight item.', username=UserID, dept=UserDept)

		sql = "select count(*), ID from inventory where Name = (%s)"
		values = (Name)
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		if(result[0][0] == 1):
			if(result[0][1] != int(ItemID)):
				return render_template('crewmateError.html', error ='The item already exists in the inventory.', username=UserID, dept=UserDept)

		sql = "select count(*) from inventory where ID = (%s)"
		values = (ItemID)
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		if(result[0][0] == 1):
			sql = "update inventory set Name = (%s), Quantity_Present = (%s), Weight = (%s), Status = (%s), Description = (%s) where ID = (%s)"
			values = (Name, Quantity, Weight, Status, Description, ItemID)
			mycursor.execute(sql, values)
			mysqldb.commit()
			sql = "update freight set Luggage = (%s), Destination = (%s)  where Inventory_ID = (%s)"
			values = (Luggage, Destination, ItemID)
			mycursor.execute(sql, values)
			mysqldb.commit()
		elif(result[0][0] == 0):
			return render_template('crewmateError.html', error ='The item does not exist in the inventory.', username=UserID, dept=UserDept)

	except Exception as e:
		return render_template('crewmateError.html', error=e, username=UserID, dept=UserDept)

	finally:
		mycursor.close()
		mysqldb.close()
	return render_template('confirmCrew.html', result='Your Transaction has been Completed.', username=UserID, dept=UserDept)

@app.route('/insertMenuScheduleInter', methods=['POST', 'GET'])
def insertMenuScheduleInter():
	try:
		mysqldb = mysql.connect()
		mycursor = mysqldb.cursor()

		UserID = request.form['userMenuInsert']
		Dept = request.form['DeptMenuInsert']

		mycursor.execute("select distinct Name from Menu order by Name asc")
		result = mycursor.fetchall()

		arr = []
		for i in result:
			arr.append(i[0])

		mycursor.close()
		mysqldb.close()

	except Exception as e:
		return render_template('crewmateError.html', error=e, username=UserID, dept=Dept)

	return render_template('insertMenu.html', username=UserID, dept=Dept, food=arr)

@app.route('/insertMenu', methods=['POST', 'GET'])
def insertMenu():
	try:
		mysqldb = mysql.connect()
		mycursor = mysqldb.cursor()

		UserID = request.form['user']
		Dept = request.form['dept']
		Name = request.form['Name']

		Monday = ''
		if request.form.get('Monday'):
			Monday = 'M'

		Tuesday = ''
		if request.form.get('Tuesday'):
			Tuesday = 'T'

		Wednesday = ''
		if request.form.get('Wednesday'):
			Wednesday = 'W'

		Thursday = ''
		if request.form.get('Thursday'):
			Thursday = 'R'

		Friday = ''
		if request.form.get('Friday'):
			Friday = 'F'

		Saturday = ''
		if request.form.get('Saturday'):
			Saturday = 'S'

		Sunday = ''
		if request.form.get('Sunday'):
			Sunday = 'U'
		
		Day = Monday +  Tuesday +  Wednesday +  Thursday +  Friday +  Saturday + Sunday
		if Day == '':
			return render_template('crewmateError.html', error='You did not select a Day.', username=UserID, dept=Dept)

		Breakfast = 0
		if request.form.get('Breakfast'):
			Breakfast = 1

		Lunch = 0
		if request.form.get('Lunch'):
			Lunch = 1

		Dinner = 0
		if request.form.get('Dinner'):
			Dinner = 1

		if Dinner == 0 and Lunch == 0 and Breakfast == 0:
			return render_template('crewmateError.html', error='You did not select either Breakfast, Dinner, or Lunch.', username=UserID, dept=Dept)

		mycursor.execute("select Name from Menu order by Name asc")
		result = mycursor.fetchall()

		arr = []
		for i in result:
			arr.append(i[0])

		print(arr)

		if Name in arr:
			return render_template('crewmateError.html', error='Item already exists.', username=UserID, dept=Dept)

		mycursor.execute("select count(*) from Menu")
		result = mycursor.fetchall()

		new_id = result[0][0] + 1

		sql = "select ID from Crewmate where Login_ID = (%s) and Status = (%s) and ID like (%s)"
		values = (UserID, '1', '203___2')
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		print("here")
		sql = "insert into Menu values (%s, %s, %s, %s, %s, %s, %s)"
		values = (new_id, Name, Day, Breakfast, Lunch, Dinner, result[0][0])
		mycursor.execute(sql, values)

		mysqldb.commit()

		mycursor.close()
		mysqldb.close()

	except Exception as e:
		return render_template('crewmateError.html', error=e, username=UserID, dept=Dept)

	return render_template('confirmCrew.html', result='Your Transaction has been Completed.', username=UserID, dept=Dept)

@app.route('/updateMenuScheduleInter', methods=['POST', 'GET'])
def updateMenuScheduleInter():
	try:
		mysqldb = mysql.connect()
		mycursor = mysqldb.cursor()

		UserID = request.form['userMenuUpdate']
		Dept = request.form['DeptMenuUpdate']

		mycursor.execute("select ID, Name, Day, Breakfast, Lunch, Dinner from Menu order by ID asc")
		result = mycursor.fetchall()

		arr = []
		for i in result:
			arr.append(i)

		mycursor.close()
		mysqldb.close()

	except Exception as e:
		return render_template('crewmateError.html', error=e, username=UserID, dept=Dept)

	return render_template('updateMenu.html', username=UserID, dept=Dept, food=arr)

@app.route('/updateMenu', methods=['POST', 'GET'])
def updateMenu():
	try:
		mysqldb = mysql.connect()
		mycursor = mysqldb.cursor()

		UserID = request.form['user']
		Dept = request.form['dept']
		ID = request.form['ID']
		Day = ''

		Monday = ''
		if request.form.get('Monday'):
			Monday = 'M'

		Tuesday = ''
		if request.form.get('Tuesday'):
			Tuesday = 'T'

		Wednesday = ''
		if request.form.get('Wednesday'):
			Wednesday = 'W'

		Thursday = ''
		if request.form.get('Thursday'):
			Thursday = 'R'

		Friday = ''
		if request.form.get('Friday'):
			Friday = 'F'

		Saturday = ''
		if request.form.get('Saturday'):
			Saturday = 'S'

		Sunday = ''
		if request.form.get('Sunday'):
			Sunday = 'U'
		
		Day = Monday +  Tuesday +  Wednesday +  Thursday +  Friday +  Saturday + Sunday

		if Day == '':
			return render_template('crewmateError.html', error='You did not select a Day.', username=UserID, dept=Dept)


		Breakfast = 0
		if request.form.get('Breakfast'):
			Breakfast = 1

		Lunch = 0
		if request.form.get('Lunch'):
			Lunch = 1

		Dinner = 0
		if request.form.get('Dinner'):
			Dinner = 1

		if Dinner == 0 and Lunch == 0 and Breakfast == 0:
			return render_template('crewmateError.html', error='You did not select either Breakfast, Dinner, or Lunch.', username=UserID, dept=Dept)

		mycursor.execute('select count(*) from Menu')
		result = mycursor.fetchall()

		if result[0][0] < int(ID):
			return render_template('crewmateError.html', error='Item does not exist.', username=UserID, dept=Dept)

		print(result)
		print("yosh")
		sql = "update Menu set Day = (%s) where ID = (%s)"
		values = (Day, ID)
		mycursor.execute(sql, values)

		sql = "update Menu set Breakfast = (%s) where ID = (%s)"
		values = (Breakfast, ID)
		mycursor.execute(sql,values)

		sql = "update Menu set Dinner = (%s) where ID = (%s)"
		values = (Dinner, ID)
		mycursor.execute(sql, values)

		sql = "update Menu set Lunch = (%s) where ID = (%s)"
		values = (Lunch, ID)
		mycursor.execute(sql, values)

		mysqldb.commit()

		mycursor.close()
		mysqldb.close()

	except Exception as e:
		return render_template('crewmateError.html', error=e, username=UserID, dept=Dept)

	return render_template('confirmCrew.html', result='Your Transaction has been Completed.', username=UserID, dept=Dept)

@app.route('/routingJourneyInter', methods=['POST', 'GET'])
def routingJourneyInter():
	try:
		UserID = request.form['userMap']
		UserDept = request.form['DeptMap']

	except Exception as e:
		return render_template('crewmateError.html', error=e, username=UserID, dept=UserDept)

	print(UserID, UserDept)
	return render_template('routingJourney.html', username=UserID, dept=UserDept)

@app.route('/routingJourney', methods=['POST', 'GET'])
def routingJourney():
	try:
		global cruise_dest
		mysqldb = mysql.connect()
		mycursor = mysqldb.cursor()

		UserID = request.form['user']
		UserDept = request.form['dept']
		Start = request.form['Departure']
		End = request.form['Arrival']

		print(Start, End)

		if(Start == End):
			return render_template('crewmateError.html', error='The Destination and Source are the same.', username=UserID, dept=UserDept)

		sql = "select count(*) from Location where Name = (%s)"
		values = (Start)
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		if(result[0][0] == 0):
			return render_template('crewmateError.html', error='The departure country entered either does not exist or is land-locked.', username=UserID, dept=UserDept)

		sql = "select count(*) from Location where Name = (%s)"
		values = (End)
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		if(result[0][0] == 0):
			return render_template('crewmateError.html', error='The arrival country entered either does not exist or is land-locked.', username=UserID, dept=UserDept)

		sql = "select latitude, longitude from Location where Name = (%s)"
		values = Start
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		DepartLat = result[0][0]
		DepartLon = result[0][1]

		sql = "select latitude, longitude from Location where Name = (%s)"
		values = End
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		ArriveLat = result[0][0]
		ArriveLon = result[0][1]

		sql = "select count(*) from route where Source = %s and Destination = (%s)"
		values = (Start, End)
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		if(result[0][0] == 1):
			'''Countrycoord = open('default_country.txt', "w")
			Countrycoord.write(str(DepartLat))
			Countrycoord.write('')
			Countrycoord.write(str(DepartLon))
			Countrycoord.close()'''
			#setCountry(DepartLat, DepartLon)
			cruise_dest = [DepartLon, DepartLat]
			return render_template('confirmCrew.html', result='This route already exists. Transaction completed.', username=UserID, dept=UserDept)

		Distance = int(math.sqrt(pow(ArriveLon - DepartLon, 2) + pow(ArriveLat - DepartLat, 2)))
		'''
		Countrycoord = open('default_country.txt', "w")
		Countrycoord.write(str(DepartLat))
		Countrycoord.write('')
		Countrycoord.write(str(DepartLon))
		Countrycoord.close()'''
		#setCountry(DepartLat, DepartLon)
		
		cruise_dest = [DepartLon, DepartLat]

		#print(cr)
		sql = "insert into Route values (%s, %s, %s)"
		values = (Start, End, Distance)
		mycursor.execute(sql, values)
		mysqldb.commit()

	except Exception as e:
		return render_template('crewmateError.html', error=e, username=UserID, dept=UserDept)
	finally:
		mycursor.close()
		mysqldb.close()
	return render_template('confirmCrew.html', result = 'Transaction completed.', username=UserID, dept=UserDept)

@app.route('/viewMenuInter', methods=['POST', 'GET'])
def viewMenuInter():
	if request.form['userCategory'] == '1':
		UserID = request.form['userMenu']
		return render_template('viewMenuPassengerInter.html', username=UserID)
	else:
		UserID = request.form['userMenu']
		Dept = request.form['DeptMenu']
		return render_template('viewMenuCrewmateInter.html', username=UserID, dept=Dept)

@app.route('/viewMenuPassenger',methods=['POST', 'GET'])
def viewMenuPassenger():
	try:
		UserID = request.form['user']
		Day = request.form['Day']

		if Day == 'Monday':
			Day = 'M'
		elif Day == 'Tuesday':
			Day = 'T'
		elif Day == 'Wednesday':
			Day = 'W'
		elif Day == 'Thursday':
			Day = 'R'
		elif Day == 'Friday':
			Day = 'F'
		elif Day == 'Saturday':
			Day = 'S'
		else:
			Day = 'U'

		mysqldb = mysql.connect()
		mycursor = mysqldb.cursor()

		sql = "select distinct Name from Menu where Day like (%s) and Breakfast = (%s) order by Name asc"
		values = ('%'+Day+'%', '1')
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		breakfast = []

		for i in result:
			breakfast.append(i[0])

		sql = "select distinct Name from Menu where Day like (%s) and Lunch = (%s) order by Name asc"
		values = ('%'+Day+'%', '1')
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		lunch = []

		for i in result:
			lunch.append(i[0])

		sql = "select distinct Name from Menu where Day like (%s) and Dinner = (%s) order by Name asc"
		values = ('%'+Day+'%', '1')
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		dinner = []

		for i in result:
			dinner.append(i[0])

	except Exception as e:
		return render_template('passengerError.html', error=e, username=UserID)
	return render_template('viewMenuPassenger.html', username=UserID, breakfast=breakfast, lunch=lunch, dinner=dinner)

@app.route('/viewMenuCrewmate',methods=['POST', 'GET'])
def viewMenuCrewmate():
	try:
		UserID = request.form['user']
		Dept = request.form['dept']
		Day = request.form['Day']

		print(UserID, Dept)

		if Day == 'Monday':
			Day = 'M'
		elif Day == 'Tuesday':
			Day = 'T'
		elif Day == 'Wednesday':
			Day = 'W'
		elif Day == 'Thursday':
			Day = 'R'
		elif Day == 'Friday':
			Day = 'F'
		elif Day == 'Saturday':
			Day = 'S'
		else:
			Day = 'U'

		mysqldb = mysql.connect()
		mycursor = mysqldb.cursor()

		sql = "select distinct Name from Menu where Day like (%s) and Breakfast = (%s) order by Name asc"
		values = ('%'+Day+'%', '1')
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		breakfast = []

		for i in result:
			breakfast.append(i[0])

		sql = "select distinct Name from Menu where Day like (%s) and Lunch = (%s) order by Name asc"
		values = ('%'+Day+'%', '1')
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		lunch = []

		for i in result:
			lunch.append(i[0])

		sql = "select distinct Name from Menu where Day like (%s) and Dinner = (%s) order by Name asc"
		values = ('%'+Day+'%', '1')
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		dinner = []

		for i in result:
			dinner.append(i[0])

	except Exception as e:
		return render_template('crewmateError.html', error=e, username=UserID, dept=Dept)
	return render_template('viewMenuCrewmate.html', username=UserID, breakfast=breakfast, lunch=lunch, dinner=dinner, dept=Dept)


@app.route('/scheduleFacilityInter', methods=['POST','GET'])
def scheduleFacilityInter():
	try:
		UserID = request.form['userFacility']
		mysqldb = mysql.connect()
		mycursor = mysqldb.cursor()

		mycursor.execute("select Name from Facility where Status = 1")
		result = mycursor.fetchall()
		tables = []
		for i in result:
			tables.append(i[0])
	except Exception as e:
		return render_template('passengerError.html', error=e, username=UserID)
	finally:
		mycursor.close()
		mysqldb.close()
	return render_template('scheduleFacilityInter.html', username=UserID, tables = tables)

@app.route('/scheduleFacility', methods=['POST','GET'])
def scheduleFacility():
	try:
		UserID = request.form['user']
		Name = request.form['Name']
		Day = request.form['Day']
		Date = request.form['Date']
		Quarter = request.form['Quarter']
		cruise = Date[2:4] + Quarter

		mysqldb = mysql.connect()
		mycursor = mysqldb.cursor()

		mycursor.execute("select ID from crewmate where ID like '______2' order by ID desc LIMIT 1")
		result = mycursor.fetchall()

		Current_Year = str(result[0][0])[0:2]
		Current_Quarter = str(result[0][0])[2]
		Current_Cruise =Current_Year + Current_Quarter

		if(int(Date[2:4]) != int(Current_Year)):
			return render_template('passengerError.html', error="You cannot schedule an activity for a cruise other than the current quarter.", username=UserID)

		if(int(Quarter) != int(Current_Quarter)):
			return render_template('passengerError.html', error="You cannot schedule an activity for a cruise other than the current quarter.", username=UserID)

		sql = "select count(*) from Facility where Name = (%s)"
		values = (Name)
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		if result[0][0] == 0:
			return render_template('passengerError.html', error = 'The input Facility does not exist.', username=UserID)

		sql = "select count(*) from Scheduling inner join Timeslot on Scheduling.Timeslot_ID = Timeslot.ID where Timeslot.Day = (%s) and Scheduling.Facility_Name = (%s) and Scheduling.Passenger_ID like (%s)"
		values = (Day, Name, cruise + '___1')
		mycursor.execute(sql, values)
		result = mycursor.fetchall()

		print(result)

		facility_count = result[0][0]

		sql = "select capacity from Facility where Name = (%s)"
		values = (Name)
		mycursor.execute(sql, values)
		result = mycursor.fetchall()

		if int(result[0][0]) <= facility_count:
			return render_template('passengerError.html', error='The Facility is fully booked for the input day.', username=UserID)

		if facility_count >= 3:
			return render_template('passengerError.html', error='You have exceeded your facility booking limit for the input day.', username=UserID)

		sql = "select Status from Facility where Name = (%s)"
		values = (Name)
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		print(result)

		if result[0][0] == 0:
			return render_template('passengerError.html', error='The Facility is unavailable for the input day.', username=UserID)

		sql = "select ID, Start_Time, End_Time from Timeslot where Day = (%s)"
		values = (Day)
		mycursor.execute(sql, values)
		result = mycursor.fetchall()

		#print(result, Day)

		Slots = []
		temp = []
		for i in result:
			strtime = i[1].strftime("%H:%M:%S")
			if int(strtime[0:2]) >= 10 and int(strtime[0:2]) < 23:
				Slots.append(i)
				temp.append(i[0])

		print(Slots)

		sql = "select Timeslot_ID from Scheduling where Passenger_ID like (%s) and Facility_Name = (%s)"
		values = (cruise + '___1', Name)
		mycursor.execute(sql, values)
		result = mycursor.fetchall()

		temp_Slots = []
		for i in result:
			temp_Slots.append(i[0])

		second_Slots = []
		for i in range(0, len(Slots)):
			if temp[i] not in temp_Slots:
				second_Slots.append(Slots[i])

		final_Slots = []
		for i in range(0, len(second_Slots)):
			temp = (second_Slots[i][0], second_Slots[i][1].strftime("%H:%M:%S")[0:5], second_Slots[i][2].strftime("%H:%M:%S")[0:5])
			final_Slots.append(temp)

	except Exception as e:
		return render_template('passengerError.html', error=e, username=UserID)
	mycursor.close()
	mysqldb.close()
	return render_template('scheduleFacility.html', username=UserID, tables=final_Slots, facility=Name, cruise= cruise, day=Day)

@app.route('/scheduleFacilityFinal', methods=['POST','GET'])
def scheduleFacilityFinal():
	try:
		mysqldb = mysql.connect()
		mycursor = mysqldb.cursor()

		UserID = request.form['user']
		Name = request.form['facility']
		Slot = request.form['ID']
		cruise = request.form['cruise']
		Day = request.form['day']

		sql = "select ID, Start_Time, End_Time from Timeslot where Day = (%s)"
		values = (Day)
		mycursor.execute(sql, values)
		result = mycursor.fetchall()



		Slots = []
		temp = []
		for i in result:
			strtime = i[1].strftime("%H:%M:%S")
			if int(strtime[0:2]) >= 10 and int(strtime[0:2]) < 23:
				Slots.append(i)
				temp.append(i[0])

		print(Slots)

		sql = "select Timeslot_ID from Scheduling where Passenger_ID like (%s) and Facility_Name = (%s)"
		values = (cruise + '___1', Name)
		mycursor.execute(sql, values)
		result = mycursor.fetchall()

		temp_Slots = []
		for i in result:
			temp_Slots.append(i[0])

		second_Slots = []
		for i in range(0, len(Slots)):
			if temp[i] not in temp_Slots:
				second_Slots.append(Slots[i])
		#print(second_Slots)

		final_Slots = []
		for i in range(0, len(second_Slots)):
			final_Slots.append(second_Slots[i][0])

		print(final_Slots)

		if int(Slot) not in final_Slots:
			return render_template('passengerError.html', error = 'Invalid ID input', username=UserID)

		sql = "select ID from passenger where Login_ID = (%s) and ID like (%s)"
		values = (UserID, cruise + '___1')
		mycursor.execute(sql, values)
		result = mycursor.fetchall()

		if not result:
			return render_template('passengerError.html', error = 'You are not an active member for this cruise.', username=UserID)


		sql = "insert into Scheduling values (%s, %s, %s, %s)"
		values = (result[0][0], Name, Slot, 3)
		mycursor.execute(sql, values)
		mysqldb.commit()
	except Exception as e:
		return render_template('passengerError.html', error=e, username=UserID)
	mycursor.close()
	mysqldb.close()
	return render_template('confirmPassenger.html', result='Your Transaction has been Completed.', username=UserID)

@app.route('/viewActivitiesInter', methods=['POST', 'GET'])
def viewActivitiesInter():
	try:
		UserID = request.form['userActivity']
	except Exception as e:
		return render_template('passengerError.html', error=e, username=UserID)
	return render_template('viewActivitiesInter.html', username=UserID)

@app.route('/viewActivities', methods=['POST', 'GET'])
def viewActivities():
	try:
		UserID = request.form['user']
		Year = request.form['Date'][2:4]
		Quarter = request.form['Quarter']
		cruise = Year + Quarter

		mysqldb = mysql.connect()
		mycursor = mysqldb.cursor()

		sql = "select Scheduling.Facility_Name, Timeslot.Day, Timeslot.Start_Time, Timeslot.End_Time from Scheduling inner join Timeslot on Timeslot.ID = Scheduling.Timeslot_ID inner join Passenger on Passenger.ID = Scheduling.Passenger_ID where Passenger.Login_ID = (%s) and Passenger.ID like (%s)"
		values = (UserID, cruise + '___1')
		mycursor.execute(sql, values)
		result = mycursor.fetchall()

		final = []

		for i in result:
			temp = (i[0], i[1], i[2].strftime("%H:%M:%S")[0:5], i[3].strftime("%H:%M:%S")[0:5])
			final.append(temp)

	except Exception as e:
		return render_template('passengerError.html', error=e, username=UserID)
	mycursor.close()
	mysqldb.close()
	return render_template('viewActivities.html', username = UserID, tables=final)

@app.route('/viewTicketsInter', methods=['POST', 'GET'])
def viewTicketsInter():
	try:
		UserID = request.form['userTicketView']
	except Exception as e:
		return render_template('passengerError.html', error=e, username=UserID)
	return render_template('viewTicketsInter.html', username=UserID)

@app.route('/viewTickets', methods=['POST', 'GET'])
def viewTickets():
	try:
		UserID = request.form['user']
		Year = request.form['Date'][2:4]
		Quarter = request.form['Quarter']
		cruise = Year + Quarter

		mysqldb = mysql.connect()
		mycursor = mysqldb.cursor()

		sql = "select Ticket.ID, Ticket.Type, Ticket.Status from Ticket inner join Passenger on Ticket.Passenger_ID = Passenger.ID where Passenger.Login_ID = (%s) and Passenger.ID like (%s) order by Ticket.ID asc"
		values = (UserID, cruise + '___1')
		mycursor.execute(sql, values)
		result = mycursor.fetchall()

		final = []

		for i in result:
			stat = 'Terminated'
			if i[2] == 1:
				stat = 'Pending'

			temp = (i[0], i[1], stat)
			final.append(temp)

	except Exception as e:
		return render_template('passengerError.html', error=e, username=UserID)
	mycursor.close()
	mysqldb.close()
	return render_template('viewTickets.html', username = UserID, tables=final)


if __name__ == "__main__":
    app.run()