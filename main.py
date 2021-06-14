from flask import Flask, render_template, request
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
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

db = SQLAlchemy(app)
print("this is change")

class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone_num = db.Column(db.String(12), nullable=False)
    msg = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    email = db.Column(db.String(20), nullable=False)

class Languages(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name= db.Column(db.String(80), nullable=False)
    decription = db.Column(db.String(21), nullable=False)
    website_link = db.Column(db.String(120), nullable=False)
    download_link = db.Column(db.String(12), nullable=True)
    documentation_link = db.Column(db.String(12), nullable=True)
    other_link = db.Column(db.String(12), nullable=True)
    logo = db.Column(db.String(12), nullable=True)
    slug = db.Column(db.String(12), nullable=True)


@app.route("/")
def home():
    #yaha per fetch bhi to krna pedega post kr nahi yaha nahi aega ya to sare post fetch honge jitne bhi he data base me
    languages= Languages.query.all() #yaha per sari post ki list aegi for index ke through ek ek post ko lelenge ok 
    
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


app.run(debug=True)