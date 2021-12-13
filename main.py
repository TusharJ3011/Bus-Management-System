from flask import render_template, url_for, Flask, request, redirect, session
import datetime as dt
import os

# Local Files
import dbms
import security


app = Flask(__name__)
app.secret_key = os.environ['APP_KEY']
app.register_error_handler(404, 'pageNotFound')


@app.route('/')
@app.route('/home')
@app.route('/home/')
def home():
    return render_template('Home.html')


@app.route('/findbuses', methods=['POST', 'GET'])
@app.route('/findbuses/', methods=['POST', 'GET'])
def findbuses():
    today = dt.date.today()
    today = today.strftime("%Y-%m-%d")
    finalList = []
    error = False
    cities = dbms.getCities()
    if request.method == 'POST':
        data = request.form
        city1 = data['source']
        city2 = data['dest']
        date = dt.datetime.strptime(data['date'], "%Y-%m-%d").date()
        details = [city1, city2, date]
        selBus = dbms.getBusDet(details)
        print(selBus)
        if len(selBus) == 0:
            error = True
        else:
            selBus = list(selBus)
            finalList = []
            for bus in selBus:
                temp = list(bus)
                temp[9] = date
                temp.append(date + dt.timedelta(days=temp[11]))
                print(finalList)
                finalList.append(temp)
    return render_template('FindBuses.html', today=today, cities=cities, selBus=finalList, error=error)


@app.route('/bookseat/<i>/<date>/<date1>/<j>/<type>')
def bookseat(i, date, date1, j, type):
    global tickNo, details
    tickNo = None
    details = None
    tickNo = dbms.setTicketNo()
    details = dbms.getBusDetID(i, date, date1)
    details = list(details)
    seat = f"{type}{j}"
    details.append(seat)
    details = tuple(details)
    return render_template('SeatConfirmation.html', tickNo=tickNo, details=details)


@app.route('/con')
def con():
    global tickNo, details
    dbms.confirm(tickNo, details)
    return redirect(url_for('findbuses'))


@app.route('/ticketstatus', methods=['POST', 'GET'])
@app.route('/ticketstatus/', methods=['POST', 'GET'])
def ticketstatus():
    error = False
    details = []
    show = False
    if request.method == 'POST':
        data = request.form
        print(data)
        ticketID = data['product']
        details = dbms.getTicket(ticketID)
        if len(details) == 0:
            error = True
            details = []
        else:
            show = True
    return render_template('TicketStatus.html', error=error, details=details, show=show)


@app.route('/adminlogin', methods=['POST', 'GET'])
@app.route('/adminlogin/', methods=['POST', 'GET'])
def adminlogin():
    error = 'none'
    if request.method == 'POST':
        data = request.form
        uname = data['username']
        password = data['password']
        errors = security.checkAdmin(uname, password)
        if errors[0]:
            error = 'uname'
        else:
            if errors[1]:
                error = 'password'
            else:
                session['adminLogin'] = True
                return redirect(url_for('admin'))
    return render_template('Login.html', error=error)


@app.route('/admin/logout')
def adminlogout():
    session['adminLogin'] = False
    return redirect(url_for('admin'))


@app.route('/admin')
@app.route('/admin/')
def admin():
    try:
        if session['adminLogin']:
            buses = dbms.getBusList()
            emps = dbms.getEmpList()
            return render_template('admin.html', emps=emps, buses=buses)
        else:
            return redirect(url_for('adminlogin'))
    except (RuntimeError, KeyError):
        return redirect(url_for('adminlogin'))


@app.route('/form1', methods=['POST', 'GET'])
def form1():
    global error1
    data = request.form
    empID = data['emp']
    busID = data['busnum']
    date = data['date1']
    details = [empID, busID, date]
    error1 = dbms.insertJob(details)
    return redirect(url_for('admin'))


@app.route('/form2', methods=['POST', 'GET'])
def form2():
    data = request.form
    empName = data['ename']
    password = data['epassword']
    job = data['job']
    pNumber = data['phoneNumber']
    empDOB = data['edob']
    empAddress = data['eaddress']
    details = [empName, password, job, pNumber, empDOB, empAddress]
    dbms.insertEmp(details)
    return redirect(url_for('admin'))


@app.route('/form3', methods=['POST', 'GET'])
def form3():
    data = request.form
    busNumber = data['busNo']
    city1 = data['city1']
    city2 = data['city2']
    frequency = data['frequency']
    dept1 = data['dept1']
    arrv1 = data['arrv1']
    dept2 = data['dept2']
    arrv2 = data['arrv2']
    sDate = data['sDate']
    seater = data['seater']
    sleeper = data['sleeper']
    daysTaken = data['daysTaken']
    details = [busNumber, city1, city2, frequency, dept1, arrv1, dept2, arrv2, sDate, daysTaken, seater, sleeper]
    dbms.addBus(details)
    return redirect(url_for('admin'))


@app.route('/form4', methods=['POST', 'GET'])
def form4():
    data = request.form
    busNo = data['busNo']
    dbms.actdeact(busNo)
    return redirect(url_for('admin'))


@app.route('/employee')
@app.route('/employee/')
def employee():
    try:
        if session['employeeLogin']:
            global empID
            jobs = dbms.getJobList(empID)
            return render_template('Employee.html', jobs=jobs)
        else:
            return redirect(url_for('employeelogin'))
    except (RuntimeError, KeyError):
        return redirect(url_for('employeelogin'))


@app.route('/employeelogin', methods=['POST', 'GET'])
@app.route('/employeelogin/', methods=['POST', 'GET'])
def employeelogin():
    error = 'none'
    if request.method == 'POST':
        data = request.form
        name = data['name']
        password = data['password']
        errors = security.checkEmployee(name, password)
        if errors[0]:
            error = 'name'
        else:
            if errors[1]:
                error = 'password'
            else:
                session['employeeLogin'] = True
                global empID
                empID = name
                return redirect(url_for('employee'))
    return render_template('EmployeeLogin.html', error=error)


@app.route('/employee/logout')
def employeelogout():
    session['employeeLogin'] = False
    return redirect(url_for('employee'))


@app.route('/sendCompSignal/<i>/<j>')
def completion(i, j):
    dbms.completion(i, j)
    return redirect(url_for('home'))


@app.errorhandler(404)
def pageNotFound(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run()
