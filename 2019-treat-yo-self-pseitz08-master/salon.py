from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import datetime

app=Flask(__name__)
app.secret_key = "This is a terrible key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///salon.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db=SQLAlchemy(app)

appointmentPatron =db.Table('appointmentPatron',
    db.Column('appointment_id', db.Integer, db.ForeignKey('appointment.id')),
    db.Column('patron_id', db.Integer, db.ForeignKey('patron.id')))

appointmentStylist = db.Table('appointmentStylist',
    db.Column('appointment_id', db.Integer, db.ForeignKey('appointment.id')),
    db.Column('stylist_id', db.Integer, db.ForeignKey('stylist.id')))
    





class Owner(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    un = db.Column(db.String(30))
    pw = db.Column(db.String(30))
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(30))

    def __init__(self,un,pw,first_name="Philip",last_name="Seitz"):
        self.un = un
        self.pw = pw
        self.first_name = first_name
        self.last_name = last_name

class Patron(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    un = db.Column(db.String(30))
    pw = db.Column(db.String(30))
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(30))
    #appointmentList = db.Column(db.Integer, db.ForeignKey('appointment.id'))
    appointmentList = db.relationship('Appointment', backref='patron', lazy='select', uselist = False)
    appointments = db.relationship('Appointment', secondary=appointmentPatron, backref='patron1', lazy='select')
    

    def __init__(self,un,pw,first_name,last_name):
        self.un = un
        self.pw = pw
        self.first_name = first_name
        self.last_name = last_name

class Stylist(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    un = db.Column(db.String(30))
    pw = db.Column(db.String(30))
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(30))
    appointments = db.relationship('Appointment', secondary=appointmentStylist, backref='stylist1', lazy='select')
    #appointmentList = db.Column(db.Integer, db.ForeignKey('appointment.id'))
    appointmentList = db.relationship('Appointment', backref='stylist', lazy='select', uselist = False)


    def __init__(self,un,pw,first_name,last_name):
        self.un = un
        self.pw = pw
        self.first_name = first_name
        self.last_name = last_name

class PatronBook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(30))
    time = db.Column(db.String(30))
    patron_id = db.Column(db.Integer, db.ForeignKey('patron.id'))

class StylistBook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(30))
    time = db.Column(db.String(30))
    stylist_id = db.Column(db.Integer, db.ForeignKey('stylist.id'))

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    #patron = db.relationship('Patron', backref='appointment', lazy='select', uselist = False)
    #stylist = db.relationship('Stylist', backref='appointment', lazy='select', uselist = False)
    #patron = db.relationship('Patron', secondary=appointmentPatron, backref='appointment', lazy='select')
    stylist_id = db.Column(db.Integer, db.ForeignKey('stylist.id'))
    patron_id = db.Column(db.Integer, db.ForeignKey('patron.id'))



patrons = [
    Patron(un="p1",pw="p1",first_name="Joe",last_name="Harris"),
    Patron(un="p2",pw="p2",first_name="Jamal",last_name="Crawford"),
    Patron(un="p3",pw="p3",first_name="Vince",last_name="Carter")
]

stylists = [
    Stylist(un="s1",pw="s1",first_name="Jermaine",last_name="Cole"),
    Stylist(un="s2",pw="s2",first_name="Kendrick",last_name="Lamar"),
    Stylist(un="s3",pw="s3",first_name="Malcom",last_name="McCormick")
]

appointmenter = [
    PatronBook(date="08/10/98",time="8:00"),
    PatronBook(date="08/10/98",time="8:00"),
    PatronBook(date="08/10/98",time="8:00"),
    PatronBook(date="08/11/98",time="8:00")
]

user=""

@app.route("/")
def hello():
    return render_template('home_page.html')

@app.route("/members/", methods=['POST'])
def members():
    un = request.form.get("un")
    pw = request.form.get("pw")
    global user
    user=un
    if un == Owner.query.all()[0].un and pw == Owner.query.all()[0].pw:
        #global user
        #user = Owner.query.all()[0]
        return redirect(url_for('owner_page'))
    elif un in [patron.un for patron in Patron.query.all()] and Patron.query.filter_by(un=un).first().pw == pw:
        #user = Patron.query.filter_by(un=un).first()
        #print(Patron.query.filter_by(un=un).first().first_name)
        print("patron")
        return redirect(url_for('patron_page', uname = un))
    elif un in [stylist.un for stylist in Stylist.query.all()]:
        #user = Stylist.query.filter_by(un=un).first()
        return redirect(url_for('stylist_page', uname = un))
    else:
        return redirect(url_for('hello'))

#Owner routes
@app.route("/members/owner/")
def owner_page():
    return render_template('owner_page.html',fn=Owner.query.all()[0].first_name,
                            ln=Owner.query.all()[0].last_name,
                            stylists=Stylist.query.all(),
                            patrons=Patron.query.all(),
                            name = datetime.datetime.now())

@app.route("/members/owner/new_stylist/")
def new_stylist():
    return render_template('new_stylist.html')

@app.route("/members/owner/new_stylist/add_stylist", methods=['POST'])
def add_stylist():
    db.session.add(Stylist(request.form.get('username'),
                            request.form.get('password'),
                            request.form.get('firstname'),
                            request.form.get('lastname')))
    
    db.session.commit()

    return redirect(url_for('owner_page'))

@app.route("/members/owner/stylists/")
def owner_to_stylist():
    #print(request.args.get('un'))
    return redirect(url_for('stylist_view', uname=request.args.get('un')))

@app.route("/members/owner/stylists/<uname>")
def stylist_view(uname):
    return render_template('stylist_page.html',
                            user = user,
                            person = Stylist.query.filter_by(un=uname).first(),
                            date = [datetime.datetime.now(),
                                    datetime.datetime.now() + timedelta(days=1),
                                    datetime.datetime.now() + timedelta(days=2),
                                    datetime.datetime.now() + timedelta(days=3),
                                    datetime.datetime.now() + timedelta(days=4),
                                    datetime.datetime.now() + timedelta(days=5),
                                    datetime.datetime.now() + timedelta(days=6)],
                                    appointments = Appointment.query.filter_by(stylist_id=Stylist.query.filter_by(un=uname).first().id))

@app.route("/members/owner/patrons/")
def owner_to_patron():
    #print(request.args.get('un'))
    return redirect(url_for('owner_view', uname=request.args.get('un')))

@app.route("/members/owner/patrons/<uname>")
def owner_view(uname):
    return render_template('patron_page.html',
                            person = Patron.query.filter_by(un=uname).first(),
                            stylists=Stylist.query.all(),
                            date = datetime.datetime.now(),
                            appointments = Appointment.query.filter_by(patron_id=Patron.query.filter_by(un=uname).first().id))


#Patron routes
@app.route("/members/patrons/<uname>/")
def patron_page(uname):
    print("Here")
    return render_template('patron_page.html',
                            person=Patron.query.filter_by(un=uname).first(),
                            stylists=Stylist.query.all(),
                            date = datetime.datetime.now(),
                            appointments = Appointment.query.filter_by(patron_id=Patron.query.filter_by(un=uname).first().id))

@app.route("/members/patrons/stylists/")
def patron_to_stylist():
    #print(request.args.get('un'))
    return redirect(url_for('patron_view', uname=request.args.get('un')))

@app.route("/members/patrons/stylists/<uname>")
def patron_view(uname):
    return render_template('stylist_page.html',
                            user="",
                            person = Stylist.query.filter_by(un=uname).first(),
                            date = [datetime.datetime.now(),
                                    datetime.datetime.now() + timedelta(days=1),
                                    datetime.datetime.now() + timedelta(days=2),
                                    datetime.datetime.now() + timedelta(days=3),
                                    datetime.datetime.now() + timedelta(days=4),
                                    datetime.datetime.now() + timedelta(days=5),
                                    datetime.datetime.now() + timedelta(days=6)],
                                    appointments = Appointment.query.filter_by(stylist_id=Stylist.query.filter_by(un=uname).first().id))

@app.route("/members/patrons/make_appointment/", methods=['POST'])
def make_appointment():
    return render_template('make_appointment.html',
                            stylists=Stylist.query.all(),
                            user = request.args.get('patron'))

@app.route("/members/patrons/create_appointment/", methods=['POST'])
def create_appointment():
    print(request.form.get('drop'))
    a = Appointment(DateTime(request.form.get('date')))
    db.session.add(a)
    a.stylist = Stylist.query.filter_by(un=request.form.get('drop'))
    a.patron = Patron.query.filter_by(un=request.args.get('patron'))
    Patron.query.filter_by(un=request.args.get('patron')).appointments.append(a)
    Stylist.query.filter_by(un=request.form.get('drop')).appointments.append(a)
    db.session.commit()
    return redirect('patron_page', uname=request.args.get('patron'))

@app.route("/members/patrons/cancel_appointment/", methods=['POST'])
def cancel_appointment():
    return render_template('cancel_app.html',
                            appointments = request.args.get('apps'))

@app.route("/registration/", methods=['POST'])
def new_patron():
    return render_template('new_patron.html')

@app.route("/registration/add_patron", methods=['POST'])
def add_patron():
    db.session.add(Patron(request.form.get('username'),
                            request.form.get('password'),
                            request.form.get('firstname'),
                            request.form.get('lastname')))
    
    db.session.commit()
    return redirect(url_for('hello'))

#Stylist routes
@app.route("/members/stylists/<uname>/")
def stylist_page(uname):
    print("Here")
    return render_template('stylist_page.html',
                            person=Stylist.query.filter_by(un=uname).first(),
                            date = [datetime.datetime.now(),
                                    datetime.datetime.now() + timedelta(days=1),
                                    datetime.datetime.now() + timedelta(days=2),
                                    datetime.datetime.now() + timedelta(days=3),
                                    datetime.datetime.now() + timedelta(days=4),
                                    datetime.datetime.now() + timedelta(days=5),
                                    datetime.datetime.now() + timedelta(days=6)],
                            appointments = Appointment.query.filter_by(stylist_id=Stylist.query.filter_by(un=uname).first().id))


@app.cli.command("initdb")
def initdb():
    """Creates SQLite Database"""
    db.drop_all()
    db.create_all()
    print("Database initialized.")

    """Adds Owner to the db"""
    db.session.add(Owner("owner","pass"))
    db.session.commit()
    print("Owner Added")

@app.cli.command("add_owner")
def create_owner():
    """Adds Owner to the db"""
    db.session.add(Owner("owner","pass"))
    db.session.commit()
    print("Owner Added")

@app.cli.command("add_patrons")
def create_patrons():
    """Adds Patrons to the db"""
    i=0
    for people in patrons:
        db.session.add(people)
        db.session.add(appointments[i])
        people.appointments = appointments[i]
        i+=1

    db.session.commit()
    print("Patrons Added")

@app.cli.command("add_stylists")
def create_stylists():
    """Adds Stylists to the db"""
    for people in stylists:
        db.session.add(people)

    db.session.commit()
    print("Stylists Added")

@app.cli.command("bootstrap")
def bootstrap():

    """Adds Patrons to the db"""
    for people in patrons:
        db.session.add(people)

    a1 = Appointment(date=datetime.datetime.now())
    a2 = Appointment(date=datetime.datetime.now() + timedelta(days=1))
    a3 = Appointment(date=datetime.datetime.now() + timedelta(days=2))

    db.session.add(a1)
    db.session.add(a2)
    db.session.add(a3)

    a1.patron = patrons[0]
    a1.stylist = stylists[0]

    a2.patron = patrons[0]
    a2.stylist = stylists[1]

    a3.patron = patrons[0]
    a3.stylist = stylists[2]

    patrons[0].appointments.extend((a1,a2,a3))
    stylists[0].appointments.append(a1)
    stylists[1].appointments.append(a2)
    stylists[2].appointments.append(a3)

    db.session.commit()
    print("Patrons Added")

    """Adds Stylists to the db"""
    for people in stylists:
        db.session.add(people)

    db.session.commit()
    print("Stylists Added")

      





if __name__ == "__main__":
    app.run()