from flask import Flask, request, url_for, redirect, render_template
from flaskext.mysql import MySQL
import re

def dbconfig(app):
    mysql = MySQL()
    app.config["MYSQL_DATABASE_USER"]='root'
    app.config["MYSQL_DATABASE_PASSWORD"]='123456789'
    app.config["MYSQL_DATABASE_DB"]='register'
    app.config["MYSQL_DATABASE_HOST"]='localhost'
    mysql.init_app(app)
    return mysql
#==================================================================================
def subjectname(subid, app):
    mysql = dbconfig(app)
    connect = mysql.connect()
    curr = connect.cursor()
    check = curr.execute("SELECT * FROM subject WHERE id = %s", subid)
    if check == 1:
        record = curr.fetchall()
        for row in record:
            subname = row[1]
            
        return subname
    else:
        return None

def config(subid,app,condi,course):
    mysql = dbconfig(app)
    connect = mysql.connect()
    curr = connect.cursor()
    if len(subid)>6:
        subid = re.findall(r"[\w']+", subid)
        if int(course)>18:
            subid = subid[1]
            curr.execute("SELECT * FROM subject WHERE id = %s", subid)
        else:
            subid = subid[0]
            curr.execute("SELECT * FROM subject WHERE id = %s", subid)
    else: 
        curr.execute("SELECT * FROM subject WHERE id = %s", subid)
    record = curr.fetchall()
    for row in record:
        name = row[1]
        if condi == 'HT':
            subcheck = row[2]
            if subcheck == None:
                return name, subid, None
        elif condi == 'SH':
            subcheck = row[3]
            if subcheck == None:
                return name, subid, None
        elif condi == 'TQ':
            subcheck = row[4]
            if subcheck == None:
                return name, subid, None
    subcheck = re.findall(r"[\S']+", subcheck)
    result = ""
    for i in subcheck:
        if (len(i)>6):
            result = result + subjectname(i[0:6],app) + ' [ ' + i.replace("\\"," hoặc ") + " ], "
        else:
            result = result + subjectname(i,app) + ' [ ' + i + " ], "
    return name, subid, result

def subconfig(subjectid,app,condition,course):
    if condition == 'HT':
        subname, subjectid, cfig = config(subjectid,app,'HT',course)
        if cfig == None:
            return 'Môn ' +  subname +' [ ' + subjectid + ' ] không có môn học trước '
        else:
            return 'Môn học trước của ' + subname + ' [ ' + subjectid + ' ] là ' + cfig
    elif condition == 'SH':
        subname, subjectid, cfig = config(subjectid,app,'SH',course)
        if cfig == None:
            return 'Môn ' +  subname +' [ ' + subjectid + ' ] không có môn song hành '
        else:
            return 'Môn song hành của ' + subname +' [ ' + subjectid + ' ] là ' + cfig
    elif condition == 'TQ':
        subname, subjectid, cfig = config(subjectid,app,'TQ',course)
        if cfig == None:
            return 'Môn ' +  subname +' [ ' + subjectid + ' ] không có môn tiên quyết '
        else:
            return 'Môn tiên quyết của ' +subname +' [ ' + subjectid + ' ] là ' + cfig
    else:
        return 'None'

#==============================================================================================
def avyearname(year, course, read_lis, speak_write):
    switcher={
        #Chuẩn anh văn
        'CAV1':'Chuẩn anh văn năm 1 khóa ' + str(course) + ' là TOEIC nghe - đọc ' + str(read_lis), 
        'CAV2':'Chuẩn anh văn năm 2 khóa ' + str(course) + ' là TOEIC nghe - đọc ' + str(read_lis),
        'CAV3':'Chuẩn anh văn năm 3 khóa ' + str(course) + ' là TOEIC nghe - đọc ' + str(read_lis),
        'CAVLV':'Chuẩn anh văn nhận luận văn của khóa ' + str(course) + ' là TOEIC nghe - đọc ' + str(read_lis),
        'CAVTN':'Chuẩn anh văn nhận xét tốt nghiệp của khóa ' + str(course) + ' là TOEIC nghe - đọc ' 
                                            + str(read_lis) + ' TOEIC nói - viết ' + str(speak_write),
        #Chuẩn sinh viên
        'CSV1':'Chuẩn sinh viên năm nhất cần đạt ' + str(read_lis) + ' bạn nhé !',
        'CSV2':'Chuẩn sinh viên năm hai cần đạt ' + str(read_lis) + ' bạn nhé !',
        'CSV3':'Chuẩn sinh viên năm ba cần đạt ' + str(read_lis) + ' bạn nhé !',
        'CSV4':'Chuẩn sinh viên năm tư cần đạt ' + str(read_lis) + ' bạn nhé !',
        'CSV5':'Chuẩn sinh viên năm năm cần đạt ' + str(read_lis) + ' bạn nhé !'
    }
    return switcher.get(year,None)

def avstand(year,course,app):
    mysql = dbconfig(app)
    connect = mysql.connect()
    curr = connect.cursor()
    if (course=="NULL"):
        check = curr.execute("SELECT * FROM stustandard WHERE course IS NULL AND years = %s", year)
    else:
        check = curr.execute("SELECT * FROM stustandard WHERE course = %s AND years = %s", [course,year])
    record = curr.fetchall()
    if check == 1:
        for row in record:
            lis_read = row[3]
            course_data = row[1]
            speak_write = row[4]
        return avyearname(year,course_data,lis_read,speak_write)
    else:
        return 'Hiện tại hệ thống không tìm được chuẩn theo yêu cầu của bạn !'

#====================================================================================================
def teachinfo(teacher,app):
    mysql = dbconfig(app)
    connect = mysql.connect()
    curr = connect.cursor()
    check = curr.execute("SELECT * FROM infoteacher WHERE id = %s", teacher)
    record = curr.fetchall()
    if (check==0):
        return 'Thông tin giảng viên không có trong hệ thống bạn nhé !'
    else:
        for row in record:
            name = row[1]
            room_day = row[2]
            mail = row[3]
        result_mail = 'Địa chỉ email của giảng viên '+name+' là '+'<a href =mailto:'+mail+'>'+mail+'</a>'
        if room_day != None:
            result_room = '. Bạn có thể đến gặp thầy tại '+room_day
        else:
            result_room = ''
    return result_mail + result_room

    
    


