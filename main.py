from doctest import debug
import os

from flask import Flask, render_template, request, session, redirect, flash,make_response,url_for
from flask.sessions import SecureCookieSession
from werkzeug.utils import secure_filename
from DBConnection import Db
from datetime import datetime
from datetime import date
import time
import json
import jsonify


AreaManagerImages = 'AreaManagerImages'

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app = Flask(__name__)
app.secret_key="xyss"
app.config['UPLOAD_FOLDER'] = AreaManagerImages
path='/home/SPS/'

@app.route('/')
def login():
    return render_template("admin/login.html")

@app.route('/logaction',methods=['post'])
def LoginAction():
    uname = request.form['username']
    paswd = request.form['password']
    q = "select * from login where email='" + uname + "' and password='" + paswd + "' and status!='inactive'"
    ob = Db()
    res = ob.selectOne(q)
    if res is not None:
        session['login'] = res['id']
        session['type'] = res['type']
        session['name'] = res['name']
        ob = Db()
        ob.update("update login set status='online',date_time=now() where id='"+str(session['login'])+"'")
        if res['type'] == 'admin':
            return redirect('/adminhome')
        elif res['type'] == 'trainer':
            ob=Db()
            img=ob.selectOne("select photo,branch from trainers where l_id='"+str(session['login'])+"'")
            session['photo']=img['photo']
            session['branch']=img['branch']
            return redirect('/teacherhome')
        elif res['type'] == 'area manager':
            ob=Db()
            img=ob.selectOne("select photo,area from area_manager where l_id='"+str(session['login'])+"'")
            session['photo']=img['photo']
            session['area']=img['area']
            return redirect('/area_managerhome')
        elif res['type'] == 'branch manager':
            ob=Db()
            img=ob.selectOne("select photo,branch from branch_manager where l_id='"+str(session['login'])+"'")
            session['photo']=img['photo']
            session['branch']=img['branch']
            return redirect('/branch_managerhome')
    if res is None:
        return '''<script>alert('Incurrect username or password');window.history.back()</script>'''

@app.route('/log_out')
def log_out():
    session.clear()
    return redirect('/')

# -----------------------------------------------admin------------------------------------------------------------

#HOME

@app.route('/adminhome')
def adminhome():
    if session.get('login'):
        ob=Db()
        trainers=ob.selectOne("SELECT COUNT(TYPE)AS trainers FROM login WHERE TYPE='trainer'")
        students=ob.selectOne("SELECT COUNT(TYPE)AS students FROM login WHERE TYPE='student'")
        area_managers=ob.selectOne("SELECT COUNT(TYPE)AS area_managers FROM login WHERE TYPE='area manager'")
        branch_managers=ob.selectOne("SELECT COUNT(TYPE)AS branch_managers FROM login WHERE TYPE='branch manager'")
        notice=ob.select("select * from notice where status='publish'")
        event=ob.select("select * from event where status='publish'")
        return render_template("admin/home.html",trainers=trainers,students=students,area_managers=area_managers,branch_managers=branch_managers,notice=notice,event=event)
    else:
        return redirect('/')


# MYPROFILE

@app.route('/viewprofile')
def viewprofile():
    if session.get('login'):
        ob=Db()
        admin=ob.selectOne("SELECT * FROM admin WHERE l_id='"+str(session['login'])+"'")
        return render_template("admin/view_profile.html",admin=admin)
    else:
        return redirect('/')

@app.route('/updateprofile/<a>',methods=['post'])
def updateprofile(a):
    if session.get('login'):
        name = request.form['name']
        gender = request.form['gender']
        dob = request.form['dob']
        mobile = request.form['mobile']
        email = request.form['email']
        photo = request.files['photo']
        ob = Db()
        if request.files is not None:
            if photo.filename!="":
                fname = time.strftime("%Y%m%d_%H%M%S")+".jpg"
                photo.save(r"/home/SPS/tuition/static/admin/"+fname)
                q="update admin set name='"+name+"',gender='"+gender+"',dob='"+dob+"',mobile='"+mobile+"',email='"+email+"',photo='"+fname+"' where l_id='"+str(a)+"'"
                ob=Db()
                result=ob.update(q)
            else:
                q="update admin set name='"+name+"',gender='"+gender+"',dob='"+dob+"',mobile='"+mobile+"',email='"+email+"' where l_id='"+str(a)+"'"
                ob=Db()
                result=ob.update(q)
        else:
            q="update admin set name='"+name+"',gender='"+gender+"',dob='"+dob+"',mobile='"+mobile+"',email='"+email+"' where l_id='"+str(a)+"'"
            result=ob.update(q)
        q = "update login set name='"+name+"',email='"+email+"' where id='" + str(a) + "'"
        ob = Db()
        ob.update(q)
        if result :
            session['name']=name
            return '''  <script>  alert('Updated');window.location='/viewprofile'</script> '''
        else:
            return '''  <script>  alert('No Changes');window.history.back()</script> '''
    else:
        return redirect('/')

# AREA MANAGER

@app.route('/addareamanager')
def AddAreaManager():
    if session.get('login'):
        ob = Db()
        res1 = ob.select("select * from branch where status='active'")
        resarea = ob.select("select * from area where status='active' ")
        rescountry = ob.select("select * from country where status='active' ")
        resstate = ob.select("select * from state where status='active' ")
        resdist = ob.select("select * from district where status='active' ")
        return render_template("admin/AddAreaManager.html",data=res1,area=resarea,country = rescountry,state = resstate,district = resdist)
    return redirect('/')

@app.route('/addareamanageraction', methods=["post"])
def AddAreaManagerAction():
    if session.get('login'):
        name = request.form['name']
        gender = request.form['gender']
        salary = request.form['salary']
        country = request.form['country']
        state = request.form['state']
        district = request.form['district']
        area = request.form['area']
        mail = request.form['mail']
        phone = request.form['phone']
        photo = request.files['photo']
        pswd = request.form['repassword']
        designation = 'area manager'
        ob = Db()
        fname = time.strftime("%Y%m%d_%H%M%S") + ".jpg"
        photo.save(r"/home/SPS/tuition/static/AreaManagerImages/" + fname)

        q = "insert into login values(null,'" + name + "','" + mail + "','" + pswd + "','" + designation + "','ofline','Pending','"+str(session['name'])+"')"
        id=ob.insert(q)
        q = "insert into staff_salary values(null,'"+str(id)+"','"+designation+"','"+salary+"','pending')"
        ob.insert(q)
        q = "insert into area_manager values(null,'"+str(id)+"','" + name + "','" + gender + "','" + country + "','" + state + "','" + district + "','" + area + "','" + mail + "','" + phone + "','" + fname + "','" + pswd + "','" + designation + "','" + salary + "','active')"
        result = ob.insert(q)
        if result:
            return '''  <script>  alert('Added successfully');window.location='/viewareamanager'</script> '''
        else:
            return '''  <script>  alert('Error!!!');window.history.back()</script> '''
    return redirect('/')

@app.route('/viewareamanager')
def ViewAreaManager():
    if session.get('login'):
        ob = Db()
        res = ob.select("select * from area_manager where status='active'")
        return render_template("admin/view_area_manager.html",val = res)
    else:
        return redirect('/')

@app.route('/delete_areamanager')
def delete_areamanager():
    if session.get('login'):
        lid = request.args.get('lid')
        ob = Db()
        ob.update("update area_manager set status='inactive'  where l_id='"+str(lid)+"'")
        ob = Db()
        ob.update("update login set status='inactive'  where id='"+str(lid)+"'")
        return '''<script>alert("Deleted");window.location='/viewareamanager';</script>'''
    else:
        return redirect('/')

@app.route('/editareamanager')
def editareamanager():
    if session.get('login'):
        lid = request.args.get('lid')
        ob = Db()
        res = ob.selectOne("select * from area_manager where l_id='" + str(lid) + "'  ")
        res1 = ob.select("select * from branch where status='active'")
        resarea = ob.select("select * from area where status='active' ")
        rescountry = ob.select("select * from country where status='active' ")
        resstate = ob.select("select * from state where status='active' ")
        resdist = ob.select("select * from district where status='active' ")
        return render_template("admin/edit_areamanager.html",val=res,data=res1,area=resarea,country = rescountry,state = resstate,district = resdist)
    else:
        return redirect('/')

@app.route('/updateareamanager/<a>', methods=["post"])
def updateareamanager(a):
    if session.get('login'):
        name = request.form['name']
        gender = request.form['gender']
        salary = request.form['salary']
        country = request.form['country']
        state = request.form['state']
        district = request.form['district']
        area = request.form['area']
        email = request.form['mail']
        phone = request.form['phone']
        photo = request.files['photo']
        ob = Db()
        import time
        if request.files is not None:
            if photo.filename!="":
                fname = time.strftime("%Y%m%d_%H%M%S")+".jpg"
                photo.save(r"/home/SPS/tuition/static/AreaManagerImages/"+fname)
                q="update area_manager set name='"+name+"',gender='"+gender+"',country='"+country+"',state='"+state+"',district='"+district+"',email='"+email+"',phone='"+phone+"',photo='"+fname+"',area='"+area+"',salary='"+salary+"' where l_id='"+str(a)+"'"
                ob=Db()
                result=ob.update(q)
            else:
                q="update area_manager set name='"+name+"',gender='"+gender+"',country='"+country+"',state='"+state+"',district='"+district+"',email='"+email+"',phone='"+phone+"',area='"+area+"',salary='"+salary+"' where l_id='"+str(a)+"'"
                ob=Db()
                result=ob.update(q)
        else:
            q="update area_manager set name='"+name+"',gender='"+gender+"',country='"+country+"',state='"+state+"',district='"+district+"',email='"+email+"',phone='"+phone+"',area='"+area+"',salary='"+salary+"' where l_id='"+str(a)+"'"
            result=ob.update(q)
        q = "update login set name='"+name+"',email='"+email+"' where id='" + str(a) + "'"
        ob = Db()
        ob.update(q)
        q = "update staff_salary set salary='"+salary+"' where l_id='" + str(a) + "'"
        ob.update(q)
        if result :
            return '''  <script>  alert('Updated');window.location='/viewareamanager'</script> '''
        else:
            return '''  <script>  alert('No Changes');window.history.back()</script> '''
    else:
        return redirect('/')

# BRANCH MANAGER

@app.route('/addbranchmanager')
def AddBranchManager():
    if session.get('login'):
        ob = Db()
        res1 = ob.select("select * from branch where status='active'")
        resarea = ob.select("select * from area where status='active' ")
        rescountry = ob.select("select * from country where status='active' ")
        resstate = ob.select("select * from state where status='active' ")
        resdist = ob.select("select * from district where status='active' ")
        return render_template("admin/AddBranchManager.html",area=resarea,data=res1,country = rescountry,state = resstate,district = resdist)
    else:
        return redirect('/')

@app.route('/addbranchmanageraction', methods=["post"])
def AddBranchManagerAction():
    if session.get('login'):
        name = request.form['name']
        gender = request.form['gender']
        salary = request.form['salary']
        country = request.form['country']
        state = request.form['state']
        district = request.form['district']
        area = request.form['area']
        mail = request.form['mail']
        phone = request.form['phone']
        photo = request.files['photo']
        pswd = request.form['repassword']
        designation = 'branch manager'
        branch = request.form['branch']
        ob = Db()

        fname = time.strftime("%Y%m%d_%H%M%S") + ".jpg"
        photo.save(r"/home/SPS/tuition/static/BranchManagerImages/" + fname)

        q = "insert into login values(null,'" + name + "','" + mail + "','" + pswd + "','" + designation + "','ofline','Pending','"+session['name']+"')"
        id=ob.insert(q)
        q = "insert into staff_salary values(null,'"+str(id)+"','"+designation+"','"+salary+"','pending')"
        ob.insert(q)
        q = "insert into notification values(null,'"+str(session['login'])+"','A new branch manager is added by admin','"+area+"','specified',now(),'unread')"
        ob.insert(q)
        q = "insert into branch_manager values(null,'"+str(id)+"','" + name + "','" + gender + "','" + country + "','" + state + "','" + district + "','" + area + "','" + mail + "','" + phone + "','" + fname + "','" + pswd + "','" + designation + "','" + branch + "','"+salary+"','active')"
        result = ob.insert(q)
        if result:
            return '''  <script>  alert('Added successfully');window.location='/viewbranchamanager'</script> '''
        else:
            return '''  <script>  alert('Error!!!');window.history.back()</script> '''
    else:
        return redirect('/')

@app.route('/viewbranchamanager')
def ViewBranchManager():
    if session.get('login'):
        ob = Db()
        res = ob.select("select * from branch_manager where status='active' ")
        return render_template("admin/view_branch_manager.html",val = res)
    else:
        return redirect('/')

@app.route('/editbranchmanager')
def editbranchmanager():
    if session.get('login'):
        ob = Db()
        lid = request.args.get('lid')
        res = ob.selectOne("select * from branch_manager where l_id='" + str(lid) + "'")
        res1 = ob.select("select * from branch where status='active'")
        resarea = ob.select("select * from area where status='active' ")
        rescountry = ob.select("select * from country where status='active' ")
        resstate = ob.select("select * from state where status='active' ")
        resdist = ob.select("select * from district where status='active' ")
        return render_template("admin/edit_branchmanager.html",val=res,area=resarea,data=res1,country = rescountry,state = resstate,district = resdist)
    else:
        return redirect('/')

@app.route('/updatebranchmanager/<a>', methods=["post"])
def updatebranchmanager(a):
    if session.get('login'):
        name = request.form['name']
        gender = request.form['gender']
        salary = request.form['salary']
        country = request.form['country']
        state = request.form['state']
        district = request.form['district']
        area = request.form['area']
        email = request.form['mail']
        phone = request.form['phone']
        photo = request.files['photo']
        branch = request.form['branch']
        ob = Db()
        import time
        if request.files is not None:
            if photo.filename!="":
                fname = time.strftime("%Y%m%d_%H%M%S")+".jpg"
                photo.save(r"/home/SPS/tuition/static/BranchManagerImages/"+fname)
                q="update branch_manager set name='"+name+"',gender='"+gender+"',country='"+country+"',state='"+state+"',district='"+district+"',email='"+email+"',phone='"+phone+"',photo='"+fname+"',area='"+area+"',branch='"+branch+"',salary='"+salary+"' where l_id='"+str(a)+"'"
                ob=Db()
                result=ob.update(q)
            else:
                q="update branch_manager set name='"+name+"',gender='"+gender+"',country='"+country+"',state='"+state+"',district='"+district+"',email='"+email+"',phone='"+phone+"',area='"+area+"',branch='"+branch+"',salary='"+salary+"' where l_id='"+str(a)+"'"
                ob=Db()
                result=ob.update(q)
        else:
            q="update branch_manager set name='"+name+"',gender='"+gender+"',country='"+country+"',state='"+state+"',district='"+district+"',email='"+email+"',phone='"+phone+"',area='"+area+"',branch='"+branch+"',salary='"+salary+"' where l_id='"+str(a)+"'"
            result=ob.update(q)
        q = "update login set name='"+name+"',email='"+email+"' where id='" + str(a) + "'"
        ob = Db()
        ob.update(q)
        q = "update staff_salary set salary='"+salary+"' where l_id='" + str(a) + "'"
        ob.update(q)
        if result :
            ob = Db()
            q = "insert into notification values(null,'"+str(session['login'])+"','"+name+" profile is updated by admin','"+area+"','specified',now(),'unread')"
            ob.insert(q)
            return '''  <script>  alert('Updated');window.location='/viewbranchamanager'</script> '''
        else:
            return '''  <script>  alert('No Changes');window.history.back()</script> '''
    else:
        return redirect('/')

@app.route('/delete_branchmanager')
def delete_branchmanager():
    if session.get('login'):
        lid = request.args.get('lid')
        ob = Db()
        ob.update("update branch_manager set status='inactive'  where l_id='"+str(lid)+"'")
        ob = Db()
        ob.update("update login set status='inactive'  where id='"+str(lid)+"'")
        ob = Db()
        name=ob.selectOne("select name,area from branch_manager where l_id='"+str(lid)+"'")
        ob = Db()
        q = "insert into notification values(null,'"+str(session['login'])+"','"+name['name']+" profile is deleted by admin','"+name['area']+"','specified',now(),'unread')"
        ob.insert(q)
        return '''<script>alert("Deleted");window.location='/viewbranchamanager';</script>'''
    else:
        return redirect('/')

# ACCOUNTANT

@app.route('/addaccountant')
def addaccountant():
    if session.get('login'):
        ob = Db()
        res1 = ob.select("select * from branch where status='active'")
        resarea = ob.select("select * from area where status='active' ")
        rescountry = ob.select("select * from country where status='active' ")
        resstate = ob.select("select * from state where status='active' ")
        resdist = ob.select("select * from district where status='active' ")
        return render_template("admin/add_accountant.html",data=res1,area=resarea,country = rescountry,state = resstate,district = resdist)
    else:
        return redirect('/')

@app.route('/add_accountant',methods=['POST'])
def add_accountant():
    if session.get('login'):
        name=request.form['name']
        gender=request.form['gender']
        area=request.form['area']
        branch=request.form['branch']
        join_date=request.form['join_date']
        country=request.form['country']
        street=request.form['street']
        city=request.form['city']
        po=request.form['po']
        dist=request.form['dist']
        pin=request.form['pin']
        state=request.form['state']
        email=request.form['email']
        mobile=request.form['mobile']
        address=request.form['address']
        photo=request.files['photo']
        salary=request.form['salary']
        password=request.form['repassword']
        remark=request.form['remark']

        import time
        fname=time.strftime("%Y%m%d_%H%M%S")+".jpg"
        photo.save(r"/home/SPS/tuition/static/accountant_photos/"+fname)

        ob=Db()
        q="insert into login values(null,'" + name + "','" + email + "','" + password + "','accountant','ofline','pending','"+str(session['name'])+"')"
        id=ob.insert(q)
        q = "insert into accountant values(null,'"+str(id)+"','"+name+"','"+gender+"','"+area+"','"+branch+"','"+pin+"','"+email+"','"+mobile+"','"+fname+"','"+salary+"','Active','"+join_date+"')"
        ob.insert(q)
        q = "insert into staff_salary values(null,'"+str(id)+"','accountant','"+salary+"','pending')"
        ob.insert(q)
        q = "insert into address values(null,'"+str(id)+"','"+street+"','"+city+"','"+po+"','"+pin+"','"+dist+"','"+state+"','"+country+"','"+address+"','"+remark+"','accountant')"
        ob.insert(q)
        return redirect('viewaccountant')
    else:
        return redirect('/')

@app.route('/viewaccountant')
def viewaccountant():
    if session.get('login'):
        ob = Db()
        q = "SELECT * FROM accountant where status='active'"
        acc = ob.select(q)
        return render_template("admin/view_accountant.html",val=acc)
    else:
        return redirect('/')

@app.route('/editaccountant')
def editaccountant():
    if session.get('login'):
        lid = request.args.get('lid')
        q="select * from accountant,address where accountant.l_id=address.l_id and accountant.l_id='"+str(lid)+"'"
        ob = Db()
        res=ob.selectOne(q)
        ob = Db()
        res1 = ob.select("select * from branch where status='active'")
        resarea = ob.select("select * from area where status='active' ")
        rescountry = ob.select("select * from country where status='active' ")
        resstate = ob.select("select * from state where status='active' ")
        resdist = ob.select("select * from district where status='active' ")
        return render_template("admin/edit_accountant.html",val=res,data=res1,area=resarea,country = rescountry,state = resstate,district = resdist)
    else:
        return redirect('/')

@app.route('/update_accountant/<a>',methods=['POST'])
def update_accountant(a):
    if session.get('login'):
        name=request.form['name']
        gender=request.form['gender']
        area=request.form['area']
        branch=request.form['branch']
        join_date=request.form['join_date']
        country=request.form['country']
        street=request.form['street']
        city=request.form['city']
        po=request.form['po']
        dist=request.form['dist']
        pin=request.form['pin']
        state=request.form['state']
        email=request.form['email']
        mobile=request.form['mobile']
        address=request.form['address']
        photo=request.files['photo']
        salary=request.form['salary']
        remark=request.form['remark']

        import time
        if request.files is not None:
            if photo.filename!="":
                fname = time.strftime("%Y%m%d_%H%M%S")+".jpg"
                photo.save(r"/home/SPS/tuition/static/accountant_photos/"+fname)
                q="update accountant set name='"+name+"',gender='"+gender+"',pin='"+pin+"',email='"+email+"',mobile='"+mobile+"',photo='"+fname+"',area='"+area+"',branch='"+branch+"',salary='"+salary+"',join_date='"+join_date+"' where l_id='"+str(a)+"'"
                ob=Db()
                result=ob.update(q)
            else:
                q="update accountant set name='"+name+"',gender='"+gender+"',pin='"+pin+"',email='"+email+"',mobile='"+mobile+"',area='"+area+"',branch='"+branch+"',salary='"+salary+"',join_date='"+join_date+"' where l_id='"+str(a)+"'"
                ob=Db()
                result=ob.update(q)
        else:
            q="update accountant set name='"+name+"',gender='"+gender+"',pin='"+pin+"',email='"+email+"',mobile='"+mobile+"',area='"+area+"',branch='"+branch+"',salary='"+salary+"',join_date='"+join_date+"' where l_id='"+str(a)+"'"
            result=ob.update(q)
        q = "update login set name='"+name+"',email='"+email+"' where id='" + str(a) + "'"
        ob = Db()
        ob.update(q)
        q = "update address set country='"+country+"',street='"+street+"',city='"+city+"',po='"+po+"',dist='"+dist+"',pin='"+pin+"',state='"+state+"',address='"+address+"',remark='"+remark+"' where l_id='" + str(a) + "'"
        ob = Db()
        ad=ob.update(q)
        if result or ad :
            return '''  <script>  alert('Updated');window.location='/viewaccountant'</script> '''
        else:
            return '''  <script>  alert('No Changes');window.history.back()</script> '''
    else:
        return redirect('/')

@app.route('/delete_accountant')
def delete_accountant():
    if session.get('login'):
        lid = request.args.get('lid')
        ob = Db()
        ob.update("update accountant set status='inactive'  where l_id='"+str(lid)+"'")
        ob = Db()
        ob.update("update login set status='inactive'  where id='"+str(lid)+"'")
        return '''<script>alert("Deleted");window.location='/viewaccountant';</script>'''
    else:
        return redirect('/')

# STUDENT

@app.route('/addstudent')
def addstudent():
    if session.get('login'):
        ob = Db()
        q = "SELECT * FROM course WHERE status='active'"
        crs = ob.select(q)
        ob = Db()
        q = "SELECT * FROM standard WHERE status='active'"
        std = ob.select(q)
        ob = Db()
        q = "SELECT * FROM subjects WHERE subjects.status='active'"
        sub = ob.select(q)
        ob = Db()
        q = "SELECT * FROM syllabus WHERE status='active'"
        syb = ob.select(q)
        ob = Db()
        q = "SELECT name FROM trainers WHERE status='available'"
        trn = ob.select(q)
        ob = Db()
        res = ob.select("select * from branch where status='active'")
        resarea = ob.select("select * from area where status='active' ")
        rescountry = ob.select("select * from country where status='active' ")
        resstate = ob.select("select * from state where status='active' ")
        resdist = ob.select("select * from district where status='active' ")
        return render_template("admin/add_student.html",area=resarea,crs=crs,std=std,sub=sub,syb=syb,trn=trn,data=res,country = rescountry,state = resstate,district = resdist)
    else:
        return redirect('/')

@app.route('/add_student',methods=['POST'])
def add_student():
    if session.get('login'):
        name=request.form['name']
        gender=request.form['gender']
        dob=request.form['dob']
        standard=request.form['standard']
        school=request.form['school']
        date_admn=request.form['date_admn']
        syllabus=request.form['syllabus']
        course=request.form['course']
        area=request.form['area']
        branch=request.form['branch']
        father=request.form['father']
        mother=request.form['mother']
        country=request.form['country']
        street=request.form['street']
        city=request.form['city']
        po=request.form['po']
        dist=request.form['dist']
        pin=request.form['pin']
        state=request.form['state']
        email=request.form['email']
        mobile=request.form['mobile']
        address=request.form['address']
        photo=request.files['photo']
        source=request.form['source']
        remark=request.form['remark']
        password=request.form['repassword']


        import time
        fname=time.strftime("%Y%m%d_%H%M%S")+".jpg"
        photo.save(r"/home/SPS/tuition/static/student_photos/"+fname)

        ob=Db()
        q="insert into login values(null,'" + name + "','" + email + "','" + password + "','student','ofline','pending','"+str(session['name'])+"')"
        id=ob.insert(q)
        q = "insert into students values(null,'"+str(id)+"','"+name+"','"+gender+"','"+dob+"','"+standard+"','"+school+"','"+date_admn+"','"+syllabus+"','"+course+"','"+father+"','"+mother+"','"+pin+"','"+email+"','"+mobile+"','"+fname+"','"+area+"','"+branch+"','"+source+"','pending')"
        ob.insert(q)
        q = "insert into student_fee values(null,'"+str(id)+"','0','pending')"
        ob.insert(q)
        q = "insert into address values(null,'"+str(id)+"','"+street+"','"+city+"','"+po+"','"+pin+"','"+dist+"','"+state+"','"+country+"','"+address+"','"+remark+"','student')"
        ob.insert(q)
        q = "insert into notification values(null,'"+str(session['login'])+"','A new student '"+name+"' is added',null,'general',now(),'unread')"
        ob.insert(q)
        return redirect('viewstudent')
    else:
        return redirect('/')

@app.route('/viewstudent')
def viewstudent():
    if session.get('login'):
        ob = Db()
        q = "SELECT * FROM students where status!='inactive'"
        stdts = ob.select(q)
        return render_template("admin/view_student.html",val=stdts)
    else:
        return redirect('/')

@app.route('/updatestudent')
def updatestudent():
    if session.get('login'):
        lid = request.args.get('lid')
        q="select * from students,address where students.l_id=address.l_id AND students.l_id='"+str(lid)+"'"
        ob = Db()
        res=ob.selectOne(q)
        ob = Db()
        q = "SELECT * FROM course WHERE status='active'"
        crs = ob.select(q)
        ob = Db()
        q = "SELECT * FROM standard WHERE status='active'"
        std = ob.select(q)
        ob = Db()
        q = "SELECT * FROM syllabus WHERE status='active'"
        syb = ob.select(q)
        ob = Db()
        q = "SELECT name FROM trainers WHERE status='available'"
        trn = ob.select(q)
        ob = Db()
        res2 = ob.select("select * from branch where status='active'")
        resarea = ob.select("select * from area where status='active' ")
        rescountry = ob.select("select * from country where status='active' ")
        resstate = ob.select("select * from state where status='active' ")
        resdist = ob.select("select * from district where status='active' ")
        return render_template("admin/edit_student.html",area=resarea,data=res,crs=crs,std=std,syb=syb,trn=trn,res=res2,country = rescountry,state = resstate,district = resdist)
    else:
        return redirect('/')

@app.route('/update_student/<a>',methods=['POST'])
def update_student(a):
    if session.get('login'):
        name=request.form['name']
        gender=request.form['gender']
        dob=request.form['dob']
        standard=request.form['standard']
        school=request.form['school']
        date_admn=request.form['date_admn']
        syllabus=request.form['syllabus']
        course=request.form['course']
        area=request.form['area']
        branch=request.form['branch']
        father=request.form['father']
        mother=request.form['mother']
        country=request.form['country']
        street=request.form['street']
        city=request.form['city']
        po=request.form['po']
        dist=request.form['dist']
        pin=request.form['pin']
        state=request.form['state']
        email=request.form['email']
        mobile=request.form['mobile']
        address=request.form['address']
        photo=request.files['photo']
        source=request.form['source']
        remark=request.form['remark']

        import time
        if request.files is not None:
            if photo.filename!="":
                fname = time.strftime("%Y%m%d_%H%M%S")+".jpg"
                photo.save(r"/home/SPS/tuition/static/student_photos/"+fname)
                q="update students set s_name='"+name+"',s_gender='"+gender+"',s_dob='"+dob+"',s_std='"+standard+"',s_school='"+school+"',date_admn='"+date_admn+"',syllabus='"+syllabus+"',course='"+course+"',father='"+father+"',mother='"+mother+"',pin='"+pin+"',email='"+email+"',mobile='"+mobile+"',photo='"+fname+"',area='"+area+"',branch='"+branch+"',source='"+source+"' where l_id='"+str(a)+"'"
                ob=Db()
                result=ob.update(q)
            else:
                q = "update students set s_name='"+name+"',s_gender='"+gender+"',s_dob='"+dob+"',s_std='"+standard+"',s_school='"+school+"',date_admn='"+date_admn+"',syllabus='"+syllabus+"',course='"+course+"',father='"+father+"',mother='"+mother+"',pin='"+pin+"',email='"+email+"',mobile='"+mobile+"',area='"+area+"',branch='"+branch+"',source='"+source+"' where l_id='" + str(a) + "'"
                ob = Db()
                result=ob.update(q)
        else:
            q = "update students set s_name='"+name+"',s_gender='"+gender+"',s_dob='"+dob+"',s_std='"+standard+"',s_school='"+school+"',date_admn='"+date_admn+"',syllabus='"+syllabus+"',course='"+course+"',father='"+father+"',mother='"+mother+"',pin='"+pin+"',email='"+email+"',mobile='"+mobile+"',area='"+area+"',branch='"+branch+"',source='"+source+"' where l_id='" + str(a) + "'"
            ob = Db()
            result=ob.update(q)
        q = "update login set name='"+name+"',email='"+email+"' where id='" + str(a) + "'"
        ob = Db()
        ob.update(q)
        q = "update address set country='"+country+"',street='"+street+"',city='"+city+"',po='"+po+"',dist='"+dist+"',pin='"+pin+"',state='"+state+"',address='"+address+"',remark='"+remark+"' where l_id='" + str(a) + "'"
        ob = Db()
        ad=ob.update(q)
        if result or ad :
            ob = Db()
            q = "insert into notification values(null,'"+str(session['login'])+"','"+name+"profile is updated','"+area+"','specified',now(),'unread')"
            ob.insert(q)
            return '''  <script>  alert('Updated');window.location='/viewstudent'</script> '''
        else:
            return '''  <script>  alert('No Changes');window.history.back()</script> '''
    else:
        return redirect('/')

@app.route('/delete_student')
def delete_student():
    if session.get('login'):
        lid = request.args.get('lid')
        ob = Db()
        ob.update("update students set status='inactive' where l_id='"+str(lid)+"'")
        ob = Db()
        ob.update("update login set status='inactive' where id='"+str(lid)+"'")
        return '''<script>alert("Deleted");window.location='/viewstudent';</script>'''
    else:
        return redirect('/')

#TRAINER

@app.route('/addtrainer')
def addtrainer():
    if session.get('login'):
        ob = Db()
        q = "SELECT * FROM course WHERE status='active'"
        crs = ob.select(q)
        ob = Db()
        q = "SELECT * FROM standard WHERE status='active'"
        std = ob.select(q)
        ob = Db()
        q = "SELECT * FROM subjects WHERE subjects.status='active'"
        sub = ob.select(q)
        ob = Db()
        q = "SELECT * FROM syllabus WHERE status='active'"
        syb = ob.select(q)
        ob = Db()
        res = ob.select("select * from branch where status='active'")
        resarea = ob.select("select * from area where status='active' ")
        rescountry = ob.select("select * from country where status='active' ")
        resstate = ob.select("select * from state where status='active' ")
        resdist = ob.select("select * from district where status='active' ")
        return render_template("admin/add_trainer.html",area=resarea,crs=crs,std=std,sub=sub,syb=syb,data=res,country = rescountry,state = resstate,district = resdist)
    else:
        return redirect('/')

@app.route('/add_trainer',methods=['POST'])
def add_trainer():
    if session.get('login'):
        name=request.form['name']
        gender=request.form['gender']
        standard=request.form['standard']
        syllabus=request.form['syllabus']
        subjects=request.form['subjects']
        area=request.form['area']
        branch=request.form['branch']
        join_date=request.form['join_date']
        country=request.form['country']
        street=request.form['street']
        city=request.form['city']
        po=request.form['po']
        dist=request.form['dist']
        pin=request.form['pin']
        state=request.form['state']
        email=request.form['email']
        mobile=request.form['mobile']
        address=request.form['address']
        photo=request.files['photo']
        salary=request.form['salary']
        remark=request.form['remark']
        password=request.form['repassword']


        import time
        fname=time.strftime("%Y%m%d_%H%M%S")+".jpg"
        photo.save(r"/home/SPS/tuition/static/trainers_photos/"+fname)

        ob=Db()
        q="insert into login values(null,'" + name + "','" + email + "','" + password + "','trainer','ofline','pending','"+str(session['name'])+"')"
        id=ob.insert(q)
        q = "insert into trainers values(null,'"+str(id)+"','"+name+"','"+gender+"','"+syllabus+"','"+standard+"','"+subjects+"','"+area+"','"+branch+"','"+pin+"','"+email+"','"+mobile+"','"+fname+"','"+salary+"','available','"+join_date+"')"
        ob.insert(q)
        q = "insert into address values(null,'"+str(id)+"','"+street+"','"+city+"','"+po+"','"+pin+"','"+dist+"','"+state+"','"+country+"','"+address+"','"+remark+"','trainer')"
        ob.insert(q)
        q = "insert into staff_salary values(null,'"+str(id)+"','trainer','"+salary+"','pending')"
        ob.insert(q)
        return redirect('viewtrainer')
    else:
        return redirect('/')

@app.route('/viewtrainer')
def viewtrainer():
    if session.get('login'):
        ob = Db()
        q = "SELECT * FROM trainers where status!='inactive'"
        trns = ob.select(q)
        return render_template("admin/view_trainer.html",val=trns)
    else:
        return redirect('/')

@app.route('/updatetrainer')
def updatetrainer():
    if session.get('login'):
        lid = request.args.get('lid')
        q="select * from trainers,address where trainers.l_id=address.l_id AND trainers.l_id='"+str(lid)+"'"
        ob = Db()
        res=ob.selectOne(q)
        ob = Db()
        q = "SELECT * FROM course WHERE status='active'"
        crs = ob.select(q)
        ob = Db()
        q = "SELECT * FROM standard WHERE status='active'"
        std = ob.select(q)
        ob = Db()
        q = "SELECT * FROM subjects WHERE subjects.status='active'"
        sub = ob.select(q)
        ob = Db()
        q = "SELECT * FROM syllabus WHERE status='active'"
        syb = ob.select(q)
        ob = Db()
        res2 = ob.select("select * from branch where status='active'")
        resarea = ob.select("select * from area where status='active' ")
        rescountry = ob.select("select * from country where status='active' ")
        resstate = ob.select("select * from state where status='active' ")
        resdist = ob.select("select * from district where status='active' ")
        return render_template("admin/edit_trainer.html",area=resarea,data=res,crs=crs,std=std,sub=sub,syb=syb,res=res2,country = rescountry,state = resstate,district = resdist)
    else:
        return redirect('/')

@app.route('/update_trainer/<a>',methods=['POST'])
def update_trainer(a):
    if session.get('login'):
        name=request.form['name']
        gender=request.form['gender']
        standard=request.form['standard']
        syllabus=request.form['syllabus']
        subjects=request.form['subjects']
        area=request.form['area']
        branch=request.form['branch']
        join_date=request.form['join_date']
        country=request.form['country']
        street=request.form['street']
        city=request.form['city']
        po=request.form['po']
        dist=request.form['dist']
        pin=request.form['pin']
        state=request.form['state']
        email=request.form['email']
        mobile=request.form['mobile']
        address=request.form['address']
        photo=request.files['photo']
        salary=request.form['salary']
        remark=request.form['remark']

        import time
        if request.files is not None:
            if photo.filename!="":
                fname = time.strftime("%Y%m%d_%H%M%S")+".jpg"
                photo.save(r"/home/SPS/tuition/static/trainers_photos/"+fname)
                q="update trainers set name='"+name+"',gender='"+gender+"',p_standard='"+standard+"',syllabus='"+syllabus+"',p_subject='"+subjects+"',pin='"+pin+"',email='"+email+"',mobile='"+mobile+"',photo='"+fname+"',area='"+area+"',branch='"+branch+"',salary='"+salary+"',join_date='"+join_date+"' where l_id='"+str(a)+"'"
                ob=Db()
                result=ob.update(q)
            else:
                q = "update trainers set name='"+name+"',gender='"+gender+"',p_standard='"+standard+"',syllabus='"+syllabus+"',p_subject='"+subjects+"',pin='"+pin+"',email='"+email+"',mobile='"+mobile+"',area='"+area+"',branch='"+branch+"',salary='"+salary+"',join_date='"+join_date+"' where l_id='" + str(a) + "'"
                ob = Db()
                result=ob.update(q)
        else:
            q = "update trainers set name='"+name+"',gender='"+gender+"',p_standard='"+standard+"',syllabus='"+syllabus+"',p_subject='"+subjects+"',pin='"+pin+"',email='"+email+"',mobile='"+mobile+"',area='"+area+"',branch='"+branch+"',salary='"+salary+"',join_date='"+join_date+"' where l_id='" + str(a) + "'"
            ob = Db()
            result=ob.update(q)
        q = "update login set name='"+name+"',email='"+email+"' where id='" + str(a) + "'"
        ob = Db()
        ob.update(q)
        q = "update address set country='"+country+"',street='"+street+"',city='"+city+"',po='"+po+"',dist='"+dist+"',pin='"+pin+"',state='"+state+"',address='"+address+"',remark='"+remark+"' where l_id='" + str(a) + "'"
        ob = Db()
        ad=ob.update(q)
        if result or ad :
            return '''  <script>  alert('Updated');window.location='/viewtrainer'</script> '''
        else:
            return '''  <script>  alert('No Changes');window.history.back()</script> '''
    else:
        return redirect('/')

@app.route('/delete_trainer')
def delete_trainer():
    if session.get('login'):
        lid = request.args.get('lid')
        ob = Db()
        ob.update("update trainers set status='inactive'  where l_id='"+str(lid)+"'")
        ob = Db()
        ob.update("update login set status='inactive'  where id='"+str(lid)+"'")
        return '''<script>alert("Deleted");window.location='/viewtrainer';</script>'''
    else:
        return redirect('/')

#AREA

@app.route('/addarea')
def AddArea():
    if session.get('login'):
        ob = Db()
        rescountry = ob.select("select * from country where status='active' ")
        resstate = ob.select("select * from state where status='active' ")
        resdist = ob.select("select * from district where status='active' ")
        return render_template("admin/AddArea.html",country = rescountry,state = resstate,district = resdist)
    else:
        return redirect('/')

@app.route('/addareaaction',methods=["post"])
def AddAreaAction():
    if session.get('login'):
        name = request.form['name']
        country = request.form['country']
        state = request.form['state']
        district = request.form['district']
        address = request.form['address']
        ob = Db()
        numrows = None

        q = "insert into area values(null,'" + name + "','" + country + "','" + state + "','" + district + "','" + address + "','"+str(session['name'])+"','active')"
        result = ob.insert(q)
        if result:
            return '''  <script>  alert('Added Successfully');window.location='/viewarea'</script> '''
        else:
            return '''  <script>  alert('Error!!!');window.history.back()</script> '''
    else:
        return redirect('/')

@app.route('/viewarea')
def viewarea():
    if session.get('login'):
        ob = Db()
        q = "SELECT * FROM area"
        area = ob.select(q)
        return render_template("admin/view_area.html",val=area)
    else:
        return redirect('/')

@app.route('/editarea')
def editarea():
    if session.get('login'):
        id = request.args.get('id')
        q="select * from area where id='"+str(id)+"'"
        ob = Db()
        res=ob.selectOne(q)
        rescountry = ob.select("select * from country where status='active' ")
        resstate = ob.select("select * from state where status='active' ")
        resdist = ob.select("select * from district where status='active' ")
        return render_template("admin/edit_area.html",val=res,country = rescountry,state = resstate,district = resdist)
    else:
        return redirect('/')

@app.route('/updatearea/<a>',methods=["post"])
def updatearea(a):
    if session.get('login'):
        name = request.form['name']
        country = request.form['country']
        state = request.form['state']
        district = request.form['district']
        address = request.form['address']
        ob = Db()
        numrows = None

        q = "update area set area_name='" + name + "',country='" + country + "',state='" + state + "',district='" + district + "',address='" + address + "' where id='"+str(a)+"'"
        result = ob.update(q)
        if result:
            return '''  <script>  alert('Updated');window.location='/viewarea'</script> '''
        else:
            return '''  <script>  alert('No Changes');window.history.back()</script> '''
    else:
        return redirect('/')

@app.route('/activate_area')
def activate_area():
    if session.get('login'):
        id = request.args.get('id')
        ob = Db()
        ob.update("update area set status='active'  where id='"+str(id)+"'")
        return '''<script>alert("Activated");window.location='/viewarea';</script>'''
    else:
        return redirect('/')

@app.route('/deactivate_area')
def deactivate_area():
    if session.get('login'):
        id = request.args.get('id')
        ob = Db()
        ob.update("update area set status='inactive'  where id='"+str(id)+"'")
        return '''<script>alert("Deactivated");window.location='/viewarea';</script>'''
    else:
        return redirect('/')

# BRANCH

@app.route('/addbranch')
def AddBranch():
    if session.get('login'):
        ob = Db()
        resarea = ob.select("select * from area where status='active' ")
        rescountry = ob.select("select * from country where status='active' ")
        resstate = ob.select("select * from state where status='active' ")
        resdist = ob.select("select * from district where status='active' ")
        return render_template("admin/AddBranch.html",area=resarea,country = rescountry,state = resstate,district = resdist)
    else:
        return redirect('/')

@app.route('/addbranchaction',methods=["post"])
def AddBranchAction():
    if session.get('login'):
        area = request.form['area']
        name = request.form['name']
        country = request.form['country']
        state = request.form['state']
        district = request.form['district']
        address = request.form['address']
        ob = Db()
        numrows = None

        q = "insert into branch values(null,'" + area + "','" + name + "','" + country + "','" + state + "','" + district + "','" + address + "','"+str(session['name'])+"','active')"
        result = ob.insert(q)
        if result:
            return '''  <script>  alert('Added Successfully');window.location='/viewbranch'</script> '''
        else:
            return '''  <script>  alert('Error!!!');window.history.back()</script> '''
    else:
        return redirect('/')

@app.route('/viewbranch')
def viewbranch():
    if session.get('login'):
        ob = Db()
        q = "SELECT branch.*,area.area_name FROM branch,area where branch.area_id=area.id"
        branch = ob.select(q)
        return render_template("admin/view_branch.html",val=branch)
    else:
        return redirect('/')

@app.route('/editbranch')
def editbranch():
    if session.get('login'):
        id = request.args.get('id')
        q="select * from branch where id='"+str(id)+"'"
        ob = Db()
        res=ob.selectOne(q)
        ob = Db()
        resarea = ob.select("select * from area where status='active' ")
        rescountry = ob.select("select * from country where status='active' ")
        resstate = ob.select("select * from state where status='active' ")
        resdist = ob.select("select * from district where status='active' ")
        return render_template("admin/edit_branch.html",val=res,area=resarea,country = rescountry,state = resstate,district = resdist)
    else:
        return redirect('/')

@app.route('/updatebranch/<a>',methods=["post"])
def updatebranch(a):
    if session.get('login'):
        area = request.form['area']
        name = request.form['name']
        country = request.form['country']
        state = request.form['state']
        district = request.form['district']
        address = request.form['address']
        ob = Db()
        numrows = None

        q = "update branch set area_id='" + area + "',branch_name='" + name + "',country='" + country + "',state='" + state + "',district='" + district + "',address='" + address + "' where id='"+str(a)+"'"
        result = ob.update(q)
        if result:
            return '''  <script>  alert('Updated');window.location='/viewbranch'</script> '''
        else:
            return '''  <script>  alert('No changes');window.history.back()</script> '''
    else:
        return redirect('/')

@app.route('/activate_branch')
def activate_branch():
    if session.get('login'):
        id = request.args.get('id')
        ob = Db()
        ob.update("update branch set status='active'  where id='"+str(id)+"'")
        return '''<script>alert("Activated");window.location='/viewbranch';</script>'''
    else:
        return redirect('/')

@app.route('/deactivate_branch')
def deactivate_branch():
    if session.get('login'):
        id = request.args.get('id')
        ob = Db()
        ob.update("update branch set status='inactive'  where id='"+str(id)+"'")
        return '''<script>alert("Deactivated");window.location='/viewbranch';</script>'''
    else:
        return redirect('/')

#ACCOUNTS

#EXPENSE

@app.route('/addexpense')
def addexpense():
    if session.get('login'):
        return render_template("admin/add_expense.html")
    else:
        return redirect('/')

@app.route('/addexpenseaction',methods=["post"])
def addexpenseaction():
    if session.get('login'):
        purpose = request.form['purpose']
        amount = request.form['amount']
        comment = request.form['comment']
        file=request.files['file']

        import time
        fname=time.strftime("%Y%m%d_%H%M%S")+".jpg"
        file.save(r"/home/SPS/tuition/static/expense/"+fname)

        ob = Db()
        q = "insert into expense values(null,'" + purpose + "','" + amount + "','" + fname + "','" + comment + "',curdate(),'"+str(session['name'])+"','active')"
        result = ob.insert(q)
        if result:
            return '''  <script>  alert('Added Successfully');window.location='/viewexpense'</script> '''
        else:
            return '''  <script>  alert('Error!!!');window.history.back()</script> '''
    else:
        return redirect('/')

@app.route('/viewexpense')
def viewexpense():
    if session.get('login'):
        ob = Db()
        q = "SELECT * FROM expense "
        expense = ob.select(q)
        return render_template("admin/view_expense.html",val=expense)
    else:
        return redirect('/')


#INCOME

@app.route('/addincome')
def addincome():
    if session.get('login'):
        today=date.today()
        return render_template("admin/add_income.html",today=today)
    else:
        return redirect('/')

@app.route('/addincomeaction',methods=["post"])
def addincomeaction():
    if session.get('login'):
        type = request.form['type']
        date = request.form['date']
        amount = request.form['amount']
        comment = request.form['comment']
        file=request.files['file']
        payed_by = request.form['payed_by']

        import time
        fname=time.strftime("%Y%m%d_%H%M%S")+".jpg"
        file.save(r"/home/SPS/tuition/static/income/"+fname)

        ob = Db()
        q = "insert into income values(null,'" + type + "','" + date + "','" + amount + "','" + fname + "','" + comment + "',curdate(),'" + payed_by + "','"+str(session['name'])+"','active')"
        result = ob.insert(q)
        if result:
            return '''  <script>  alert('Added Successfully');window.location='/viewincome'</script> '''
        else:
            return '''  <script>  alert('Error!!!');window.history.back()</script> '''
    else:
        return redirect('/')

@app.route('/viewincome')
def viewincome():
    if session.get('login'):
        ob = Db()
        q = "SELECT * FROM income "
        income = ob.select(q)
        return render_template("admin/view_income.html",val=income)
    else:
        return redirect('/')


#LOCATION COUNTRY,STATE,DISTRICT

@app.route('/addlocation')
def addlocation():
    if session.get('login'):
        ob = Db()
        rescountry = ob.select("select * from country where status='active' ")
        resstate = ob.select("select * from state where status='active' ")
        resdist = ob.select("select * from district where status='active' ")
        return render_template("admin/add_location.html",country=rescountry,state=resstate,district=resdist)
    else:
        return redirect('/')

@app.route('/addcountry',methods=['POST'])
def addcountry():
    if session.get('login'):
        country = request.form['country']
        ob = Db()
        q = "SELECT name FROM country where name='"+country+"'"
        cnty = ob.selectOne(q)
        ob = Db()
        if cnty is None :
            q = "insert into country values(null,'" + country + "','active')"
            result = ob.insert(q)
            if result:
                return '''  <script>  alert('Added Successfully');window.location='/viewcountry'</script> '''
            else:
                return '''  <script>  alert('Error!!!');window.history.back()</script> '''
        else:
            return '''  <script>  alert('Already added');window.history.back()</script> '''
    else:
        return redirect('/')

@app.route('/viewcountry')
def viewcountry():
    if session.get('login'):
        ob = Db()
        q = "SELECT * FROM country"
        cnty = ob.select(q)
        return render_template("admin/view_country.html",country=cnty)
    else:
        return redirect('/')

@app.route('/activate_country')
def activate_country():
    if session.get('login'):
        id = request.args.get('id')
        ob = Db()
        ob.update("update country set status='active'  where id='"+str(id)+"'")
        return '''<script>alert("Activated");window.location='/viewcountry';</script>'''
    else:
        return redirect('/')

@app.route('/deactivate_country')
def deactivate_country():
    if session.get('login'):
        id = request.args.get('id')
        ob = Db()
        ob.update("update country set status='inactive'  where id='"+str(id)+"'")
        return '''<script>alert("Deactivated");window.location='/viewcountry';</script>'''
    else:
        return redirect('/')

@app.route('/addstate',methods=['POST'])
def addstate():
    if session.get('login'):
        state = request.form['state']
        country = request.form['country']
        ob = Db()
        q = "SELECT name FROM state where name='"+state+"' and country_id='"+country+"'"
        st = ob.selectOne(q)
        ob = Db()
        if st is None :
            q = "insert into state values(null,'" + country + "','" + state + "','active')"
            result = ob.insert(q)
            if result:
                return '''  <script>  alert('Added Successfully');window.location='/viewstate'</script> '''
            else:
                return '''  <script>  alert('Error!!!');window.history.back()</script> '''
        else:
            return '''  <script>  alert('Already added');window.history.back()</script> '''
    else:
        return redirect('/')

@app.route('/viewstate')
def viewstate():
    if session.get('login'):
        ob = Db()
        q = "SELECT country.name AS country, state.* FROM state,country WHERE country.id=state.country_id"
        st = ob.select(q)
        return render_template("admin/view_state.html",state=st)
    else:
        return redirect('/')

@app.route('/activate_state')
def activate_state():
    if session.get('login'):
        id = request.args.get('id')
        ob = Db()
        ob.update("update state set status='active'  where id='"+str(id)+"'")
        return '''<script>alert("Activated");window.location='/viewstate';</script>'''
    else:
        return redirect('/')

@app.route('/deactivate_state')
def deactivate_state():
    if session.get('login'):
        id = request.args.get('id')
        ob = Db()
        ob.update("update state set status='inactive'  where id='"+str(id)+"'")
        return '''<script>alert("Deactivated");window.location='/viewstate';</script>'''
    else:
        return redirect('/')

@app.route('/adddistrict',methods=['POST'])
def adddistrict():
    if session.get('login'):
        district = request.form['district']
        state = request.form['state']
        country = request.form['country']
        ob = Db()
        q = "SELECT district FROM district where district='"+district+"' and state_id='"+state+"' and country_id='"+country+"'"
        st = ob.selectOne(q)
        ob = Db()
        if st is None :
            q = "insert into district values(null,'" + country + "','" + state + "','" + district + "','active')"
            result = ob.insert(q)
            if result:
                return '''  <script>  alert('Added Successfully');window.location='/viewdistrict'</script> '''
            else:
                return '''  <script>  alert('Error!!!');window.history.back()</script> '''
        else:
            return '''  <script>  alert('Already added');window.history.back()</script> '''
    else:
        return redirect('/')

@app.route('/viewdistrict')
def viewdistrict():
    if session.get('login'):
        ob = Db()
        q = "SELECT district.*,state.name AS state,country.name AS country FROM district,state,country where country.id=district.country_id and state.id=district.state_id"
        dist = ob.select(q)
        return render_template("admin/view_district.html",district=dist)
    else:
        return redirect('/')

@app.route('/activate_district')
def activate_district():
    if session.get('login'):
        id = request.args.get('id')
        ob = Db()
        ob.update("update district set status='active'  where id='"+str(id)+"'")
        return '''<script>alert("Activated");window.location='/viewdistrict';</script>'''
    else:
        return redirect('/')

@app.route('/deactivate_district')
def deactivate_district():
    if session.get('login'):
        id = request.args.get('id')
        ob = Db()
        ob.update("update district set status='inactive'  where id='"+str(id)+"'")
        return '''<script>alert("Deactivated");window.location='/viewdistrict';</script>'''
    else:
        return redirect('/')


@app.route('/viewnotification')
def viewnotification():
    if session.get('login'):
        ob = Db()
        noti = ob.select("SELECT notification.*,login.name FROM notification LEFT JOIN login ON login.id=notification._from WHERE  notification._to='"+str(session['type'])+"' OR notification.type='general'")
        return render_template("admin/view_notifications.html",noti=noti)
    else:
        return redirect('/')

@app.route('/notificationarea')
def notificationarea():
    if session.get('login'):
        ob = Db()
        noti = ob.select("SELECT notification.*,login.name FROM notification LEFT JOIN login ON login.id=notification._from WHERE  notification.status='unread' AND  notification._to='"+str(session['type'])+"' OR notification.type='general'")
        if len(noti) == 0:
            result='''<li class="nav-item dropdown mr-3"><a href="/viewnotification" id="notifications" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false" class="nav-link dropdown-toggle text-gray-400 px-1"><i class="fa fa-bell"></i></a>
            <div aria-labelledby="notifications" class="dropdown-menu">
                <a href="/viewnotification" class="dropdown-item">
                    <div class="d-flex align-items-center">
                      <div class="icon icon-sm bg-violet text-white"><i class="fas fa-bell"></i></div>
                      <div class="text ml-2">
                        <p class="mb-0">No New Notification</p>
                      </div>
                    </div></a>
              <div class="dropdown-divider"></div><a href="/viewnotification" class="dropdown-item text-center"><small class="font-weight-bold headings-font-family text-uppercase">View all notifications</small></a>
            </div>
          </li>'''
        else:
            for noti in noti:
                  result='''<li class="nav-item dropdown mr-3"><a href="/viewnotification" id="notifications" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false" class="nav-link dropdown-toggle text-gray-400 px-1"><i class="fa fa-bell"></i><span class="notification-icon"></span></a>
                <div aria-labelledby="notifications" class="dropdown-menu">
                  <a href="/viewnotification" class="dropdown-item">
                    <div class="d-flex align-items-center">
                      <div class="icon icon-sm bg-violet text-white"><i class="fas fa-envelope"></i></div>
                      <div class="text ml-2">
                        <p class="mb-0">'''+noti['notification']+'''</p>
                      </div>
                    </div></a>
                  <div class="dropdown-divider"></div><a href="/viewnotification" class="dropdown-item text-center"><small class="font-weight-bold headings-font-family text-uppercase">View all notifications</small></a>
                </div>
              </li>'''

        resp = make_response(json.dumps(result))
        resp.status_code = 200
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp
    else:
        return redirect('/')


@app.route('/makeasread')
def makeasread():
    if session.get('login'):
        id = request.args.get('id')
        ob = Db()
        ob.update("update notification set status='read'  where n_id='"+str(id)+"'")
        return '''<script>window.location='/viewnotification';</script>'''
    else:
        return redirect('/')

@app.route('/makeasunread')
def makeasunread():
    if session.get('login'):
        id = request.args.get('id')
        ob = Db()
        ob.update("update notification set status='unread'  where n_id='"+str(id)+"'")
        return '''<script>window.location='/viewnotification';</script>'''
    else:
        return redirect('/')


#ANNOUNCEMENT

#NOTICE

@app.route('/addnotice')
def addnotice():
    if session.get('login'):
        return render_template("admin/add_notice.html")
    else:
        return redirect('/')

@app.route('/addnoticeaction',methods=['POST'])
def addnoticeaction():
    if session.get('login'):
        title = request.form['title']
        date = request.form['date']
        notice = request.form['notice']
        ob = Db()
        q = "insert into notice values(null,'" + title + "','" + date + "','" + notice + "','"+str(session['name'])+"',curdate(),'publish')"
        result = ob.insert(q)
        if result:
            return '''  <script>  alert('Added Successfully');window.location='/viewnotice'</script> '''
        else:
            return '''  <script>  alert('Error!!!');window.history.back()</script> '''
    else:
        return redirect('/')

@app.route('/viewnotice')
def viewnotice():
    if session.get('login'):
        ob = Db()
        q = "SELECT * from notice"
        notice = ob.select(q)
        return render_template("admin/view_notice.html",notice=notice)
    else:
        return redirect('/')

@app.route('/published_notice')
def published_notice():
    if session.get('login'):
        id = request.args.get('id')
        ob = Db()
        ob.update("update notice set status='publish'  where id='"+str(id)+"'")
        return '''<script>window.location='/viewnotice';</script>'''
    else:
        return redirect('/')

@app.route('/unpublished_notice')
def unpublished_notice():
    if session.get('login'):
        id = request.args.get('id')
        ob = Db()
        ob.update("update notice set status='unpublish'  where id='"+str(id)+"'")
        return '''<script>window.location='/viewnotice';</script>'''
    else:
        return redirect('/')


#EVENT


@app.route('/addnevenet')
def addnevenet():
    if session.get('login'):
        return render_template("admin/add_event.html")
    else:
        return redirect('/')

@app.route('/addevenetaction',methods=['POST'])
def addevenetaction():
    if session.get('login'):
        title = request.form['title']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        note = request.form['note']
        file=request.files['file']
        import time
        fname=time.strftime("%Y%m%d_%H%M%S")+".jpg"
        file.save(r"/home/SPS/tuition/static/event/"+fname)
        ob = Db()
        q = "insert into event values(null,'" + title + "','" + start_date + "','" + end_date + "','" + fname + "','" + note + "','"+str(session['name'])+"',curdate(),'publish')"
        result = ob.insert(q)
        if result:
            return '''  <script>  alert('Added Successfully');window.location='/viewevenet'</script> '''
        else:
            return '''  <script>  alert('Error!!!');window.history.back()</script> '''
    else:
        return redirect('/')

@app.route('/viewevenet')
def viewevenet():
    if session.get('login'):
        ob = Db()
        q = "SELECT * from event"
        notice = ob.select(q)
        ln=0
        if len(notice) == 0:
            ln = 1
        return render_template("admin/view_event.html",notice=notice,ln=ln)
    else:
        return redirect('/')

@app.route('/published_evenet')
def published_evenet():
    if session.get('login'):
        id = request.args.get('id')
        ob = Db()
        ob.update("update event set status='publish'  where id='"+str(id)+"'")
        return '''<script>window.location='/viewevenet';</script>'''
    else:
        return redirect('/')

@app.route('/unpublished_evenet')
def unpublished_evenet():
    if session.get('login'):
        id = request.args.get('id')
        ob = Db()
        ob.update("update event set status='unpublish'  where id='"+str(id)+"'")
        return '''<script>window.location='/viewevenet';</script>'''
    else:
        return redirect('/')

@app.route('/viewongoingclass')
def viewongoingclass():
    if session.get('login'):
        today=datetime.today().strftime('%A')
        ob=Db()
        sd=("select schedules.*,trainers.name,trainers.l_id,trainers.area,trainers.branch,COUNT(student_schedule.id)AS students,attendance_tr.start,attendance_tr.end,attendance_tr.status as startorend,attendance_tr.hours,attendance_tr.count_st,attendance_tr.id as at_id from student_schedule,trainers,schedules left join attendance_tr on schedules.id=attendance_tr.schedule_id and date=curdate()  where student_schedule.schedule_id=schedules.id and days like '%"+today+"%' and trainers.l_id=schedules.trainer_id GROUP BY schedules.id ")
        print(sd)
        sdl=ob.select(sd)
        if sdl:
            sdll=sdl
        else:
            sdll=''
        return render_template("admin/view_ongoingclass.html",sdll=sdll)
    else:
        return redirect('/')






@app.route('/downloadsAD')
def downloadsAD():
    if session.get('login'):
        ob = Db()
        q = "SELECT * from downloads where status='publish'"
        downloads = ob.select(q)
        return render_template("admin/view_downloads.html",downloads=downloads)
    else:
        return redirect('/')

@app.route('/adddownloadsAD')
def adddownloadsAD():
    if session.get('login'):
        ob=Db()

        return render_template("admin/add_downloads.html")
    else:
        return redirect('/')

@app.route('/adddownloadsaction',methods=['POST'])
def adddownloadsaction():
    if session.get('login'):
        note = request.form['note']
        file=request.files['file']
        import time
        name=secure_filename(file.filename)
        pre=time.strftime("%Y%m%d_%H%M%S")
        fname=str(pre)+str(name)
        file.save(r"/home/SPS/tuition/static/downloads/"+fname)
        ob = Db()
        q = "insert into downloads values(null,'" + fname + "','" + note + "','"+str(session['name'])+"',curdate(),'publish')"
        result = ob.insert(q)
        if result:
            return '''  <script>  alert('Added Successfully');window.location='/downloadsAD'</script> '''
        else:
            return '''  <script>  alert('Error!!!');window.history.back()</script> '''
    else:
        return redirect('/')

@app.route('/delete_downloads')
def delete_downloads():
    if session.get('login'):
        id = request.args.get('id')
        ob = Db()
        ob.update("update downloads set status='unpublish'  where id='"+str(id)+"'")
        return '''<script>window.location='/downloadsAD';</script>'''
    else:
        return redirect('/')

@app.route('/documentsAD')
def documentsAD():
    if session.get('login'):
        ob = Db()
        q = "SELECT * from documents where status='publish'"
        documents = ob.select(q)
        return render_template("admin/view_documents.html",documents=documents)
    else:
        return redirect('/')

@app.route('/addlinksAD')
def addlinksAD():
    if session.get('login'):
        ob=Db()

        return render_template("admin/add_links.html")
    else:
        return redirect('/')

@app.route('/addlinksaction',methods=['POST'])
def addlinksaction():
    if session.get('login'):
        title = request.form['title']
        url = request.form['url']
        ob = Db()
        q = "insert into documents values(null,'" + title + "','" + url + "',curdate(),'"+str(session['name'])+"','publish')"
        result = ob.insert(q)
        if result:
            return '''  <script>  alert('Added Successfully');window.location='/documentsAD'</script> '''
        else:
            return '''  <script>  alert('Error!!!');window.history.back()</script> '''
    else:
        return redirect('/')

@app.route('/delete_links')
def delete_links():
    if session.get('login'):
        id = request.args.get('id')
        ob = Db()
        ob.update("update documents set status='unpublish'  where id='"+str(id)+"'")
        return '''<script>window.location='/documentsAD';</script>'''
    else:
        return redirect('/')


@app.route('/viewstatitics')
def viewstatitics():
    if session.get('login'):
        ob=Db()
        statitics=ob.select("SELECT COUNT(students.s_id) AS students,COUNT(trainers.t_id) AS trainers ,students.area,students.branch FROM students LEFT JOIN trainers ON students.area=trainers.area AND students.branch=trainers.branch")
        return render_template("admin/view_statitics.html",statitics=statitics)
    else:
        return redirect('/')

#SCHEDULE

@app.route('/viewallscheduleAD')
def viewallscheduleAD():
    if session.get('login'):
        ob=Db()
        sd=("SELECT schedules.*,COUNT(student_schedule.id)AS students,trainers.name,trainers.area FROM trainers,schedules left join student_schedule on student_schedule.schedule_id=schedules.id WHERE trainers.l_id=schedules.trainer_id GROUP BY schedules.id")
        print(sd)
        sdll=ob.select(sd)
        return render_template("admin/view_all_schedule.html",sdll=sdll)
    else:
        return redirect('/')


@app.route('/create_scheduleAD')
def create_scheduleAD():
    if session.get('login'):
        ob=Db()
        sb = "select * from subjects"
        sb = ob.select(sb)
        res = ob.select("select * from branch where status='active'")
        return render_template("admin/create_schedule.html",sub=sb,data=res)
    else:
        return redirect('/')

@app.route('/create_scheduleactionAD', methods=["post"])
def create_scheduleactionAD():
    if session.get('login'):
        ob = Db()
        branch = request.form['branch']
        day = request.form.getlist('day[]')
        print(day)
        days=''
        for i in day:
            j = i.replace(' ', '')
            days=days+'"'+j+'",'
        dayss=days[:-1]
        daysss='['+dayss+']'
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        subjects = request.form['subjects']
        trainers = request.form['trainers']

        data=ob.selectOne("select * from schedules where days='" + daysss + "' and start_time='" +start_time+ "' and end_time='" +end_time+ "' and subject='" +subjects+ "' and branch='" +branch+ "' and add_by='" +str(session['name'])+ "' ")
        if data:
            return '''  <script>  alert('Already Exist');window.history.back()</script> '''
        else:
            q = "insert into schedules values(null,'" + daysss + "','" + start_time + "','" + end_time + "','" + subjects + "','" + trainers + "','" + branch+ "','" + str(session['name']) + "','active')"
            print(q)
            ob.insert(q)
            return '''<script>alert('Created');window.location='/viewallscheduleAD';</script>'''
    else:
        return redirect('/')


@app.route('/trainerselectAD',methods=['post'])
def trainerselectAD():
    if session.get('login'):
        branch = request.args.get('branch')
        day = request.args.get('days')
        da=day.replace('[','')
        days=da.replace(']','')
        print(days)
        start_time = request.args.get('starttime')
        end_time = request.args.get('endtime')
        subject = request.args.get('subject')
        ob=Db()
        trainers_id=("select trainer_id from schedules where days='"+days+"' and start_time  between '" +start_time+ "' and '" +end_time+ "' and end_time  between '" +start_time+ "' and '" +end_time+ "' or start_time='" +start_time+ "' or start_time='" +end_time+ "' or end_time='" +start_time+ "' or end_time='" +end_time+ "' and subject='"+subject+"' and branch='"+branch+"'")
        print(trainers_id)
        trainer_id=ob.select(trainers_id)
        check =""
        for trainer_id in trainer_id:
            ch= "l_id!='"+trainer_id['trainer_id']+"' and "
            check=check+ch
        print(check)
        if trainer_id:
            print(trainer_id['trainer_id'])
            trainers =ob.select("select name,l_id,p_standard from trainers where "+check+" branch='"+branch+"' and p_subject='"+subject+"' and status!='inactive'")
            print(trainers)
        else:
            trainers=ob.select("select name,l_id,p_standard from trainers where branch='"+branch+"' and p_subject='"+subject+"' and status!='inactive' ")
        if trainers:
            result=['<option value="" selected disabled>Trainer</option>']
            for trainers in trainers:
                resul = '''<option value=''' + str(trainers['l_id']) + '''>''' + trainers['name']+''' - Std '''+trainers['p_standard'] + '''</option>'''
                result.append(resul)
        else:
            result = '''<option value="">Not available</option>'''
        resp = make_response(json.dumps(result))
        resp.status_code = 200
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp
    else:
        return redirect('/')



@app.route('/aisgn_subjectAD')
def aisgn_subjectAD():
    if session.get('login'):
        lid = request.args.get('lid')
        ob=Db()
        sd = ob.selectOne("select * from students where l_id = '" + str(lid) +"'")
        q = "SELECT * FROM subjects WHERE subjects.status='active'"
        sub = ob.select(q)
        schedule=ob.select("select schedules.*,trainers.name,student_schedule.id as ss_id from schedules,trainers,student_schedule where schedules.trainer_id=trainers.l_id and student_schedule.schedule_id=schedules.id and student_schedule.s_id='" + str(lid) +"' and student_schedule.status='active'")
        ln=0
        if len(schedule) == 0:
            ln = 1
        return render_template("admin/aisgn_subject.html",sd=sd,sub=sub,schedule=schedule,ln=ln)
    else:
        return redirect('/')

@app.route('/deletestudenscheduleAD',methods=['post'])
def deletestudenscheduleAD():
    if session.get('login'):
        id = request.args.get('sid')
        print(id)
        ob = Db()
        ob.delete("delete from student_schedule where id='"+str(id)+"'")
        return '''<script>window.location.reload();</script>'''
    else:
        return redirect('/')

@app.route('/scheduleselectAD',methods=['post'])
def scheduleselectAD():
    if session.get('login'):
        std = request.args.get('std')
        subject = request.args.get('subject')
        branch = request.args.get('branch')
        ob=Db()
        trainers_id=("select l_id from trainers where p_standard='"+std+"' and p_subject='"+subject+"' and branch='"+branch+"'")
        trainer_id=ob.select(trainers_id)
        check =""
        for trainer_id in trainer_id:
            ch= "trainers.l_id='"+str(trainer_id['l_id'])+"' or "
            check=check+ch
        check=check[:-3]
        print(check)
        if trainer_id:
            trainers =ob.select("select trainers.name,schedules.* from trainers LEFT JOIN schedules ON schedules.trainer_id=trainers.l_id  where "+check+" and trainers.branch='"+branch+"' and trainers.status!='inactive'")
            print(trainers)
        else:
            trainers=''
        if trainers:
            result=['<option value selected disabled>Schedule</option>']
            for trainers in trainers:
                s = datetime.strptime(str(trainers['start_time']), "%H:%M")
                start=s.strftime("%I:%M %p")
                e = datetime.strptime(str(trainers['end_time']), "%H:%M")
                end = e.strftime("%I:%M %p")
                resul = '''<option value=''' + str(trainers['id']) + '''>''' + trainers['name']+''' , days '''+trainers['days'].replace('"',' ') + ''' at '''+start + ''' to '''+ end + '''</option>'''
                result.append(resul)
        else:
            result = '''<option value >Not available</option>'''
        resp = make_response(json.dumps(result))
        resp.status_code = 200
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp
    else:
        return redirect('/')

@app.route('/student_scheduleasignAD', methods=["post"])
def student_scheduleasignAD():
    if session.get('login'):
        s_id = request.form['s_id']
        schedule = request.form['schedule']
        subject = request.form['subject']
        ob=Db()
        data=ob.selectOne("select * from student_schedule where s_id='" + str(s_id) + "' and schedule_id='" + str(schedule) + "' ")
        if data:
            return '''<script>alert('Already Exist');window.history.back();</script>'''
        else:
            q = "insert into student_schedule values(null,'" + str(s_id) + "','" + str(schedule) + "','" + subject + "',now(),'" + str(session['name']) + "','active')"
            result=ob.insert(q)
            if result:
                return '''<script>window.location.reload();</script>'''
            else:
                return '''<script>alert('Error!!');window.history.back();</script>'''
    else:
        return redirect('/')



@app.route('/viewattendanceAD')
def viewattendanceAD():
    if session.get('login'):
        lid = request.args.get('lid')
        ob=Db()
        atd=ob.select("SELECT students.s_name,attendance.date,attendance.attendance,schedules.start_time,schedules.end_time FROM students,attendance,schedules WHERE students.l_id=attendance.s_id AND attendance.schedule_id=schedules.id and students.l_id='"+str(lid)+"'")
        return render_template("admin/view_attendancestd.html",atd=atd)
    else:
        return redirect('/')










































































# -----------------------------------------------teacher------------------------------------------------------------

#HOME

@app.route('/viewprofileTR')
def viewprofileTR():
    if session.get('login'):
        ob=Db()
        trainers=ob.selectOne("SELECT * FROM trainers WHERE l_id='"+str(session['login'])+"'")
        return render_template("teacher/view_profile.html",trainers=trainers)
    else:
        return redirect('/')

@app.route('/teacherhome')
def teacherhome():
    if session.get('login'):
        ob=Db()
        notice=ob.select("select * from notice where status='publish'")
        event=ob.select("select * from event where status='publish'")
        return render_template("teacher/home.html",notice=notice,event=event)
    else:
        return redirect('/')

@app.route('/viewscheduleTR')
def viewscheduleTR():
    if session.get('login'):
        today=datetime.today().strftime('%A')
        ob=Db()
        sd=("select schedules.*,COUNT(student_schedule.id)AS students,attendance_tr.start,attendance_tr.end,attendance_tr.status as startorend,attendance_tr.hours,attendance_tr.count_st,attendance_tr.id as at_id from student_schedule,schedules left join attendance_tr on schedules.id=attendance_tr.schedule_id and date=curdate()  where student_schedule.schedule_id=schedules.id and schedules.trainer_id='"+str(session['login'])+"' and schedules.branch='"+str(session['branch'])+"' and days like '%"+today+"%' GROUP BY schedules.id ")
        print(sd)
        sdl=ob.select(sd)
        if sdl:
            sdll=sdl
        else:
            sdll=''
        return render_template("teacher/schedule.html",sdll=sdll)
    else:
        return redirect('/')

@app.route('/viewallscheduleTR')
def viewallscheduleTR():
    if session.get('login'):
        ob=Db()
        sd=("SELECT schedules.*,COUNT(student_schedule.id)AS students FROM student_schedule,schedules WHERE student_schedule.schedule_id=schedules.id GROUP BY schedules.id and schedules.trainer_id='"+str(session['login'])+"' and schedules.branch='"+str(session['branch'])+"'")
        print(sd)
        sdll=ob.select(sd)
        return render_template("teacher/view_all_schedule.html",sdll=sdll)
    else:
        return redirect('/')


@app.route('/start_class')
def start_class():
    if session.get('login'):
        id = request.args.get('id')
        ob = Db()
        id=ob.insert("insert into attendance_tr values(null,'"+str(session['login'])+"','"+str(id)+"',curdate(),'Pending',NOW(),null,null,null,'started')")
        return '''<script>window.location='/viewscheduleTR';</script>'''
    else:
        return redirect('/')

@app.route('/end_class')
def end_class():
    if session.get('login'):
        id = request.args.get('id')
        ob = Db()
        start=ob.selectOne("select start,schedule_id,date from attendance_tr where id='"+str(id)+"'")
        count=ob.selectOne("select count(id)as count from attendance where date='"+str(start['date'])+"' and schedule_id='"+start['schedule_id']+"' and attendance='Present'")
        start_time=datetime.strptime(start['start'],'%Y-%m-%d %H:%M:%S')
        hour=(start_time-datetime.now())
        hh=round(24-(hour.seconds/3600)%24,2)
        ob.update("update attendance_tr set end=now(), status='ended',hours='"+str(hh)+"',count_st='"+str(count['count'])+"',attendance='Present' where id='"+str(id)+"'")
        return '''<script>window.location='/viewscheduleTR';</script>'''
    else:
        return redirect('/')


@app.route('/take_std_attendance')
def take_std_attendance():
    if session.get('login'):
        id = request.args.get('id')
        ob = Db()
        std=ob.select("select students.l_id,students.s_name,student_schedule.schedule_id,attendance.attendance from students,student_schedule left join attendance on student_schedule.schedule_id=attendance.schedule_id and attendance.date=curdate() and attendance.s_id=student_schedule.s_id where students.l_id=student_schedule.s_id and student_schedule.schedule_id='"+str(id)+"'")
        return render_template("teacher/student_attendance.html",std=std)
    else:
        return redirect('/')

@app.route('/present_std')
def present_std():
    if session.get('login'):
        id = request.args.get('id')
        lid = request.args.get('lid')
        ob = Db()
        ob.insert("insert into attendance values(null,'"+str(lid)+"','"+str(id)+"',curdate(),'Present','"+str(session['name'])+"','active')")
        return redirect('/take_std_attendance?id='+id)
    else:
        return redirect('/')

@app.route('/absent_std')
def absent_std():
    if session.get('login'):
        id = request.args.get('id')
        lid = request.args.get('lid')
        ob = Db()
        ob.insert("insert into attendance values(null,'"+str(lid)+"','"+str(id)+"',curdate(),'Absent','"+str(session['name'])+"','active')")
        return redirect('/take_std_attendance?id='+id)
    else:
        return redirect('/')

@app.route('/viewmystudents')
def viewmystudents():
    if session.get('login'):
        ob=Db()
        atd=ob.select("SELECT students.*,address.* FROM students,address,schedules LEFT JOIN student_schedule ON schedules.id=student_schedule.schedule_id AND schedules.trainer_id='"+str(session['login'])+"'  WHERE students.l_id=student_schedule.s_id AND students.l_id=address.l_id GROUP BY student_schedule.s_id")
        return render_template("teacher/view_mystudents.html",atd=atd)
    else:
        return redirect('/')

@app.route('/viewattendanceTR')
def viewattendanceTR():
    if session.get('login'):
        lid = request.args.get('lid')
        ob=Db()
        atd=ob.select("SELECT students.s_name,attendance.date,attendance.attendance,schedules.start_time,schedules.end_time FROM students,attendance,schedules WHERE students.l_id=attendance.s_id AND attendance.schedule_id=schedules.id AND attendance.add_by='"+str(session['name'])+"' and students.l_id='"+str(lid)+"'")
        return render_template("teacher/view_attendance.html",atd=atd)
    else:
        return redirect('/')





@app.route('/notificationareaTR')
def notificationareaTR():
    if session.get('login'):
        ob = Db()
        noti = ob.select("SELECT notification.*,login.name FROM notification LEFT JOIN login ON login.id=notification._from WHERE  notification.status='unread' AND  notification._to=(SELECT trainers.name FROM trainers WHERE l_id='"+str(session['login'])+"') OR notification.type='general'")
        if len(noti) == 0:
            result='''<li class="nav-item dropdown mr-3"><a href="/viewnotificationTR" id="notifications" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false" class="nav-link dropdown-toggle text-gray-400 px-1"><i class="fa fa-bell"></i></a>
            <div aria-labelledby="notifications" class="dropdown-menu">
                <a href="/viewnotificationTR" class="dropdown-item">
                    <div class="d-flex align-items-center">
                      <div class="icon icon-sm bg-violet text-white"><i class="fas fa-bell"></i></div>
                      <div class="text ml-2">
                        <p class="mb-0">No New Notification</p>
                      </div>
                    </div></a>
              <div class="dropdown-divider"></div><a href="/viewnotificationTR" class="dropdown-item text-center"><small class="font-weight-bold headings-font-family text-uppercase">View all notifications</small></a>
            </div>
          </li>'''
        else:
            for noti in noti:
                  result='''<li class="nav-item dropdown mr-3"><a href="/viewnotificationAM" id="notifications" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false" class="nav-link dropdown-toggle text-gray-400 px-1"><i class="fa fa-bell"></i><span class="notification-icon"></span></a>
                <div aria-labelledby="notifications" class="dropdown-menu">
                  <a href="/viewnotificationTR" class="dropdown-item">
                    <div class="d-flex align-items-center">
                      <div class="icon icon-sm bg-violet text-white"><i class="fas fa-envelope"></i></div>
                      <div class="text ml-2">
                        <p class="mb-0">'''+noti['notification']+'''</p>
                      </div>
                    </div></a>
                  <div class="dropdown-divider"></div><a href="/viewnotificationTR" class="dropdown-item text-center"><small class="font-weight-bold headings-font-family text-uppercase">View all notifications</small></a>
                </div>
              </li>'''
        resp = make_response(json.dumps(result))
        resp.status_code = 200
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp
    else:
        return redirect('/')


@app.route('/viewnotificationTR')
def viewnotificationTR():
    if session.get('login'):
        ob = Db()
        noti = ob.select("SELECT notification.*,login.name FROM notification LEFT JOIN login ON login.id=notification._from WHERE _to=(SELECT trainers.name FROM trainers WHERE l_id='"+str(session['login'])+"') OR notification.type='general'")
        return render_template("teacher/view_notification.html",noti=noti)
    else:
        return redirect('/')

@app.route('/makeasreadTR')
def makeasreadTR():
    if session.get('login'):
        id = request.args.get('id')
        ob = Db()
        ob.update("update notification set status='read'  where n_id='"+str(id)+"'")
        return '''<script>window.location='/viewnotificationTR';</script>'''
    else:
        return redirect('/')

@app.route('/makeasunreadTR')
def makeasunreadTR():
    if session.get('login'):
        id = request.args.get('id')
        ob = Db()
        ob.update("update notification set status='unread'  where n_id='"+str(id)+"'")
        return '''<script>window.location='/viewnotificationTR';</script>'''
    else:
        return redirect('/')



@app.route('/downloadsTR')
def downloadsTR():
    if session.get('login'):
        ob = Db()
        q = "SELECT * from downloads where status='publish'"
        downloads = ob.select(q)
        return render_template("teacher/view_downloads.html",downloads=downloads)
    else:
        return redirect('/')









# -----------------------------------------------area managerhome------------------------------------------------------------

#HOME

@app.route('/viewprofileAR')
def viewprofileAR():
    if session.get('login'):
        ob=Db()
        area_manager=ob.selectOne("SELECT * FROM area_manager WHERE l_id='"+str(session['login'])+"'")
        return render_template("area_manager/view_profile.html",area_manager=area_manager)
    else:
        return redirect('/')

@app.route('/area_managerhome')
def area_managerhome():
    if session.get('login'):
        ob=Db()
        trainers=ob.selectOne("SELECT COUNT(TYPE)AS trainers FROM login,trainers WHERE login.TYPE='trainer' and login.id=trainers.l_id and trainers.area='"+str(session['area'])+"'")
        students=ob.selectOne("SELECT COUNT(TYPE)AS students FROM login,students WHERE login.TYPE='student' and login.id=students.l_id and students.area='"+str(session['area'])+"' ")
        branch_managers=ob.selectOne("SELECT COUNT(TYPE)AS branch_managers FROM login,branch_manager WHERE login.TYPE='branch manager' and login.id=branch_manager.l_id and branch_manager.area='"+str(session['area'])+"' and login.status!='inactive' ")
        notice=ob.select("select * from notice where status='publish'")
        event=ob.select("select * from event where status='publish'")
        return render_template("area_manager/home.html",trainers=trainers,students=students,branch_managers=branch_managers,notice=notice,event=event)
    else:
        return redirect('/')

@app.route('/addbranchmanagerAM')
def addbranchmanagerAM():
    if session.get('login'):
        ob = Db()
        res1 = ob.select("select * from branch where area_id=(select id from area where area_name='"+str(session['area'])+"') and status='active'")
        return render_template("area_manager/add_branchmanager.html",data=res1)
    else:
        return redirect('/')

@app.route('/addbranchmanageractionAM', methods=["post"])
def addbranchmanageractionAM():
    if session.get('login'):
        name = request.form['name']
        gender = request.form['gender']
        salary = request.form['salary']
        mail = request.form['mail']
        phone = request.form['phone']
        photo = request.files['photo']
        pswd = request.form['repassword']
        designation = 'branch manager'
        branch = request.form['branch']
        addedby = session['name']
        area = session['area']
        ob = Db()
        data=ob.selectOne("select country,state,district from area_manager where l_id='"+str(session['login'])+"'")
        country =data['country']
        state = data['state']
        district =data['district']
        fname = time.strftime("%Y%m%d_%H%M%S") + ".jpg"
        photo.save(r"/home/SPS/tuition/static/BranchManagerImages/" + fname)

        q = "insert into login values(null,'" + name + "','" + mail + "','" + pswd + "','" + designation + "','ofline','Pending','"+addedby+"')"
        id=ob.insert(q)
        q = "insert into staff_salary values(null,'"+str(id)+"','"+designation+"','"+salary+"','pending')"
        ob.insert(q)
        q = "insert into branch_manager values(null,'"+str(id)+"','" + name + "','" + gender + "','" + country + "','" + state + "','" + district + "','" + area + "','" + mail + "','" + phone + "','" + fname + "','" + pswd + "','" + designation + "','" + branch + "','"+salary+"','active')"
        result = ob.insert(q)
        if result:
            return '''  <script>  alert('Added successfully');window.location='/viewbranchamanagerAM'</script> '''
        else:
            return '''  <script>  alert('Error!!!');window.history.back()</script> '''
    else:
        return redirect('/')

@app.route('/viewbranchamanagerAM')
def ViewBranchManagerAM():
    if session.get('login'):
        ob = Db()
        res = ob.select("select * from branch_manager where area= '"+str(session['area'])+"' and status='active'")
        return render_template("area_manager/view_branchmanager.html",val = res)
    else:
        return redirect('/')

@app.route('/editbranchmanagerAM')
def editbranchmanagerAM():
    if session.get('login'):
        ob = Db()
        lid = request.args.get('lid')
        res = ob.selectOne("select * from branch_manager where l_id='" + str(lid) + "'")
        res1 = ob.select("select * from branch where area_id=(select id from area where area_name='"+str(session['area'])+"') and status='active'")
        return render_template("area_manager/edit_branchmanager.html",val=res,data=res1)
    else:
        return redirect('/')

@app.route('/updatebranchmanagerAM/<a>', methods=["post"])
def updatebranchmanagerAM(a):
    if session.get('login'):
        name = request.form['name']
        gender = request.form['gender']
        salary = request.form['salary']
        email = request.form['mail']
        phone = request.form['phone']
        photo = request.files['photo']
        branch = request.form['branch']
        ob = Db()
        data=ob.selectOne("select country,state,district from area_manager where l_id='"+str(session['login'])+"'")
        country =data['country']
        state = data['state']
        district =data['district']
        import time
        if request.files is not None:
            if photo.filename!="":
                fname = time.strftime("%Y%m%d_%H%M%S")+".jpg"
                photo.save(r"/home/SPS/tuition/static/BranchManagerImages/"+fname)
                q="update branch_manager set name='"+name+"',gender='"+gender+"',country='"+country+"',state='"+state+"',district='"+district+"',email='"+email+"',phone='"+phone+"',photo='"+fname+"',branch='"+branch+"',salary='"+salary+"' where l_id='"+str(a)+"'"
                ob=Db()
                result=ob.update(q)
            else:
                q="update branch_manager set name='"+name+"',gender='"+gender+"',country='"+country+"',state='"+state+"',district='"+district+"',email='"+email+"',phone='"+phone+"',branch='"+branch+"',salary='"+salary+"' where l_id='"+str(a)+"'"
                ob=Db()
                result=ob.update(q)
        else:
            q="update branch_manager set name='"+name+"',gender='"+gender+"',country='"+country+"',state='"+state+"',district='"+district+"',email='"+email+"',phone='"+phone+"',branch='"+branch+"',salary='"+salary+"' where l_id='"+str(a)+"'"
            result=ob.update(q)
        q = "update login set name='"+name+"',email='"+email+"' where id='" + str(a) + "'"
        ob = Db()
        ob.update(q)
        q = "update staff_salary set salary='"+salary+"' where l_id='" + str(a) + "'"
        ob.update(q)
        if result :
            return '''  <script>  alert('Updated');window.location='/viewbranchamanagerAM'</script> '''
        else:
            return '''  <script>  alert('No Changes');window.history.back()</script> '''
    else:
        return redirect('/')

@app.route('/delete_branchmanagerAM')
def delete_branchmanagerAM():
    if session.get('login'):
        lid = request.args.get('lid')
        ob = Db()
        ob.update("update branch_manager set status='inactive'  where l_id='"+str(lid)+"'")
        ob = Db()
        ob.update("update login set status='inactive' where id='"+str(lid)+"'")
        return '''<script>alert("Deleted");window.location='/viewbranchamanagerAM';</script>'''
    else:
        return redirect('/')

@app.route('/viewstudentAM')
def viewstudentAM():
    if session.get('login'):
        ob = Db()
        q = "SELECT * FROM students where area='"+str(session['area'])+"' and status!='inactive'"
        stdts = ob.select(q)
        return render_template("area_manager/view_student.html",val=stdts)
    else:
        return redirect('/')


@app.route('/addstudentAM')
def addstudentAM():
    if session.get('login'):
        ob = Db()
        q = "SELECT * FROM course WHERE status='active'"
        crs = ob.select(q)
        ob = Db()
        q = "SELECT * FROM standard WHERE status='active'"
        std = ob.select(q)
        ob = Db()
        q = "SELECT * FROM subjects WHERE subjects.status='active'"
        sub = ob.select(q)
        ob = Db()
        q = "SELECT * FROM syllabus WHERE status='active'"
        syb = ob.select(q)
        ob = Db()
        res = ob.select("select * from branch where status='active' and area_id=(select id from area where area_name='"+str(session['area'])+"')")
        return render_template("area_manager/add_student.html",crs=crs,std=std,sub=sub,syb=syb,data=res)
    else:
        return redirect('/')

@app.route('/add_studentAM',methods=['POST'])
def add_studentAM():
    if session.get('login'):
        name=request.form['name']
        gender=request.form['gender']
        dob=request.form['dob']
        standard=request.form['standard']
        school=request.form['school']
        date_admn=request.form['date_admn']
        syllabus=request.form['syllabus']
        course=request.form['course']
        branch=request.form['branch']
        father=request.form['father']
        mother=request.form['mother']
        street=request.form['street']
        city=request.form['city']
        po=request.form['po']
        pin=request.form['pin']
        email=request.form['email']
        mobile=request.form['mobile']
        address=request.form['address']
        photo=request.files['photo']
        source=request.form['source']
        remark=request.form['remark']
        password=request.form['repassword']
        area = session['area']
        ob = Db()
        data=ob.selectOne("select country,state,district from area_manager where l_id='"+str(session['login'])+"'")
        country =data['country']
        state = data['state']
        dist =data['district']

        import time
        fname=time.strftime("%Y%m%d_%H%M%S")+".jpg"
        photo.save(r"/home/SPS/tuition/static/student_photos/"+fname)

        ob=Db()
        q="insert into login values(null,'" + name + "','" + email + "','" + password + "','student','ofline','pending','"+str(session['name'])+"')"
        ob.insert(q)
        q = "insert into students values(null,'"+str(id)+"','"+name+"','"+gender+"','"+dob+"','"+standard+"','"+school+"','"+date_admn+"','"+syllabus+"','"+course+"','"+father+"','"+mother+"','"+pin+"','"+email+"','"+mobile+"','"+fname+"','"+area+"','"+branch+"','"+source+"','pending')"
        result=ob.insert(q)
        q = "insert into student_fee values(null,'"+str(id)+"','0','pending')"
        ob.insert(q)
        q = "insert into address values(null,'"+str(id)+"','"+street+"','"+city+"','"+po+"','"+pin+"','"+dist+"','"+state+"','"+country+"','"+address+"','"+remark+"','student')"
        ad=ob.insert(q)
        # q = "insert into notification values(null,'"+str(session['login'])+"','A new student '"+name+"' is added','admin','specified',now(),'unread')"
        # ob.insert(q)
        if result or ad :
            return '''  <script>  alert('Added Successfully');window.location='/viewstudentAM'</script> '''
        else:
            return '''  <script>  alert('Error!!');window.history.back()</script> '''
    else:
        return redirect('/')

@app.route('/updatestudentAM')
def updatestudentAM():
    if session.get('login'):
        lid = request.args.get('lid')
        q="select * from students,address where students.l_id=address.l_id AND students.l_id='"+str(lid)+"'"
        ob = Db()
        res=ob.selectOne(q)
        ob = Db()
        q = "SELECT * FROM course WHERE status='active'"
        crs = ob.select(q)
        ob = Db()
        q = "SELECT * FROM standard WHERE status='active'"
        std = ob.select(q)
        ob = Db()
        q = "SELECT * FROM syllabus WHERE status='active'"
        syb = ob.select(q)
        ob = Db()
        res2 = ob.select("select * from branch where status='active' and area_id=(select id from area where area_name='"+str(session['area'])+"')")
        return render_template("area_manager/edit_student.html",data=res,crs=crs,std=std,syb=syb,res=res2)
    else:
        return redirect('/')

@app.route('/update_studentAM/<a>',methods=['POST'])
def update_studentAM(a):
    if session.get('login'):
        name=request.form['name']
        gender=request.form['gender']
        dob=request.form['dob']
        standard=request.form['standard']
        school=request.form['school']
        date_admn=request.form['date_admn']
        syllabus=request.form['syllabus']
        course=request.form['course']
        branch=request.form['branch']
        father=request.form['father']
        mother=request.form['mother']
        street=request.form['street']
        city=request.form['city']
        po=request.form['po']
        pin=request.form['pin']
        email=request.form['email']
        mobile=request.form['mobile']
        address=request.form['address']
        photo=request.files['photo']
        source=request.form['source']
        remark=request.form['remark']
        ob = Db()
        import time
        if request.files is not None:
            if photo.filename!="":
                fname = time.strftime("%Y%m%d_%H%M%S")+".jpg"
                photo.save(r"/home/SPS/tuition/static/student_photos/"+fname)
                q="update students set s_name='"+name+"',s_gender='"+gender+"',s_dob='"+dob+"',s_std='"+standard+"',s_school='"+school+"',date_admn='"+date_admn+"',syllabus='"+syllabus+"',course='"+course+"',father='"+father+"',mother='"+mother+"',pin='"+pin+"',email='"+email+"',mobile='"+mobile+"',photo='"+fname+"',branch='"+branch+"',source='"+source+"' where l_id='"+str(a)+"'"
                ob=Db()
                result=ob.update(q)
            else:
                q = "update students set s_name='"+name+"',s_gender='"+gender+"',s_dob='"+dob+"',s_std='"+standard+"',s_school='"+school+"',date_admn='"+date_admn+"',syllabus='"+syllabus+"',course='"+course+"',father='"+father+"',mother='"+mother+"',pin='"+pin+"',email='"+email+"',mobile='"+mobile+"',branch='"+branch+"',source='"+source+"' where l_id='" + str(a) + "'"
                ob = Db()
                result=ob.update(q)
        else:
            q = "update students set s_name='"+name+"',s_gender='"+gender+"',s_dob='"+dob+"',s_std='"+standard+"',s_school='"+school+"',date_admn='"+date_admn+"',syllabus='"+syllabus+"',course='"+course+"',father='"+father+"',mother='"+mother+"',pin='"+pin+"',email='"+email+"',mobile='"+mobile+"',branch='"+branch+"',source='"+source+"' where l_id='" + str(a) + "'"
            ob = Db()
            result=ob.update(q)
        q = "update login set name='"+name+"',email='"+email+"' where id='" + str(a) + "'"
        ob = Db()
        ob.update(q)
        q = "update address set street='"+street+"',city='"+city+"',po='"+po+"',pin='"+pin+"',address='"+address+"',remark='"+remark+"' where l_id='" + str(a) + "'"
        ob = Db()
        ad=ob.update(q)
        if result or ad :
            # ob = Db()
            # q = "insert into notification values(null,'"+str(session['login'])+"','"+name+"profile is updated','"+area+"','specified',now(),'unread')"
            # ob.insert(q)
            return '''  <script>  alert('Updated');window.location='/viewstudentAM'</script> '''
        else:
            return '''  <script>  alert('No Changes');window.history.back()</script> '''
    else:
        return redirect('/')

@app.route('/delete_studentAM')
def delete_studentAM():
    if session.get('login'):
        lid = request.args.get('lid')
        ob = Db()
        ob.update("update students set status='inactive' where l_id='"+str(lid)+"'")
        ob = Db()
        ob.update("update login set status='inactive' where id='"+str(lid)+"'")
        return '''<script>alert("Deleted");window.location='/viewstudentAM';</script>'''
    else:
        return redirect('/')

@app.route('/viewtrainerAM')
def viewtrainerAM():
    if session.get('login'):
        ob = Db()
        q = "SELECT * FROM trainers where area='"+str(session['area'])+"'and status!='inactive'"
        trns = ob.select(q)
        return render_template("area_manager/view_trainer.html",val=trns)
    else:
        return redirect('/')

@app.route('/addtrainerAM')
def addtrainerAM():
    if session.get('login'):
        ob = Db()
        q = "SELECT * FROM course WHERE status='active'"
        crs = ob.select(q)
        ob = Db()
        q = "SELECT * FROM standard WHERE status='active'"
        std = ob.select(q)
        ob = Db()
        q = "SELECT * FROM subjects WHERE subjects.status='active'"
        sub = ob.select(q)
        ob = Db()
        q = "SELECT * FROM syllabus WHERE status='active'"
        syb = ob.select(q)
        ob = Db()
        res = ob.select("select * from branch where status='active' and area_id=(select id from area where area_name='"+str(session['area'])+"')")
        return render_template("area_manager/add_trainer.html",crs=crs,std=std,sub=sub,syb=syb,data=res)
    else:
        return redirect('/')

@app.route('/add_trainerAM',methods=['POST'])
def add_trainerAM():
    if session.get('login'):
        name=request.form['name']
        gender=request.form['gender']
        standard=request.form['standard']
        syllabus=request.form['syllabus']
        subjects=request.form['subjects']
        branch=request.form['branch']
        join_date=request.form['join_date']
        street=request.form['street']
        city=request.form['city']
        po=request.form['po']
        pin=request.form['pin']
        email=request.form['email']
        mobile=request.form['mobile']
        address=request.form['address']
        photo=request.files['photo']
        salary=request.form['salary']
        remark=request.form['remark']
        password=request.form['repassword']
        area = session['area']
        ob = Db()
        data=ob.selectOne("select country,state,district from area_manager where l_id='"+str(session['login'])+"'")
        country =data['country']
        state = data['state']
        dist =data['district']

        import time
        fname=time.strftime("%Y%m%d_%H%M%S")+".jpg"
        photo.save(r"/home/SPS/tuition/static/trainers_photos/"+fname)

        ob=Db()
        q="insert into login values(null,'" + name + "','" + email + "','" + password + "','trainer','ofline','pending','"+str(session['name'])+"')"
        id=ob.insert(q)
        q = "insert into trainers values(null,'"+str(id)+"','"+name+"','"+gender+"','"+syllabus+"','"+standard+"','"+subjects+"','"+area+"','"+branch+"','"+pin+"','"+email+"','"+mobile+"','"+fname+"','"+salary+"','active','"+join_date+"')"
        result=ob.insert(q)
        q = "insert into address values(null,'"+str(id)+"','"+street+"','"+city+"','"+po+"','"+pin+"','"+dist+"','"+state+"','"+country+"','"+address+"','"+remark+"','trainer')"
        ad=ob.insert(q)
        q = "insert into staff_salary values(null,'"+str(id)+"','trainer','"+salary+"','pending')"
        ob.insert(q)
        if result or ad :
            return '''  <script>  alert('Added Successfully');window.location='/viewtrainerAM'</script> '''
        else:
            return '''  <script>  alert('Error!!!');window.history.back()</script> '''
    else:
        return redirect('/')

@app.route('/updatetrainerAM')
def updatetrainerAM():
    if session.get('login'):
        lid = request.args.get('lid')
        q="select * from trainers,address where trainers.l_id=address.l_id AND trainers.l_id='"+str(lid)+"'"
        ob = Db()
        res=ob.selectOne(q)
        ob = Db()
        q = "SELECT * FROM course WHERE status='active'"
        crs = ob.select(q)
        ob = Db()
        q = "SELECT * FROM standard WHERE status='active'"
        std = ob.select(q)
        ob = Db()
        q = "SELECT * FROM subjects WHERE subjects.status='active'"
        sub = ob.select(q)
        ob = Db()
        q = "SELECT * FROM syllabus WHERE status='active'"
        syb = ob.select(q)
        ob = Db()
        res2 = ob.select("select * from branch where status='active' and area_id=(select id from area where area_name='"+str(session['area'])+"')")
        return render_template("area_manager/edit_trainer.html",data=res,crs=crs,std=std,sub=sub,syb=syb,res=res2)
    else:
        return redirect('/')

@app.route('/update_trainerAM/<a>',methods=['POST'])
def update_trainerAM(a):
    if session.get('login'):
        name=request.form['name']
        gender=request.form['gender']
        standard=request.form['standard']
        syllabus=request.form['syllabus']
        subjects=request.form['subjects']
        branch=request.form['branch']
        join_date=request.form['join_date']
        street=request.form['street']
        city=request.form['city']
        po=request.form['po']
        pin=request.form['pin']
        email=request.form['email']
        mobile=request.form['mobile']
        address=request.form['address']
        photo=request.files['photo']
        salary=request.form['salary']
        remark=request.form['remark']

        import time
        if request.files is not None:
            if photo.filename!="":
                fname = time.strftime("%Y%m%d_%H%M%S")+".jpg"
                photo.save(r"/home/SPS/tuition/static/trainers_photos/"+fname)
                q="update trainers set name='"+name+"',gender='"+gender+"',p_standard='"+standard+"',syllabus='"+syllabus+"',p_subject='"+subjects+"',pin='"+pin+"',email='"+email+"',mobile='"+mobile+"',photo='"+fname+"',branch='"+branch+"',salary='"+salary+"',join_date='"+join_date+"' where l_id='"+str(a)+"'"
                ob=Db()
                result=ob.update(q)
            else:
                q = "update trainers set name='"+name+"',gender='"+gender+"',p_standard='"+standard+"',syllabus='"+syllabus+"',p_subject='"+subjects+"',pin='"+pin+"',email='"+email+"',mobile='"+mobile+"',branch='"+branch+"',salary='"+salary+"',join_date='"+join_date+"' where l_id='" + str(a) + "'"
                ob = Db()
                result=ob.update(q)
        else:
            q = "update trainers set name='"+name+"',gender='"+gender+"',p_standard='"+standard+"',syllabus='"+syllabus+"',p_subject='"+subjects+"',pin='"+pin+"',email='"+email+"',mobile='"+mobile+"',branch='"+branch+"',salary='"+salary+"',join_date='"+join_date+"' where l_id='" + str(a) + "'"
            ob = Db()
            result=ob.update(q)
        q = "update login set name='"+name+"',email='"+email+"' where id='" + str(a) + "'"
        ob = Db()
        ob.update(q)
        q = "update address set street='"+street+"',city='"+city+"',po='"+po+"',pin='"+pin+"',address='"+address+"',remark='"+remark+"' where l_id='" + str(a) + "'"
        ob = Db()
        ad=ob.update(q)
        if result or ad :
            return '''  <script>  alert('Updated');window.location='/viewtrainerAM'</script> '''
        else:
            return '''  <script>  alert('No Changes');window.history.back()</script> '''
    else:
        return redirect('/')

@app.route('/delete_trainerAM')
def delete_trainerAM():
    if session.get('login'):
        lid = request.args.get('lid')
        ob = Db()
        ob.update("update trainers set status='inactive'  where l_id='"+str(lid)+"'")
        ob = Db()
        ob.update("update login set status='inactive'  where id='"+str(lid)+"'")
        return '''<script>alert("Deleted");window.location='/viewtrainerAM';</script>'''
    else:
        return redirect('/')

@app.route('/viewbranchAM')
def viewbranchAM():
    if session.get('login'):
        ob = Db()
        q = "SELECT * FROM branch WHERE area_id=(SELECT id FROM area WHERE area_name='"+str(session['area'])+"')"
        branch = ob.select(q)
        return render_template("area_manager/view_branch.html",val=branch)
    else:
        return redirect('/')


@app.route('/addbranchAM')
def addbranchAM():
    if session.get('login'):
        return render_template("area_manager/AddBranch.html")
    else:
        return redirect('/')

@app.route('/addbranchactionAM',methods=["post"])
def addbranchactionAM():
    if session.get('login'):
        name = request.form['name']
        address = request.form['address']
        ob = Db()
        area =ob.selectOne("SELECT id FROM area WHERE area_name='"+str(session['area'])+"'")
        data=ob.selectOne("select country,state,district from area_manager where l_id='"+str(session['login'])+"'")
        country =data['country']
        state = data['state']
        district =data['district']
        q = "insert into branch values(null,'" + area + "','" + name + "','" + country + "','" + state + "','" + district + "','" + address + "','"+str(session['name'])+"','active')"
        result = ob.insert(q)
        if result:
            return '''  <script>  alert('Added Successfully');window.location='/viewbranchAM'</script> '''
        else:
            return '''  <script>  alert('Error!!!');window.history.back()</script> '''
    else:
        return redirect('/')


@app.route('/editbranchAM')
def editbranchAM():
    if session.get('login'):
        id = request.args.get('id')
        q="select * from branch where id='"+str(id)+"'"
        ob = Db()
        res=ob.selectOne(q)
        return render_template("area_manager/edit_branch.html",val=res)
    else:
        return redirect('/')

@app.route('/updatebranchAM/<a>',methods=["post"])
def updatebranchAM(a):
    if session.get('login'):
        name = request.form['name']
        address = request.form['address']
        ob = Db()
        q = "update branch set branch_name='" + name + "',address='" + address + "' where id='"+str(a)+"'"
        result = ob.update(q)
        if result:
            return '''  <script>  alert('Updated');window.location='/viewbranchAM'</script> '''
        else:
            return '''  <script>  alert('No changes');window.history.back()</script> '''
    else:
        return redirect('/')

@app.route('/activate_branchAM')
def activate_branchAM():
    if session.get('login'):
        id = request.args.get('id')
        ob = Db()
        ob.update("update branch set status='active'  where id='"+str(id)+"'")
        return '''<script>alert("Activated");window.location='/viewbranchAM';</script>'''
    else:
        return redirect('/')

@app.route('/deactivate_branchAM')
def deactivate_branchAM():
    if session.get('login'):
        id = request.args.get('id')
        ob = Db()
        ob.update("update branch set status='inactive'  where id='"+str(id)+"'")
        return '''<script>alert("Deactivated");window.location='/viewbranchAM';</script>'''
    else:
        return redirect('/')

@app.route('/notificationareaAM')
def notificationareaAM():
    if session.get('login'):
        ob = Db()
        noti = ob.select("SELECT notification.*,login.name FROM notification LEFT JOIN login ON login.id=notification._from WHERE  notification.status='unread' AND  notification._to='"+str(session['area'])+"' OR notification.type='general'")
        if len(noti) == 0:
            result='''<li class="nav-item dropdown mr-3"><a href="/viewnotificationAM" id="notifications" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false" class="nav-link dropdown-toggle text-gray-400 px-1"><i class="fa fa-bell"></i></a>
            <div aria-labelledby="notifications" class="dropdown-menu">
                <a href="/viewnotificationAM" class="dropdown-item">
                    <div class="d-flex align-items-center">
                      <div class="icon icon-sm bg-violet text-white"><i class="fas fa-bell"></i></div>
                      <div class="text ml-2">
                        <p class="mb-0">No New Notification</p>
                      </div>
                    </div></a>
              <div class="dropdown-divider"></div><a href="/viewnotificationAM" class="dropdown-item text-center"><small class="font-weight-bold headings-font-family text-uppercase">View all notifications</small></a>
            </div>
          </li>'''
        else:
            for noti in noti:
                  result='''<li class="nav-item dropdown mr-3"><a href="/viewnotificationAM" id="notifications" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false" class="nav-link dropdown-toggle text-gray-400 px-1"><i class="fa fa-bell"></i><span class="notification-icon"></span></a>
                <div aria-labelledby="notifications" class="dropdown-menu">
                  <a href="/viewnotificationAM" class="dropdown-item">
                    <div class="d-flex align-items-center">
                      <div class="icon icon-sm bg-violet text-white"><i class="fas fa-envelope"></i></div>
                      <div class="text ml-2">
                        <p class="mb-0">'''+noti['notification']+'''</p>
                      </div>
                    </div></a>
                  <div class="dropdown-divider"></div><a href="/viewnotificationAM" class="dropdown-item text-center"><small class="font-weight-bold headings-font-family text-uppercase">View all notifications</small></a>
                </div>
              </li>'''
        resp = make_response(json.dumps(result))
        resp.status_code = 200
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp
    else:
        return redirect('/')


@app.route('/viewnotificationAM')
def viewnotificationAM():
    if session.get('login'):
        ob = Db()
        noti = ob.select("SELECT notification.*,login.name FROM notification LEFT JOIN login ON login.id=notification._from WHERE _to='"+str(session['area'])+"' OR notification.type='general'")
        return render_template("area_manager/view_notification.html",noti=noti)
    else:
        return redirect('/')

@app.route('/makeasreadAM')
def makeasreadAM():
    if session.get('login'):
        id = request.args.get('id')
        ob = Db()
        ob.update("update notification set status='read'  where n_id='"+str(id)+"'")
        return '''<script>window.location='/viewnotificationAM';</script>'''
    else:
        return redirect('/')

@app.route('/makeasunreadAM')
def makeasunreadAM():
    if session.get('login'):
        id = request.args.get('id')
        ob = Db()
        ob.update("update notification set status='unread'  where n_id='"+str(id)+"'")
        return '''<script>window.location='/viewnotificationAM';</script>'''
    else:
        return redirect('/')


@app.route('/downloadsAM')
def downloadsAM():
    if session.get('login'):
        ob = Db()
        q = "SELECT * from downloads where status='publish'"
        downloads = ob.select(q)
        return render_template("area_manager/view_downloads.html",downloads=downloads)
    else:
        return redirect('/')


















#                               Branch manager
#-----------------------------------------------------------------------------####____________###
@app.route('/viewprofileBM')
def viewprofileBM():
    if session.get('login'):
        ob=Db()
        branch_manager=ob.selectOne("SELECT * FROM branch_manager WHERE l_id='"+str(session['login'])+"'")
        return render_template("branch_manager/view_profile.html",branch_manager=branch_manager)
    else:
        return redirect('/')


@app.route('/branch_managerhome')
def branch_managerhome():
    if session.get('login'):
        ob=Db();
        trainers=ob.selectOne("SELECT COUNT(TYPE)AS trainers FROM login,trainers WHERE login.TYPE='trainer' and login.id=trainers.l_id and trainers.branch='"+str(session['branch'])+"'")
        students=ob.selectOne("SELECT COUNT(TYPE)AS students FROM login,students WHERE login.TYPE='student' and login.id=students.l_id and students.branch='"+str(session['branch'])+"'")
        notice=ob.select("select * from notice where status='publish'")
        event=ob.select("select * from event where status='publish'")
        return render_template("branch_manager/home.html",trainers=trainers,students=students,notice=notice,event=event)
    else:
        return redirect('/')


@app.route('/viewstudentBM')
def viewstudentBM():
    if session.get('login'):
        ob = Db()
        q = "SELECT * FROM students where status!='inactive' and branch ='" + str(session['branch']) + "' "
        print(q)
        stdts = ob.select(q)
        return render_template("branch_manager/viewstudents.html",val=stdts)
    else:
        return redirect('/')


@app.route('/aisgn_subjectBM')
def aisgn_subjectBM():
    if session.get('login'):
        lid = request.args.get('lid')
        ob=Db()
        sd = ob.selectOne("select * from students where l_id = '" + str(lid) +"'")
        q = "SELECT * FROM subjects WHERE subjects.status='active'"
        sub = ob.select(q)
        schedule=ob.select("select schedules.*,trainers.name,student_schedule.id as ss_id from schedules,trainers,student_schedule where schedules.trainer_id=trainers.l_id and student_schedule.schedule_id=schedules.id and student_schedule.s_id='" + str(lid) +"' and student_schedule.status='active'")
        ln=0
        if len(schedule) == 0:
            ln = 1
        return render_template("branch_manager/aisgn_subject.html",sd=sd,sub=sub,schedule=schedule,ln=ln)
    else:
        return redirect('/')

@app.route('/deletestudenscheduleBM',methods=['post'])
def deletestudenscheduleBM():
    if session.get('login'):
        id = request.args.get('sid')
        print(id)
        ob = Db()
        ob.delete("delete from student_schedule where id='"+str(id)+"'")
        return '''<script>window.location.reload();</script>'''
    else:
        return redirect('/')

@app.route('/scheduleselectBM',methods=['post'])
def scheduleselectBM():
    if session.get('login'):
        std = request.args.get('std')
        subject = request.args.get('subject')
        ob=Db()
        trainers_id=("select l_id from trainers where p_standard='"+std+"' and p_subject='"+subject+"' and branch='"+session['branch']+"'")
        trainer_id=ob.select(trainers_id)
        check =""
        for trainer_id in trainer_id:
            ch= "trainers.l_id='"+str(trainer_id['l_id'])+"' or "
            check=check+ch
        check=check[:-3]
        print(check)
        if trainer_id:
            trainers =ob.select("select trainers.name,schedules.* from trainers LEFT JOIN schedules ON schedules.trainer_id=trainers.l_id  where "+check+" and trainers.branch='"+session['branch']+"' and trainers.status!='inactive'")
            print(trainers)
        else:
            trainers=''
        if trainers:
            result=['<option value selected disabled>Schedule</option>']
            for trainers in trainers:
                s = datetime.strptime(str(trainers['start_time']), "%H:%M")
                start=s.strftime("%I:%M %p")
                e = datetime.strptime(str(trainers['end_time']), "%H:%M")
                end = e.strftime("%I:%M %p")
                resul = '''<option value=''' + str(trainers['id']) + '''>''' + trainers['name']+''' , days '''+trainers['days'].replace('"',' ') + ''' at '''+start + ''' to '''+ end + '''</option>'''
                result.append(resul)
        else:
            result = '''<option value >Not available</option>'''
        resp = make_response(json.dumps(result))
        resp.status_code = 200
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp
    else:
        return redirect('/')

@app.route('/student_scheduleasignBM', methods=["post"])
def student_scheduleasignBM():
    if session.get('login'):
        s_id = request.form['s_id']
        schedule = request.form['schedule']
        subject = request.form['subject']
        ob=Db()
        data=ob.selectOne("select * from student_schedule where s_id='" + str(s_id) + "' and schedule_id='" + str(schedule) + "' ")
        if data:
            return '''<script>alert('Already Exist');window.history.back();</script>'''
        else:
            q = "insert into student_schedule values(null,'" + str(s_id) + "','" + str(schedule) + "','" + subject + "',now(),'" + str(session['name']) + "','active')"
            result=ob.insert(q)
            if result:
                return '''<script>window.location.reload();</script>'''
            else:
                return '''<script>alert('Error!!');window.history.back();</script>'''
    else:
        return redirect('/')



@app.route('/create_scheduleBM')
def create_scheduleBM():
    if session.get('login'):
        ob=Db()
        sb = "select * from subjects"
        sb = ob.select(sb)
        return render_template("branch_manager/create_schedule.html",sub=sb)
    else:
        return redirect('/')

@app.route('/create_scheduleactionBM', methods=["post"])
def create_scheduleactionBM():
    if session.get('login'):
        ob = Db()
        day = request.form.getlist('day[]')
        print(day)
        days=''
        for i in day:
            j = i.replace(' ', '')
            days=days+'"'+j+'",'
        dayss=days[:-1]
        daysss='['+dayss+']'
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        subjects = request.form['subjects']
        trainers = request.form['trainers']

        data=ob.selectOne("select * from schedules where days='" + daysss + "' and start_time='" +start_time+ "' and end_time='" +end_time+ "' and subject='" +subjects+ "' and branch='" +session['branch']+ "' and add_by='" +str(session['name'])+ "' ")
        if data:
            return '''  <script>  alert('Already Exist');window.history.back()</script> '''
        else:
            q = "insert into schedules values(null,'" + daysss + "','" + start_time + "','" + end_time + "','" + subjects + "','" + trainers + "','" + session['branch']+ "','" + str(session['name']) + "','active')"
            print(q)
            ob.insert(q)
            return '''<script>alert('Created');window.location='/create_scheduleBM';</script>'''
    else:
        return redirect('/')


@app.route('/trainerselectBM',methods=['post'])
def trainerselectBM():
    if session.get('login'):
        day = request.args.get('days')
        da=day.replace('[','')
        days=da.replace(']','')
        print(days)
        start_time = request.args.get('starttime')
        end_time = request.args.get('endtime')
        subject = request.args.get('subject')
        ob=Db()
        trainers_id=("select trainer_id from schedules where days='"+days+"' and start_time  between '" +start_time+ "' and '" +end_time+ "' and end_time  between '" +start_time+ "' and '" +end_time+ "' or start_time='" +start_time+ "' or start_time='" +end_time+ "' or end_time='" +start_time+ "' or end_time='" +end_time+ "' and subject='"+subject+"' and branch='"+session['branch']+"'")
        print(trainers_id)
        trainer_id=ob.select(trainers_id)
        check =""
        for trainer_id in trainer_id:
            ch= "l_id!='"+trainer_id['trainer_id']+"' and "
            check=check+ch
        print(check)
        if trainer_id:
            print(trainer_id['trainer_id'])
            trainers =ob.select("select name,l_id,p_standard from trainers where "+check+" branch='"+session['branch']+"' and p_subject='"+subject+"' and status!='inactive'")
            print(trainers)
        else:
            trainers=ob.select("select name,l_id,p_standard from trainers where branch='"+session['branch']+"' and p_subject='"+subject+"' and status!='inactive' ")
        if trainers:
            result=['<option value="" selected disabled>Trainer</option>']
            for trainers in trainers:
                resul = '''<option value=''' + str(trainers['l_id']) + '''>''' + trainers['name']+''' - Std '''+trainers['p_standard'] + '''</option>'''
                result.append(resul)
        else:
            result = '''<option value="">Not available</option>'''
        resp = make_response(json.dumps(result))
        resp.status_code = 200
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp
    else:
        return redirect('/')

























@app.route('/viewtrainerBM')
def viewtrainerBM():
    if session.get('login'):
        ob = Db()
        branch = ob.selectOne("select branch_manager.branch from branch_manager where l_id='" + str(session['login']) + "'")

        q = "SELECT * FROM trainers where status!='inactive' and branch ='"+ branch['branch'] + "' "
        print(q)
        trainer = ob.select(q)
        return render_template("branch_manager/view_trainer.html",val=trainer)
    else:
        return redirect('/')

@app.route('/notificationareaBM')
def notificationareaBM():
    if session.get('login'):
        ob = Db()
        noti = ob.select("SELECT notification.*,login.name FROM notification LEFT JOIN login ON login.id=notification._from WHERE  notification.status='unread' AND  _to=(SELECT branch_manager.branch FROM branch_manager WHERE l_id='"+str(session['login'])+"') OR notification.type='general'")
        if len(noti) == 0:
            result='''<li class="nav-item dropdown mr-3"><a href="/viewnotificationBM" id="notifications" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false" class="nav-link dropdown-toggle text-gray-400 px-1"><i class="fa fa-bell"></i></a>
            <div aria-labelledby="notifications" class="dropdown-menu">
                <a href="/viewnotificationBM" class="dropdown-item">
                    <div class="d-flex align-items-center">
                      <div class="icon icon-sm bg-violet text-white"><i class="fas fa-bell"></i></div>
                      <div class="text ml-2">
                        <p class="mb-0">No New Notification</p>
                      </div>
                    </div></a>
              <div class="dropdown-divider"></div><a href="/viewnotificationBM" class="dropdown-item text-center"><small class="font-weight-bold headings-font-family text-uppercase">View all notifications</small></a>
            </div>
          </li>'''
        else:
            for noti in noti:
                  result='''<li class="nav-item dropdown mr-3"><a href="/viewnotificationAM" id="notifications" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false" class="nav-link dropdown-toggle text-gray-400 px-1"><i class="fa fa-bell"></i><span class="notification-icon"></span></a>
                <div aria-labelledby="notifications" class="dropdown-menu">
                  <a href="/viewnotificationBM" class="dropdown-item">
                    <div class="d-flex align-items-center">
                      <div class="icon icon-sm bg-violet text-white"><i class="fas fa-envelope"></i></div>
                      <div class="text ml-2">
                        <p class="mb-0">'''+noti['notification']+'''</p>
                      </div>
                    </div></a>
                  <div class="dropdown-divider"></div><a href="/viewnotificationBM" class="dropdown-item text-center"><small class="font-weight-bold headings-font-family text-uppercase">View all notifications</small></a>
                </div>
              </li>'''
        resp = make_response(json.dumps(result))
        resp.status_code = 200
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp
    else:
        return redirect('/')


@app.route('/viewnotificationBM')
def viewnotificationBM():
    if session.get('login'):
        ob = Db()
        noti = ob.select("SELECT notification.*,login.name FROM notification LEFT JOIN login ON login.id=notification._from WHERE _to=(SELECT branch_manager.branch FROM branch_manager WHERE l_id='"+str(session['login'])+"') OR notification.type='general'")
        return render_template("branch_manager/view_notification.html",noti=noti)
    else:
        return redirect('/')

@app.route('/makeasreadBM')
def makeasreadBM():
    if session.get('login'):
        id = request.args.get('id')
        ob = Db()
        ob.update("update notification set status='read'  where n_id='"+str(id)+"'")
        return '''<script>window.location='/viewnotificationBM';</script>'''
    else:
        return redirect('/')

@app.route('/makeasunreadBM')
def makeasunreadBM():
    if session.get('login'):
        id = request.args.get('id')
        ob = Db()
        ob.update("update notification set status='unread'  where n_id='"+str(id)+"'")
        return '''<script>window.location='/viewnotificationBM';</script>'''
    else:
        return redirect('/')

@app.route('/viewscheduleBM')
def viewschedulBM():
    if session.get('login'):
        today=datetime.today().strftime('%A')
        ob=Db()
        sdl=ob.select("SELECT schedules.*,trainers.name,COUNT(student_schedule.id)AS students FROM trainers,schedules LEFT JOIN student_schedule ON student_schedule.schedule_id=schedules.id WHERE schedules.trainer_id=trainers.l_id AND schedules.branch='Manikkadavue' GROUP BY schedules.id ")
        print(sdl)
        if sdl:
            sdll=sdl
        else:
            sdll=''
        return render_template("branch_manager/view_schedule.html",sdll=sdll)
    else:
        return redirect('/')

@app.route('/viewtodaysscheduleBM')
def viewtodaysscheduleBM():
    if session.get('login'):
        today=datetime.today().strftime('%A')
        ob=Db()
        sd=("SELECT schedules.*,trainers.name,trainers.l_id,COUNT(student_schedule.id)AS students,attendance_tr.attendance,attendance_tr.status as class,attendance_tr.hours FROM trainers,(schedules LEFT JOIN student_schedule ON student_schedule.schedule_id=schedules.id) LEFT JOIN attendance_tr ON attendance_tr.l_id=schedules.trainer_id AND attendance_tr.date=CURDATE() AND attendance_tr.schedule_id=schedules.id  WHERE schedules.trainer_id=trainers.l_id AND schedules.branch='"+str(session['branch'])+"' AND days LIKE '%"+today+"%' GROUP BY schedules.id")
        sdl=ob.select(sd)
        print(sd)
        if sdl:
            sdll=sdl
        else:
            sdll=''
        return render_template("branch_manager/today's_schedule.html",sdll=sdll,today=today)
    else:
        return redirect('/')

@app.route('/absent_tr')
def absent_tr():
    if session.get('login'):
        lid = request.args.get('lid')
        sid = request.args.get('sid')
        ob = Db()
        ob.insert("insert into attendance_tr values(null,'"+str(lid)+"','"+str(sid)+"',curdate(),'Absent',null,null,null,null,'Not Conducted')")
        return '''<script>window.location='/viewtodaysscheduleBM';</script>'''
    else:
        return redirect('/')

@app.route('/downloadsBM')
def downloadsBM():
    if session.get('login'):
        ob = Db()
        q = "SELECT * from downloads where status='publish'"
        downloads = ob.select(q)
        return render_template("branch_manager/view_downloads.html",downloads=downloads)
    else:
        return redirect('/')















if __name__ == '__main__':
    app.run(debug=True)
