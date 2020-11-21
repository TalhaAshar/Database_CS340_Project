create table Room(
	 ID int(4) NOT NULL,
	 Package varchar(8) Check (Package in ('Low', 'Medium', 'High', "Crewmate")),
	 Price numeric(8,2) Check (Price >= 0) default 0,
	 Floor varchar(7) NOT NULL Check (Floor in ('Ground','First','Second','Third','Deck')),
	 Primary Key(ID));

 create table Department(
	Dept_name varchar(20) NOT NULL,
	Min_Capacity numeric(3,0) check (Min_Capacity > 0),
	Max_Capacity numeric(3,0) check (Max_Capacity < 60),
	Budget numeric(8,2) check (Budget > 0),
	Primary Key (Dept_Name));

create table Login(
	ID int(10) NOT NULL,
	Password varchar(8) NOT NULL,
	Type varchar(20) NOT NULL Check (Type in ('Crewmate', 'Passenger', 'Offshore_Management')),
	Primary Key(ID));

create table Passenger(
	ID int(7) NOT NULL,
	Name varchar(20) NOT NULL,
	Age int(3) NOT NULL Check (Age > 0),
	CNIC int(13) NOT NULL,
	Room_ID int(4),
	Disability boolean,
	Promotional_Consent boolean,
	Login_ID int(10) NOT NULL,
	Primary Key (ID),
	Foreign Key (Room_ID) references Room(ID) on delete set NULL,
	Foreign Key (Login_ID) references Login(ID) on delete cascade);

create table Crewmate(
	ID int(7) NOT NULL,
	Name varchar(20) NOT NULL,
	Room_ID int(4),
	Origin varchar(20),
	Dept_name varchar(20),
	Experience varchar(40),
	Status boolean,
	Login_ID int(10) NOT NULL,
	Primary Key (ID),
	Foreign Key (Room_ID) references Room(ID) on delete set NULL,
	Foreign Key (Dept_name) references Department(Dept_name) on delete set NULL,
	Foreign Key (Login_ID) references Login(ID) on delete cascade);

create table Highest_Ranking_Officer(
	Officer_Rank int(2) NOT NULL,
	Crewmate_ID int(7) NOT NULL,
	Designation varchar(20),
	Primary Key (Officer_Rank),
	Foreign Key (Crewmate_ID) references Crewmate(ID) on delete cascade,
	Foreign Key (Designation) references Department(Dept_name) on delete set NULL);

create table Ticket(
	ID int NOT NULL auto_increment,
	Crewmate_ID int(7),
	Passenger_ID int(7) NOT NULL,
	Type varchar(15) Check (Type in ('General Complaint', 'Room Service', 'Lost and Found')),
	Status boolean,
	Primary Key (ID),
	Foreign Key (Crewmate_ID) references Crewmate(ID) on delete set NULL,
	Foreign Key (Passenger_ID) references Passenger(ID) on delete cascade);

create table Menu(
	ID int(4) NOT NULL,
	Name varchar(20) NOT NULL,
	Day varchar(10) Check (Day in ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')),
	Breakfast boolean,
	Lunch boolean,
	Dinner boolean,
	Crewmate_ID int(7),
	Primary Key (ID),
	Foreign Key (Crewmate_ID) references Crewmate(ID) on delete set NULL);

create table Timeslot(
	ID int(3) NOT NULL Check (ID > 0 and ID < 169),
	Day varchar(10) Check (Day in ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')),
	Start_Time datetime,
	End_Time datetime,
	Primary Key (ID));

create table Facility(
	Name varchar(15) NOT NULL,
	Capacity numeric(3,0) Check (Capacity > 0),
	Status boolean,
	Dept_name varchar(20),
	Primary Key (Name),
	Foreign Key (Dept_name) references Department(Dept_name) on delete cascade);

create table Scheduling(
	Passenger_ID int(7) NOT NULL,
	Facility_Name varchar(15) NOT NULL,
	Timeslot_ID int(3) NOT NULL,
	Scheduling_Limit numeric(2,0) Check (Scheduling_Limit in (1, 3, 6)),
	Primary Key (Passenger_ID, Facility_Name, Timeslot_ID),
	Foreign Key (Passenger_ID) references Passenger(ID) on delete cascade,
	Foreign Key (Facility_Name) references Facility(Name) on delete cascade,
	Foreign Key (Timeslot_ID) references Timeslot(ID) on delete cascade);

create table Inventory(
	ID int(4) NOT NULL,
	Name varchar(20),
	Quantity_Present numeric(3,0) Check (Quantity_Present > 0),
	Weight numeric(5,2) Check (Weight > 0),
	Status varchar(15) Check (Status in ('Perishable', 'Fragile', 'Hazardous')),
	Description varchar(75),
	Is_Freight boolean,
	Dept_name varchar(20),
	Primary Key (ID),
	Foreign Key (Dept_name) references Department(Dept_name) on delete set NULL);

create table Location(
	Name varchar(50) NOT NULL,
	Latitude numeric(8,6) NOT NULL,
	Longitude numeric(9,6) NOT NULL,
	Primary Key (Name));

create table Freight(
	Inventory_ID int(4) NOT NULL,
	Luggage boolean,
	Destination varchar(50),
	Primary Key (Inventory_ID),
	Foreign Key (Inventory_ID) references Inventory(ID) on delete cascade,
	Foreign Key (Destination) references Location(Name) on delete set NULL);

create table Route(
	Source varchar(50),
	Destination varchar(50),
	Distance numeric(4,0),
	Primary Key (Source, Destination, Distance),
	Foreign Key (Source) references Location(Name) on delete cascade,
	Foreign Key (Destination) references Location(Name) on delete cascade);
