from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

import json

from datetime import datetime


# Add this to fix the MySQLdb import issue
import pymysql
pymysql.install_as_MySQLdb()
#file opening process
with open('config.json', 'r') as c:
    params = json.load(c)["params"]

local_server = True
app = Flask(__name__)
###app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/popcornwizard'

if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']


db = SQLAlchemy(app)


class Contacts(db.Model):
    '''
    sno, name phone_num, msg, date, email
    '''
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(20), nullable=False)
    phoneno = db.Column(db.String(12), nullable=False)
    msg = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    

class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(21), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    img_file = db.Column(db.String(12), nullable=True)


@app.route("/")
def home():
    posts = Posts.query.all()
    return render_template('index.html', params=params, posts=posts)


@app.route("/about")
def about():
    return render_template('about.html', params=params)


@app.route("/contact", methods = ['GET', 'POST'])
def contect():
    if(request.method=='POST'):
        '''Add entry to the database'''
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        entry = Contacts(name=name, phoneno=phone, msg=message, date=datetime.now(), email=email)
        db.session.add(entry)
        db.session.commit()
    return render_template('contect.html', params=params)


@app.route("/post/<string:post_slug>")
def post_route(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    if not post:
        return "404 - Not Found", 404
    return render_template("post.html", params=params, post=post)



if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        # Insert a test post if none exists
        if not Posts.query.first():
            test_post = Posts(
                title="First Post",
                slug="first-post",
                content="This is the first test post created automatically.",
                date=datetime.now().strftime("%Y-%m-%d"),
                img_file="home-bg.jpg"
            )
            db.session.add(test_post)
            db.session.commit()
    app.run(debug=True)
