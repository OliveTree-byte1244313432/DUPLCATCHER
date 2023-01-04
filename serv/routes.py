from serv.models import User, Papers
from flask import render_template, url_for, flash, redirect
from serv.forms import LoginForm, AddPaper
from serv import app, db
from flask_login import login_user, current_user, logout_user
import textract
from flask import request
import os
from werkzeug.utils import secure_filename
from os.path import join, dirname, realpath
import codecs
from boilerpy3 import extractors
import urllib
import requests
import urllib.request
from urllib.request import urlopen, Request
from boilerpy3 import extractors
from serv.functions import findplag
import os

googlepath = join(dirname(realpath(__file__)), 'endless-bank-344008-a75f5b89470f.json')
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = googlepath

@app.route("/")
def homepage():
    if current_user.is_authenticated:
        return redirect(url_for('aboutpage'))
    return render_template('home.html')

@app.route("/login", methods=['GET', 'POST'])
def loginpage():
    form = LoginForm()
    if form.validate_on_submit():
        valid = 0
        a = User.query.all()
        for i in a:
            if i.username==form.username.data and form.password.data==i.password:
                valid = 1
                login_user(i,remember=form.remember.data)
                flash("Successfully logged in!", 'success')
                return redirect(url_for('userapp'))
        if valid == 0 :
            flash("Incorrect username or password. Please make sure you have enterred the correct username and password!", 'danger')

    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    flash("Successfully logged out!", 'success')
    return redirect(url_for('homepage'))


@app.route("/about")
def aboutpage():
    return render_template('about.html', title='About')

@app.route("/contact")
def contactpage():
    return render_template('contact.html', title='Contact us')

@app.route("/userapp")
def userapp():
    if current_user.is_authenticated:
        return render_template('userapp.html', title='User page!')
    else:
        flash("You must login to access this page!!", 'danger')
        return redirect(url_for('homepage'))


def findreports():
    if current_user.is_authenticated:
        a = Papers.query.all()
        b = []
        for i in a:
            if i.user_id==current_user.id:
                b.append(i.name)
        return b
    else:
        flash('fail', 'danger')

@app.route("/userapp/pastreports")
def pastreports():
    if current_user.is_authenticated:
        b = findreports()
        return render_template('pastreports.html', title='User page!', pastreports=b)
    else:
        return redirect(url_for('homepage'))



def savenewpaper(text, name):
        paper = Papers(name=name, content=text, report="No report yet", user_id=current_user.id)
        db.session.add(paper)
        db.session.commit()


@app.route("/userapp/scanpapers", methods=['GET', 'POST'])
@app.route("/userapp/scanpapers")
def scanpapers():
    form = AddPaper()
    if form.validate_on_submit():
        if request.method == 'POST':
            file = request.files['paper']
            language = request.form['language']
            filename, file_extension = os.path.splitext(file.filename)
            if file_extension==".Docx" or file_extension==".DOCX" or file_extension==".docx" or file_extension==".doc" or file_extension==".DOC" or file_extension==".PDF" or file_extension==".pdf" or file_extension==".odt" or file_extension==".ODT" or file_extension==".txt" or file_extension==".TXT" or file_extension==".PNG" or file_extension==".png" or file_extension==".jpg" or file_extension==".jpeg" or file_extension==".JPG" or file_extension==".JPEG":
                UPLOADS_PATH = join(dirname(realpath(__file__)), 'static/')
                new_filename = secure_filename(file.filename)
                file.save(os.path.join(UPLOADS_PATH, new_filename))
                link_to_file = os.path.join(UPLOADS_PATH, new_filename)
                hex = textract.process(link_to_file)
                savenewpaper(hex, file.filename)
                p = Papers.query.filter_by(name=file.filename).order_by(Papers.id.desc())[0]
                newhex = p.content
                hex_bext = newhex[1:]
                hex_best = newhex[:1]
                text = bytes.fromhex(str(hex_bext)).decode('utf-8')
                text = hex_best + text
                p.content = text[1:]
                report = findplag(text[1:], language)
                p.report = report
                db.session.commit()
                os.remove(os.path.join(UPLOADS_PATH, new_filename))
                flash("Successfully uploaded file!", 'success')
    if current_user.is_authenticated:
        return render_template('scanpapers.html', title='User page!', form=form)
    else:
        return redirect(url_for('homepage'))
reportoptiondiv big div

reportoptionname float left

reportoptionother float right

@app.route("/viewreport/<papername>/<id>")
def viewreport(papername):
    a = Papers.query.all()
    b = False
    for i in a:
        if i.user_id==current_user.id and i.name==papername and i.id==id:
             papercontent = i.content
             paperreport = i.report
             b = True
    if current_user.is_authenticated and papername!=null and b==True:
        return render_template('viewreport.html', title='Report viewing page!', papername=papername, papercontent=papercontent, paperreport=paperreport)
    else:
        flash("You must login to access this page!", 'danger')
        return redirect(url_for('homepage'))
