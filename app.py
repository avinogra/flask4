from flask import Flask, render_template
import flask
import json
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, RadioField
from flask_wtf.csrf import CSRFProtect
from wtforms.validators import DataRequired, email_validator,Required
import random
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import os
from sqlalchemy.dialects.postgresql import JSON

app = Flask(__name__)
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SECRET_KEY'] = "secretkey"
app.config['WTF_CSRF_SECRET_KEY'] = "secretkey"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")



db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Teacher(db.Model):
    #Таблица
    __tablename__ = 'teachers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    about = db.Column(db.Text(), unique=True, nullable=False)
    rating = db.Column(db.Float)
    picture = db.Column(db.String(100), unique=True)
    price = db.Column(db.Integer, nullable=False)
    free = db.Column(JSON)
    goals = db.Column(db.String(100), nullable=False)


class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    day_of_week = db.Column(db.String(10), nullable=False)
    time_str = db.Column(db.String(10), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    teacher = db.relationship("Teacher")
    teacher_id = db.Column(db.Integer, db.ForeignKey("teachers.id"))



class Request(db.Model):
    #Таблица
    __tablename__ = 'requests'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    time_for_study = db.Column(db.String(200), nullable=False)
    goal = db.Column(db.String(100), nullable=False)


goals = {"travel": "Для путешествий", "study": "Для учебы", "work": "Для работы", "relocate": "Для переезда"}
times={ "12":"1-2 часа в неделю","35":"3-5 часов в неделю","57":"5-7 часов в неделю","710":"7-10 часов в неделю"}
week={"mon":"Понедельник","tue":"Вторник","wed":"Среда","thu":"Четверг","fri":"Пятница","sat":"Суббота","sun":"Воскресенье"}


class RequestForm(FlaskForm):
    time_list=[ (key,value) for key,value in times.items()]
    choices_list= [(key,value)  for key,value in goals.items()]
    name = StringField('Вас зовут', validators=[DataRequired()])
    phone = StringField('Ваш телефон',validators=[DataRequired()])
    goal=RadioField('Какая цель занятий?', choices=choices_list, default=choices_list[0][0])
    time=RadioField('Сколько времени есть?', choices= time_list, default=time_list[0][0])
    submit = SubmitField('Найдите мне преподавателя')

class RequestBooking(FlaskForm):
    clientWeekday=StringField(validators=[DataRequired()])
    clientTime=StringField(validators=[DataRequired()])
    clientTeacher=StringField(validators=[DataRequired()])
    clientName = StringField('Вас зовут', validators=[DataRequired()])
    clientPhone = StringField('Ваш телефон',validators=[DataRequired()])
    submit = SubmitField('Записаться на пробный урок')



@app.route('/')
def main():
    teachers=db.session.query(Teacher).order_by(db.func.random()).limit(6) 

    print(teachers) 
    #.order_by(db.func.random()).limit(6)    
    return render_template('index.html',teachers=teachers, goals=goals,)


@app.route('/request/')
def render_myform():
    form = RequestForm()
    return render_template('request.html', form=form)

@app.route('/request_done/', methods=['POST'])
def render_request_done():
    goal=goals[flask.request.form.get('goal')]
    time=times[flask.request.form.get('time')]
    name=flask.request.form.get('name')
    phone=flask.request.form.get('phone')
    new_request = Request(
            name=name,
            phone=phone,
            time_for_study=time,
            goal=goal)
    db.session.add(new_request)
    db.session.commit()
    return render_template('request_done.html', name=name,goal=goal,time=time, phone=phone)


@app.route('/goal/<id>/')
def render_goal(id):
    teachers=db.session.query(Teacher).filter(Teacher.goals.contains(id)).order_by(Teacher.price.desc())        
    return render_template('goal.html',teachers=teachers,goal=goals[id])

 
@app.route('/profile/<int:id>/')
def render_profile(id):
    teacher = db.session.query(Teacher).get_or_404(id)
    return render_template('profile.html',teacher=teacher,id=id,list_goals=teacher.goals)

@app.route('/booking/<int:id>/<day>/<time>/')
def render_booking(id,day,time):
    form=RequestBooking()
    teacher= db.session.query(Teacher).get_or_404(id)
    t=week[day]+" "+time[:-2]+":"+time[2:]
    return render_template('booking.html',teacher=teacher,timestring=t,form=form,id=id,day=day,time=time[:-2]+":"+time[2:])    

@app.route('/booking_done/', methods=['POST'])
def render_booking_done():
    time=flask.request.form.get('timestring')
    new_booking = Booking(
    day_of_week=flask.request.form.get('clientWeekday'),
    time_str=flask.request.form.get('clientTime'),
    name=flask.request.form.get('clientName'),
    phone=flask.request.form.get('clientPhone'),
    teacher_id=flask.request.form.get('clientTeacher'))
    db.session.add(new_booking)
    db.session.commit()
    print(flask.request.form.get('timestring'))
    return render_template('booking_done.html', name=flask.request.form.get('clientName'),time=flask.request.form.get('timestring'), phone=flask.request.form.get('clientPhone'))

# app.run(debug=True)
if __name__ == '__main__':
    app.run()
