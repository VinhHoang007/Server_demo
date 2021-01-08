from flask import Flask, request, url_for, redirect, render_template, request
from flaskext.mysql import MySQL
import time, chatprocess, dbconfig, voicebot,os,json


app = Flask(__name__)
mysql = dbconfig.dbconfig(app)
connect = mysql.connect()
curr = connect.cursor()

#==============================================================================================
@app.route('/')
def login():
    return render_template('login.html')

@app.route('/logcheck', methods=['POST'])
def logcheck():
    username = request.form['username']
    password = request.form['password']
    return check_action(username,password)

@app.route('/logcheckapp', methods=['GET'])
def logcheckapp():
    connect = mysql.connect()
    curr = connect.cursor()
    username = request.args.get('username')
    password = request.args.get('password')
    return check_action_app(username,password)

def check_action_app(username,password):
    check = curr.execute("SELECT * FROM account WHERE username = %s", username)
    record = curr.fetchall()
    for row in record:
        state = row[5]
    if (check == 0):
        return json.dumps({"state":False,"error":"The account isn't exist"})
    elif (state == 0):
        for row in record:
            passdata = row[4]
        if passdata == password:
            name = row[1]
            mssv = row[0]
            course = row[6]
            return json.dumps({"state":True, "name":name,"mssv":mssv,"course":course})
        else:
            return json.dumps({"state":False, "error": "The password is fail"})
    else:
        return json.dumps({"state":False,"error":"Your account is blocked"})




def check_action(username,password):
    check = curr.execute("SELECT * FROM account WHERE username = %s", username)
    record = curr.fetchall()
    for row in record:
        state = row[5]
    if (check == 0):
        result = "The account isn't exist"
        return render_template('login.html', fail=result)
    elif (state == 0):
        for row in record:
            passdata = row[4]
        if passdata == password:
            name = row[1]
            mssv = row[0]
            course = row[6]
            return redirect(url_for('home',username=name,mssv=mssv,course=course))
        else:
            result = "The password is fail"
            return render_template('login.html', fail = result)
    else:
        result = "Your account is blocked. Please contact to admin to get more infomation"
        return render_template('login.html', fail = result)
#=========================================================================================
@app.route('/register')
def register():
    return render_template('register.html')



@app.route('/registercheck', methods = ['POST'])
def checkregis():
    password = request.form['password']
    passconf  = request.form['passconf']
    email = request.form['email']
    name = request.form['name']
    username = request.form['username']
    mssv = request.form['mssv']
    #-------------------------------------------------------
    check = -1
    errormail = errorpass = errornull = ''
    if password=='' or email=='' or name=='' or username=='' or mssv=='':
       errornull = "Anything on form not be empty."
       check = 1
    if passconf != password:
        errorpass = "Password confirm don't match."
        check = 1
    if email.find('@') == -1:
        errormail = "Email is wrong for missing '@' character"
        check = 1
    if len(mssv)!=7:
        errormssv = "The ID student must be has 7 numbers"
        check = 1
    #---------------------------------------------------------
    if check == 1:
         return render_template('register.html',errormail=errormail, 
             errorpass=errorpass, errornull=errornull, errormssv=errormssv)
    else: 
        try:
            curr.execute("INSERT INTO `account`(`name`,`mssv`,`email`,`username`,`password`,`state`) VALUES (%s,%s,%s,%s,%s,0)",
                          (name,mssv,email,username,password))
            connect.commit()
            result = "The register is complete !"
            curr.close()
            return render_template('login.html',sucess=result)
        except:
            error = "The email or student ID was exist ! Please check it again."
            curr.close()
            return render_template('register.html', fail=error)

#=========================================================================================
@app.route('/bot/<mssv>:<username>:<course>')
def home(username,mssv,course):
    return render_template("home.html",name=username,mssv=mssv,course=course)

@app.route('/getbot')
def get_bot_response():
    userText = request.args.get('msg')
    course = request.args.get('course')
    print(course)
    data = {'answer':chatprocess.chatbot_response(userText,course)}
    return json.dumps(data, ensure_ascii=False)

def dir_last_updated(folder):
    return str(max(os.path.getmtime(os.path.join(root_path, f))
                   for root_path, dirs, files in os.walk(folder)
                   for f in files))

@app.route("/voicebot")
def get_record():
    course = request.args.get('course')
    voicebot.voicebot(course)
    id_file = dir_last_updated('./static')
    return id_file


#=============================================================================================
if __name__ == '__main__':
    app.run(host='localhost', port=8000, debug=True)
    #app.run(host='localhost', port=8000, debug=True)