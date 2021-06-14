from flask import Flask, render_template, request
from flask.wrappers import Request
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
    #app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
    app.config['SQLALCHEMY_DATABASE_URI'] = params['kapil_database']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

db = SQLAlchemy(app)

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
    website_link = db.Column(db.String(120), nullable=True)
    download_link = db.Column(db.String(120), nullable=True)
    documentation_link = db.Column(db.String(120), nullable=True)
    other_link = db.Column(db.String(120), nullable=True)
    logo = db.Column(db.String(120), nullable=True)
    slug = db.Column(db.String(100), nullable=True)


@app.route("/")
def home():
    languages= Languages.query.all() 
    return render_template('home.html', params=params,languages = languages)


@app.route("/post/<string:languages_slug>", methods=['GET'])
def post(languages_slug):
    languages = Languages.query.filter_by(slug=languages_slug).first()
    return render_template('post.html',language=languages,params=params)

@app.route("/about")
def about():
    return render_template('about.html', params=params)


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
        return render_template("AddLanguage.html", params=params)
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        web_link = request.form.get("web_link")
        down_link = request.form.get("down_link")
        document_link = request.form.get("document_link")
        logo_link = request.form.get("logo_link")
        language = Languages(
            name = name,
            decription = description,
            website_link = web_link,
            download_link = down_link,
            documentation_link = document_link,
            logo = logo_link,
            slug = str(name).replace(" ","_")
        )
        db.session.add(language)
        db.session.commit()
        msg = str(name)+" added Successfully"
        print(msg)
        return render_template("AddLanguage.html", params=params,message = msg)
app.run(debug=True)


app.run(debug=True)
