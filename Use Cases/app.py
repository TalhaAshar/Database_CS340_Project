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
		_UserType = 'Passenger'
		if temp.get('employee'):
			_UserType = 'Employee'
		else:
			_UserType = 'Passenger'
		UserID = temp['User-ID']
		Password = temp['Password']

		sql = "select * from Login where ID = (%s) and Password = (%s) and Type = (%s)"
		values = (UserID, Password, _UserType)
		mycursor.execute(sql, values)
		result = mycursor.fetchall()

		if mycursor.rowcount <= 0:
			return render_template('error.html', error='The given username and password do not match for your type of account')

		sql = "select Name, Age, CNIC, Disability, Promotional_Consent from Passenger where Login_ID = (%s) order by ID desc"
		values = (UserID)
		mycursor.execute(sql, values)
		result = mycursor.fetchall()
		Name = result[0][0]
		Age = result[0][1]
		CNIC = result[0][2]
		Disability = result[0][3]
		Promo = result[0][4]

	except Exception as e:
		return render_template('error.html', error=e)
	finally:
		mycursor.close()
		mysqldb.close()
	if(_UserType == 'Passenger'):
		return render_template('passengerBooking.html', username=UserID, CNIC=CNIC, name=Name, age=Age, disability=Disability, promo=Promo)
	elif _UserType == 'Crewmate':
		return render_template('L6.html')
	else:
		return render_template('first_page.html')


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

		if mycursor.rowcount <= 0:
			return render_template('error.html', error='The given username and password do not match for your type of account')
	except Exception as e:
		return render_template('error.html', error=e)
	finally:
		mycursor.close()
		mysqldb.close()

	return render_template('newPassenger.html')


#@app.route('/enterPassengerInformation')
#def enterPassengerInformation():
#    return render_template('newPassenger.html')

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
				if int(_Room) <= 140:
					if curr_num >= 3:
						return render_template('error.html', error ='The given room is already full.')
				elif int(_Room) <= 180:
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
		values = _cruise + '____'
		mycursor.execute(sql, values)
		_result = mycursor.fetchall()

		if (_result[0][0] == 680):
			return render_template('error.html', error ='The Quarter for the Cruise you have selected is at capacity.')

		sql = "insert into Login values (%s, %s, %s)"
		values = (_Username, _Password, 'Passenger')
		mycursor.execute(sql, values)

		new_id = int(_cruise) * 10000 + (_result[0][0] + 1) * 10 + 1

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

	return render_template('bookingReceipt.html', name=_Name, cnic=_CNIC, age=_Age, room= _Room, pack=_package, price=_price, disabled=_Disable, promo=_Promo,date=temp['Date'], quarter=_Quarter, user=_Username)

@app.route('/returnHome')
def returnHome():
    return render_template('index.html')

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
				if int(Room) <= 140:
					if curr_num >= 3:
						return render_template('error.html', error ='The given room is already full.')
				elif int(Room) <= 180:
					if curr_num >= 4:
						return render_template('error.html', error ='The given room is already full.')
				else:
					if curr_num >= 5:
						return render_template('error.html', error ='The given room is already full.')

		sql = "select count(*) from passenger where ID like (%s)"
		values = cruise + '____'
		mycursor.execute(sql, values)
		result = mycursor.fetchall()

		if (result[0][0] == 680):
			return render_template('error.html', error ='The Quarter for the Cruise you have selected is at capacity.')

		new_id = int(cruise) * 10000 + (result[0][0] + 1) * 10 + 1
		if Promo == '1':
			Promo = 1
		else:
			Promo = 0

		sql = "insert into Passenger values (%s, %s, %s, %s, %s, %s, %s, %s)"
		values = (new_id, Name, Age, CNIC, Room, Disable, Promo, UserID)
		mycursor.execute(sql, values)
		print("niga")
		print(values)
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

	return render_template('bookingReceipt.html', name=Name, cnic=CNIC, age=Age, room= Room, pack=package, price=price, disabled=Disable, promo=Promo,date=request.form['Date'], quarter=Quarter, user=UserID)
	

if __name__ == "__main__":
    app.run(port=5508, debug=True)