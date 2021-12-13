import datetime as dt
import mysql.connector

import security
import os


def createRunners():
    myDB = mysql.connector.connect(
        host="127.0.0.1",
        user= os.environ['DBMS_USER'],
        password= os.environ['DBMS_PASS'],
        database="BMS"
    )
    myCursor = myDB.cursor()
    return [myDB, myCursor]


def getBusDet(details):
    runners = createRunners()
    runners[1].execute(
        f"SELECT * FROM buses WHERE (city1='{details[0]}' AND city2='{details[1]}') OR (city1='{details[1]}' AND city2='{details[0]}') AND (state='active')")
    buses = runners[1].fetchall()
    selBuses = []
    for bus in buses:
        date = details[2] - bus[9]
        date = date.days
        temp = date / bus[4]
        # temp = temp.total_seconds()/3600
        # print(temp)
        if temp % 2 == 0 and bus[2] == details[0]:
            bus = list(bus)
            bus.append(1)
            bus = tuple(bus)
            selBuses.append(bus)
        elif temp % 2 == 1 and bus[3] == details[0]:
            bus = list(bus)
            temp = bus[2]
            bus[2] = bus[1]
            bus[1] = temp
            bus.append(2)
            bus = tuple(bus)
            selBuses.append(bus)
    return selBuses


def getTicket(ticketID):
    runners = createRunners()
    runners[1].execute(f"SELECT * FROM bookings WHERE tickNo={ticketID}")
    details = runners[1].fetchone()
    return details


def setTicketNo():
    runners = createRunners()
    runners[1].execute(f"SELECT tickNo FROM bookings ORDER BY tickNo DESC LIMIT 1")
    temp = runners[1].fetchall()
    if len(temp) == 0:
        ID = 1
    else:
        ID = temp[0][0] + 1
    return ID


def getBusDetID(id, date, date1):
    runners = createRunners()
    runners[1].execute(f"SELECT * FROM buses WHERE busID={id}")
    temp = runners[1].fetchone()
    temp = list(temp)
    print(type(date))
    temp[9] = date
    temp.append(date1)
    temp = tuple(temp)
    return temp


def confirm(tickNo, details):
    runners = createRunners()
    if details[-1] == 1:
        dept = details[5]
        arrv = details[8]
    else:
        dept = details[7]
        arrv = details[8]
    runners[1].execute(
        f"INSERT INTO bookings(tickNo, busID, busNo, seatNo, seatType, date, city1, city2, deptTime, arrvTime) VALUES ({tickNo}, {details[0]}, '{details[1]}', {int(details[17][2:])}, '{details[17][:2]}', '{details[9]}', '{details[2]}', '{details[3]}', '{dept}', '{arrv}')")
    runners[0].commit()
    if details[17][:2] == 'SL':
        runners[1].execute(f"SELECT sleeperAvail FROM buses WHERE busID={details[0]}")
        data = runners[1].fetchone()[0]
        data = int(data) - 1
        runners[1].execute(f"UPDATE buses SET sleeperAvail={data} WHERE busID={details[0]}")
        runners[1].commit()
    else:
        runners[1].execute(f"SELECT seaterAvail FROM buses WHERE busID={details[0]}")
        data = runners[1].fetchone()[0]
        data = int(data) - 1
        runners[1].execute(f"UPDATE buses SET seaterAvail={data} WHERE busID={details[0]}")
        runners[1].commit()
    return


def getCities():
    runners = createRunners()
    runners[1].execute(f"SELECT DISTINCT city1 FROM buses")
    cities = runners[1].fetchall()
    temp = []
    for city in cities:
        temp.append(city[0])
    temp = tuple(temp)
    runners[1].execute(f"SELECT city2 FROM buses WHERE city2 NOT IN {temp}")
    cities = runners[1].fetchall()
    temp = list(temp)
    for city in cities:
        temp.append(city[0])
    return temp


def insertJob(details):
    runners = createRunners()
    runners[1].execute(f"SELECT job FROM employees WHERE ID={details[0]}")
    job = runners[1].fetchone()
    job = job[0]
    runners[1].execute(f"SELECT * FROM jobRecords WHERE empID='{details[0]}' AND date='{details[2]}'")
    temp = runners[1].fetchall()
    if len(temp) == 0:
        runners[1].execute(
            f"INSERT INTO jobRecords VALUES ({details[0]}, '{details[1]}', {details[2]}, '{job}', 'pending')")
        runners[0].commit()
        return False
    else:
        return True


def insertEmp(details):
    password = security.securePassword(details[1])
    runners = createRunners()
    runners[1].execute(
        f"INSERT INTO employees(empName, empPassword, job, phoneNo, dob, address) VALUES('{details[0]}', '{password}', '{details[2]}', {details[3]}, '{details[4]}', '{details[5]}')")
    runners[0].commit()
    return


def addBus(details):
    runners = createRunners()
    runners[1].execute(f"SELECT * FROM buses WHERE busNo='{details[0]}'")
    temp = runners[1].fetchall()
    if len(temp) != 0:
        runners[1].execute(
            f"UPDATE buses SET city1='{details[1]}', city2='{details[2]}', frequency={details[3]}, deptTime1='{details[4]}', arrvTime1='{details[5]}', deptTime2='{details[6]}', arrvTime2='{details[7]}', startDate='{details[8]}', state='active', daysTaken={details[9]}, seater={details[10]}, sleeper={details[11]} WHERE busNo='{details[0]}'")
        runners[0].commit()
    else:
        runners[1].execute(
            f"INSERT INTO buses(busNo, city1, city2, frequency, deptTime1, arrvTime1, deptTime2, arrvTime2, startDate, state, daysTaken, seater, sleeper) VALUES ('{details[0]}', '{details[1]}', '{details[2]}', {details[3]}, '{details[4]}', '{details[5]}', '{details[6]}', '{details[7]}', '{details[8]}', 'active', {details[9]}, {details[10]}, {details[11]})")
        runners[0].commit()
    return


def actdeact(busno):
    runners = createRunners()
    runners[1].execute(f"SELECT state FROM buses WHERE busNo='{busno}'")
    temp = runners[1].fetchone()
    temp = temp[0]
    print(temp)
    if temp == 'active':
        state = 'non-active'
    elif temp == 'non-active':
        state = 'active'
    print(state)
    runners[1].execute(f"UPDATE buses SET state='{state}' WHERE busNo='{busno}'")
    runners[0].commit()
    return


def getEmployee(ID):
    runners = createRunners()
    runners[1].execute(f"SELECT empPassword FROM employees WHERE empID='{ID}'")
    empDet = runners[1].fetchall()
    return empDet


def getEmpList():
    runners = createRunners()
    runners[1].execute(f"SELECT empID, empName FROM employees")
    data = runners[1].fetchall()
    list = []
    for emp in data:
        temp = f"{emp[1]} ({emp[0]})"
        list.append(temp)
    return list


def getBusList():
    runners = createRunners()
    runners[1].execute(f"SELECT busID, busNo FROM buses")
    data = runners[1].fetchall()
    list = []
    for bus in data:
        temp = f"{bus[1]} ({bus[0]})"
        list.append(temp)
    return list


def getJobList(id):
    runners = createRunners()
    runners[1].execute(f"SELECT * FROM jobRecords WHERE empID={id}")
    data = runners[1].fetchall()
    print(data)
    return data

def completion(i, j):
    runners = createRunners()
    runners[1].execute(f"UPDATE jobRecords SET status='done' WHERE busID={i} AND jobDate='{j}'")
    runners[0].commit()
    runners[1].execute(f"UPDATE buses SET sleeperAvail=sleeper, seaterAvail=seater WHERE busID={i}")
    runners[0].commit()
    return
