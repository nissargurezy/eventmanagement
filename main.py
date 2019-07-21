from flask import Flask,render_template,request,redirect,url_for,session,flash
from dbconnect import connection
from reg import register_in
from werkzeug.utils import secure_filename
import os
import smtplib
from email.message import EmailMessage
from forms import log
import random, json
UPLOAD_FOLDER='static/images'
app=Flask(__name__)
EMAIL_ADDRESS=os.environ.get('EMAIL_ADDRESS')
EMAIL_PASSWORD=os.environ.get('EMAIL_PASSWORD')
app.config['SECRET_KEY']='672d71e37b0b8864c3fa5613c6891802'
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER

@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")
@app.route("/register",methods=['Get','POST'])
def register():
    if request.method=='POST':
        register_in()
        return redirect(url_for('register'))
    return render_template("register.html")

@app.route("/gallery_images")
def gallery_images():
    c,conn=connection()
    c.execute("SELECT * FROM gallery")
    results=c.fetchall()
    return render_template("gallery.html",results=results)
@app.route("/contact_us",methods=['GET','POST'])
def contact_us():
    if request.method=='POST':
        email=request.form['email']
        subject=request.form['subject']
        message=request.form['message']
        c,conn=connection()
        c.execute("INSERT INTO contact_us(email,message,subject) VALUES(%s,%s,%s)",[email,message,subject])
        conn.commit()
        c.close()
    return render_template("contact_us.html")
@app.route("/login",methods=['GET','POST'])
def login():
    c,conn=connection()
    c.execute("SELECT * FROM admin")
    data=c.fetchall()
    if request.method=='POST':
        session.pop('admin',None)
        for i in data:
            if i[0]==request.form['email'] and i[1]==request.form['password']:
                session['admin']=request.form['email']
                return redirect(url_for('dashboard_admin'))
        flash(f'Wrong Email or Password!','danger')
        return redirect(url_for('login'))
    return render_template("login.html")

@app.route("/dashboard_admin")
def dashboard_admin():
    if session.get('admin'):
        c,conn=connection()
        c.execute("SELECT * FROM fixappointment as f,register as r WHERE f.id=r.reg_id and r.status='accepted'")
        data=c.fetchall()
        c.execute("SELECT * FROM fixappointment as f,register as r WHERE f.id=r.reg_id and r.status='processed'")
        result=c.fetchall()
        c.execute("SELECT * FROM register WHERE status='completed'")
        history=c.fetchall()
        return render_template("dashboardadmin.html",data=data,result=result,history=history)
    return redirect(url_for('login'))

@app.route("/statusto_completed")
def statusto_completed():
    if session.get('admin'):
        reg_id=request.args.get('reg_id')
        c,conn=connection()
        c.execute("UPDATE register SET status='completed' WHERE reg_id=%s",[reg_id])
        conn.commit()
        return redirect(url_for('dashboard_admin'))
    return redirect(url_for('login'))

@app.route("/statusto_processed")
def statusto_processed():
    if session.get('admin'):
        reg_id=request.args.get('reg_id')
        c,conn=connection()
        c.execute("UPDATE register SET status='processed' WHERE reg_id=%s",[reg_id])
        conn.commit()
        return redirect(url_for('dashboard_admin'))
    return redirect(url_for('login'))

@app.route("/customers_list")
def customers_list():
    if session.get('admin'):
        c,conn=connection()
        c.execute("SELECT * FROM register WHERE status='none'")
        data=c.fetchall()
        c.close()
        return render_template("customer_list.html",data=data)
    return redirect(url_for('login'))

@app.route("/fix_appointment",methods=['GET','POST'])
def fix_appointment():
    if session.get('admin'):
        id=request.args.get('id')
        name=request.args.get('name')
        email=request.args.get('email')
        c,conn=connection()
        c.execute("SELECT * FROM register WHERE reg_id=%s",[id])
        data=c.fetchall()
        if request.method=='POST':
            date=request.form['date']
            time=request.form['time']
            message=request.form['message']
            c.execute("INSERT INTO fixappointment(id,name,email,date,message,time) VALUES(%s,%s,%s,%s,%s,%s)",[id,name,email,date,message,time])
            conn.commit()
            c.execute("UPDATE register SET status='accepted' WHERE reg_id=%s",[id])
            conn.commit()
            msg=EmailMessage()
            msg['subject']='Thanks for registering with us'
            msg['From']=EMAIL_ADDRESS
            msg['To']=email
            msg.add_alternative("""\
            <!DOCTYPE html>
            <html>
            <body>
            <h4 style="color:dodgerblue;">Dear Customer, Your Appointment Has Been On:</h4>
            <h3 style="color:teal;"> Date:"""+date+"""</h3>
            <h3 style="color:teal;">Time:"""+time+"""</h3>
            <h3 style="color:SlateGray;">"""+message+"""</h3>
            <p style="font-style:italic;color:red;">Note: For Any Changes On The Above Details,Please Call 7006263419</p>
            </body>
            </html>
            """,subtype='html')
            #msg.set_content(message+"\n"+date+"\n"+time)
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(EMAIL_ADDRESS,EMAIL_PASSWORD)
                smtp.send_message(msg)
            flash(f'Accepted Succesfully!','success')
            return redirect(url_for('customers_list'))
        return render_template("fix_appointment.html",data=data)
    return redirect(url_for('login'))

@app.route("/upload_images",methods=['GET','POST'])
def upload_images():
    if session.get('admin'):
        if request.method=='POST':
            caption=request.form['caption']
            file=request.files['file_source']
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
            c,conn=connection()
            c.execute("INSERT INTO gallery(images,caption) VALUES(%s,%s)",[filename,caption])
            conn.commit()
            c.close()
            flash(f'Image uploaded Succesfully!','success')
            return redirect(url_for('upload_images'))
        return render_template("upload_image.html")
    return redirect(url_for('login'))
@app.route("/delete_image",methods=['GET','POST'])
def delete_image():
    if session.get('admin'):
        c,conn=connection()
        c.execute("SELECT * FROM gallery")
        data=c.fetchall()
        if request.method=='POST':
            delete_image=request.form['image']
            c.execute("DELETE FROM gallery WHERE caption=%s",[delete_image])
            conn.commit()
            flash(f'Deleted Succesfully!','success')
            return redirect(url_for('delete_image'))
        return render_template("delete_image.html",data=data)
    return redirect(url_for('login'))
@app.route("/contactus_details")
def contactus_details():
    if session.get('admin'):
        c,conn=connection()
        c.execute("SELECT * FROM contact_us")
        data=c.fetchall()
        c.execute("SELECT * FROM register WHERE status='completed'")
        fback=c.fetchall()
        return render_template("contactus_details.html",data=data,fback=fback)
    return redirect(url_for('login'))

@app.route("/accepted_list")
def accepted_list():
    if session.get('admin'):
        #c,conn=connection()
        #c.execute("SELECT * FROM fixappointment as f,register as r WHERE f.id=r.reg_id and r.email=%s",[name])
        return render_template("accepted_list.html")
    return redirect(url_for('login'))

@app.route("/delete")
def delete():
    id=request.args.get('id')
    c,conn=connection()
    c.execute("DELETE FROM register WHERE reg_id=%s",[id])
    conn.commit()
    return redirect(url_for('customers_list'))

@app.route("/dropsession_admin")
def dropsession_admin():
    session.pop('admin',None)
    return redirect(url_for('login'))

@app.route("/user_login",methods=['GET','POST'])
def user_login():
    c,conn=connection()
    c.execute("SELECT * FROM register")
    data=c.fetchall()
    if request.method=='POST':
        session.pop('admin',None)
        email=request.form['email']
        password=request.form['password']
        for i in data:
            if i[4]==email and i[6]==password:
                session['user']=request.form['email']
                return redirect(url_for('user_dashboard'))
        flash(f'Wrong Email or Password!','danger')
        return redirect(url_for('user_login'))
    return render_template("user_login.html")
@app.route("/user_dashboard")
def user_dashboard():
    if session.get('user'):
        email=session.get('user')
        c,conn=connection()
        c.execute("SELECT * FROM fixappointment as f,register as r WHERE f.id=r.reg_id and r.email=%s",[email])
        data=c.fetchall()
        c.execute("SELECT * FROM register WHERE email=%s",[email])
        result=c.fetchall()
        return render_template("user_dashboard.html",data=data,result=result)
    return redirect(url_for('user_login'))

@app.route("/feedback",methods=['Get','POST'])
def feedback():
    if session.get('user'):
        email=session.get('user')
        reg_id=request.args.get('use')
        print(reg_id)
        c,conn=connection()
        c.execute("SELECT * FROM register WHERE email=%s",[email])
        user1=c.fetchall()
        if request.method=='POST':
            try:
                user_feed=request.form['user_feed']
                c.execute("UPDATE register SET user_feed=%s WHERE reg_id=%s",[user_feed,reg_id])
                conn.commit()
                flash(f'Thanks for your feedback!','success')
                return redirect(url_for('user_dashboard'))

            except Exception as e:
                print(e)
        return render_template("feedback.html",user1=user1)
    return redirect(url_for('user_login'))

@app.route("/dropsession_user")
def dropsession_user():
    session.pop('user',None)
    return redirect(url_for('user_login'))
@app.route("/check")
def check():
    form=log()
    return render_template("check.html",form=form)

if (__name__)=='__main__':
    app.run(debug=True)
