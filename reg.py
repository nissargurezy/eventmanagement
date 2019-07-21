from flask import Flask,render_template,request,redirect,url_for,flash
from dbconnect import connection
from string import digits,ascii_uppercase,ascii_lowercase
import random
import string


def register_in():
    try:
        name=request.form['name']
        dob=request.form['dob']
        phone=request.form['phone']
        email=request.form['email']
        address=request.form['address']
        password=request.form['password']
        type_event=request.form['event']
        budget=request.form['budget']
        date=request.form['date']
        place=request.form['place']
        amin=request.form.getlist("users")
        amenities = ','.join(amin)
        c,conn=connection()
        c.execute("SELECT * FROM register WHERE email=%s",[email])
        data=c.fetchone()
        if data==None:
            c.execute("INSERT INTO register(name,dob,phone,email,address,password,type_event,budget,date,place,amenities,status) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",[name,dob,phone,email,address,password,type_event,budget,date,place,amenities,'none'])
            conn.commit()
            flash(f'Registerred Succesfully!','success')
        else:
            flash(f'Email Already Exists!','danger')
    except Exception as exception:
        flash(f'Error Try Again!','danger')
