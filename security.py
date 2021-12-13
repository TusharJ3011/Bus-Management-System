import werkzeug.security

# Password :
ADMINUSERNAME = 'O21GROUP9'.lower()
ADMINPASSWORD = 'pbkdf2:sha256:260000$9Pn31aie3pRdz1Nj$9d0bfe1116920058fab3328d46c8b4329c1254a43b2da995ac8264d7d3848382'


def securePassword(password):
    securePass = werkzeug.security.generate_password_hash(password=password, method="pbkdf2:sha256", salt_length=16)
    return securePass


def checkAdmin(username, password):
    error = []
    if username.lower() == ADMINUSERNAME:
        error.append(0)
        passCheck = werkzeug.security.check_password_hash(pwhash=ADMINPASSWORD, password=password)
        if passCheck:
            error.append(0)
        else:
            error.append(1)
    else:
        error.append(1)
        error.append(1)
    return error


def checkAdminPassword(password):
    passCheck = werkzeug.security.check_password_hash(pwhash=ADMINPASSWORD, password=password)
    return passCheck


import dbms


def checkEmployee(ID, password):
    empDet = dbms.getEmployee(ID)
    error = []
    if len(empDet) != 0:
        error.append(0)
        passCheck = werkzeug.security.check_password_hash(pwhash=empDet[0][0], password=password)
        if passCheck:
            error.append(0)
        else:
            error.append(1)
    else:
        error.append(1)
        error.append(1)
    return error

