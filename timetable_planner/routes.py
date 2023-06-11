from flask import Blueprint,redirect,render_template,url_for,current_app,flash,session,abort
from timetable_planner.models import User,Timetable,Subject
from timetable_planner.forms import LoginForm,RegisterForm,AddSubject,AddTimetable
from passlib.hash import pbkdf2_sha256
from dataclasses import asdict
import uuid
import functools
import datetime

pages=Blueprint("pages",__name__,template_folder="template",static_folder="static")

def login_required(route):
    @functools.wraps(route)
    def route_wrapper(*args,**kwargs):
        if session.get("email") is None:
            return redirect(url_for(".login"))
        return route(*args,**kwargs)
    return route_wrapper


@pages.route("/",methods=["GET","POST"])
@login_required
def index():
    user_data=current_app.db.user.find_one({"_id":session.get("_id")})
    user=User(**user_data)
    timetable_data=[current_app.db.timetable.find_one({"_id":_id}) for _id in user.timetables][::-1]
    timetables=[Timetable(**timetable) for timetable in timetable_data]
    form=AddTimetable()
    if form.validate_on_submit():
        timetable=Timetable(
            _id=uuid.uuid4().hex,
            name=(form.name.data).capitalize()
        )
        current_app.db.timetable.insert_one(asdict(timetable))
        current_app.db.user.update_one({"_id":session["_id"]},{"$push":{"timetables":timetable._id}})
        return redirect(url_for(".index"))

    return render_template("index.html",title="Timetable Planner",timetable_data=timetables,form=form)

@pages.route("/login",methods=["GET","POST"])
def login():
    if session.get("email"):
        return redirect(url_for(".index"))
    form=LoginForm()
    if form.validate_on_submit():
        user_data=current_app.db.user.find_one({"email":form.email.data})
        if not user_data:
            flash("Login credentials not correct",category="danger")
            return redirect(url_for(".login"))
        user=User(**user_data)

        if user and pbkdf2_sha256.verify(form.password.data,user.password):
            session["_id"]=user._id
            session["email"]=user.email
            return redirect(url_for(".index"))
        flash("Login credentials not correct",category="danger")    
    return render_template("login.html",title="Timetable Planner - Login",form=form)

@pages.route("/register",methods=["GET","POST"])
def register():
    if session.get("email"):
        return redirect(url_for(".index"))
    
    form=RegisterForm()
    if form.validate_on_submit():
        if current_app.db.user.find_one({"email":form.email.data}):
            flash("Account already exist with this email","danger")
            print("not allowed")
            return redirect(url_for(".register"))
        user=User(
            _id=uuid.uuid4().hex,
            email=form.email.data,
            password=pbkdf2_sha256.hash(form.password.data)
        )
        current_app.db.user.insert_one(asdict(user))
        flash("User Registered Succesfully","success")
        return redirect(url_for(".index"))
    return render_template("register.html",title="Timetable Planner - Register",form=form)

@pages.route("/logout")
def logout():
    session.clear()
    return redirect(url_for(".index"))

@pages.route("/timetable/<string:_id>/delete")
@login_required
def delete_timetable(_id:str):
    if not (_id in User(**(current_app.db.user.find_one({"_id":session.get("_id")}))).timetables):
        abort(401)
    
    for subject in Timetable(**(current_app.db.timetable.find_one({"_id":_id}))).subjects:
        current_app.db.subject.delete_one({"_id":subject})
    current_app.db.timetable.delete_one({"_id":_id})
    user_data=current_app.db.user.find_one({"_id":session.get("_id")})
    user=User(**user_data)
    user.timetables.pop(user.timetables.index(_id))
    current_app.db.user.replace_one(current_app.db.user.find_one({"_id":session.get("_id")}),asdict(user))
    return redirect(url_for(".login"))


@pages.route("/timetable/<string:_id>/view")
@login_required
def view_timetable(_id:str):
    if not (_id in User(**(current_app.db.user.find_one({"_id":session.get("_id")}))).timetables):
        abort(401)
    timetable_data=current_app.db.timetable.find_one({"_id":_id})
    timetable=Timetable(**timetable_data)
    subject_data=[current_app.db.subject.find_one({"_id":sub_id}) for sub_id in timetable.subjects]
    subjects=[Subject(**subject) for subject in subject_data]
    return render_template("view.html",title="Timetable Planner - edit",subject_data=subject_data,timetable=timetable)    

@pages.route("/timetable/<string:_id>/edit",methods=["GET","POST"])
def edit_timetable(_id:str):
    if not (_id in User(**(current_app.db.user.find_one({"_id":session.get("_id")}))).timetables):
        abort(401)
    
    form=AddSubject()
    timetable_data=current_app.db.timetable.find_one({"_id":_id})

    timetable=Timetable(**timetable_data)
    subject_data=[current_app.db.subject.find_one({"_id":sub_id}) for sub_id in timetable.subjects]
    subjects=[Subject(**subject) for subject in subject_data]
    total_duration=sum([item.duration for item in subjects])
    current_app.db.timetable.update_one({"_id":_id},{"$set":{"duration":total_duration}})

    if form.validate_on_submit():
        subject=Subject(
            _id=uuid.uuid4().hex,
            name=(form.name.data).capitalize(),
            duration=form.duration.data
        )
        if (total_duration+subject.duration)>=24:
            flash("Timetable cannot be longer than 24 Hours. Take a break.","danger")
            return redirect(url_for(".edit_timetable",_id=_id))
        
        current_app.db.subject.insert_one(asdict(subject))
        current_app.db.timetable.update_one({"_id":_id},{"$push":{"subjects":subject._id}})
        return redirect(url_for(".edit_timetable",_id=_id))
    return render_template("edit.html",timetable_id=_id,form=form,subject_data=subjects,title="Timetable Planner - edit",total_duration=total_duration,name=timetable.name)

@pages.route("/timetable/<string:timetable_id>/subject/<string:subject_id>/delete")
@login_required
def delete_subject(timetable_id:str,subject_id:str):
    if not (timetable_id in User(**(current_app.db.user.find_one({"_id":session.get("_id")}))).timetables):
        abort(401)
    if not (subject_id in Timetable(**(current_app.db.timetable.find_one({"_id":timetable_id}))).subjects):
        abort(401)
    current_app.db.subject.delete_one({"_id":subject_id})
    timetable_data=current_app.db.timetable.find_one({"_id":timetable_id})
    timetable=Timetable(**timetable_data)
    timetable.subjects.pop(timetable.subjects.index(subject_id))
    current_app.db.timetable.replace_one(current_app.db.timetable.find_one({"_id":timetable_id}),asdict(timetable))
    return redirect(url_for(".edit_timetable",_id=timetable_id))

    
