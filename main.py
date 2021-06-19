from flask import Flask, render_template, request,redirect,abort
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
import json
from datetime import datetime
with open('config.json', 'r') as c:
    params = json.load(c)["params"]

local_server = True
app = Flask(__name__)
app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['gmail-user'],
    MAIL_PASSWORD=  params['gmail-password']
)
mail = Mail(app)
if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
    #app.config['SQLALCHEMY_DATABASE_URI'] = params['kapil_database']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']
db = SQLAlchemy(app)
class Admin(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    lastname = db.Column(db.String(80), nullable=False)
    user_id = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(30), nullable=False)

class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone_num = db.Column(db.String(10), nullable=False)
    msg = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    email = db.Column(db.String(20), nullable=False)

class Languages(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name= db.Column(db.String(80), nullable=False)
    decription = db.Column(db.String(300), nullable=False)
    website_link = db.Column(db.String(120), nullable=False)
    download_link = db.Column(db.String(120), nullable=False)
    documentation_link = db.Column(db.String(120), nullable=False)
    other_link = db.Column(db.String(120), nullable=True)
    logo = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(100), nullable=False)


@app.route("/")
def home():
    return render_template('home.html', params=params)
@app.route("/post/<string:languages_slug>", methods=['GET'])
def post(languages_slug):
    languages = Languages.query.filter_by(slug=languages_slug).first()
    return render_template('post.html',language=languages,params=params)

@app.route("/about")
def about():
    return render_template('about.html', params=params)


@app.route("/login",methods = ["POST","GET"])
def login():
    if request.method == "GET":
        return render_template("login.html", params=params)
    if request.method == "POST":
        user_id = request.form.get("user_id")
        password = request.form.get("password")
        #check if any user exist in database having same user id 
        user = Admin.query.filter_by(user_id = user_id).first()
        if (user.user_id==user_id) or (user.password == password):
                return render_template("add.html", params=params)
        else:
            msg = "Email or Password may be wrong"
            return render_template("login.html", params=params,message = msg)

@app.route("/contact", methods = ['GET', 'POST'])
def contact():
    if(request.method=='POST'):
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        entry = Contacts(name=name, phone_num = phone, msg = message, date= datetime.now(),email = email )
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New message from ' + name,
                          sender=email,
                          recipients = [params['gmail-user']],
                          body = message + "\n" + phone
                          )
    return render_template('contact.html', params=params)


@app.route("/addlanguage",methods = ["GET","POST"])
def AddLanguage():
    if request.method == "GET":
        return render_template("add.html", params=params)

    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        web_link = request.form.get("website_link")
        down_link = request.form.get("download_link")
        document_link = request.form.get("documentation_link")
        logo_link = request.form.get("logo_link")
        language = Languages(
            name = name,
            decription = description,
            website_link =  web_link,
            download_link = down_link,
            documentation_link = document_link,
            logo = logo_link,
            slug = str(name).replace(" ","_")
        )
        db.session.add(language)
        db.session.commit()
        msg = str(name)+" added Successfully"
        return render_template("add.html", params=params,message = msg)


@app.route("/language/<string:lan>")
def showLanguages(lan):
    if lan == "":
        abort(404)
    elif lan == "all":
        languages = Languages.query.all()
    else:
        languages = Languages.query.filter_by(name = lan).all()
        print(languages)
        if not languages:
            return abort(404)
    return render_template("showlanguages.html",languages = languages)
@app.route("/searchapi")
def searchapi():
    languages= Languages.query.all()
    language_name = list(map(lambda x: x.name,languages))
    language_dict = {}
    for x in range(len(language_name)):
        language_dict[x] = language_name[x]
    return language_dict
app.run(debug=True)
