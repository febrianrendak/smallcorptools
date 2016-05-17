import json, os
from flask import Flask, url_for, redirect, request, session, render_template
from flask_login import (UserMixin, login_required, login_user, logout_user, current_user)
from flask_googlelogin import GoogleLogin
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
dbh = client.jawdat_internal
users = {}

app = Flask(__name__)
app.config.update(
    SECRET_KEY='4muANF@rg$y$&g4sNA2N1HGgAs435hg&',
    GOOGLE_LOGIN_CLIENT_ID='1039968362259-jndiml8ce9d74taggppcjogrsa7q1dog.apps.googleusercontent.com',
    GOOGLE_LOGIN_CLIENT_SECRET='sjNHDUNlFmL-8WQL8mmpUgRk',
    GOOGLE_LOGIN_REDIRECT_URI='http://localhost:5000/oauth2callback')
googlelogin = GoogleLogin(app)

class User(UserMixin):
    def __init__(self, userinfo):
        self.id = userinfo['id']
        self.name = userinfo['name']
        self.email = userinfo['email']
        self.domain = userinfo['hd']
        self.picture = userinfo.get('picture')

@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)

@googlelogin.user_loader
def get_user(userid):
    return users.get(userid)

@app.route('/')
def index():
    g_url = googlelogin.login_url(approval_prompt='force', scopes=['email'])
    return render_template('login.html', g_url=g_url)

@app.route('/main')
# @login_required
def main():
    # return render_template('index.html', username=current_user.name,
    #     profpic=current_user.picture, email=current_user.email)
    return render_template('index.html', username="Mohammad Riftadi",
        email="riftadi@jawdat.com")

@app.route('/create_claim', methods=['GET', 'POST'])
# @login_required
def create_claim():
    if request.method == "POST":
        print request.form
        return render_template('create-claim.html', username=current_user.name,
            profpic=current_user.picture, email=current_user.email,
            empdetail=employee, supdetail=supervisor)

    eh = dbh.employees

    # employee = eh.find_one({"username" : current_user.email})
    employee = eh.find_one({"username" : "riftadi@jawdat.com"})
    supervisor = eh.find_one({"username" : employee["supervisor"]})

    # return render_template('create-claim.html', username=current_user.name,
    #     profpic=current_user.picture, email=current_user.email,
    #     empdetail=employee, supdetail=supervisor)
    return render_template('create-claim.html', username="Mohammad Riftadi",
        email="riftadi@jawdat.com", empdetail=employee, supdetail=supervisor)

@app.route('/oauth2callback')
@googlelogin.oauth2callback
def login(token, userinfo, **params):
    # print userinfo
    user = users[userinfo['id']] = User(userinfo)
    login_user(user)
    session['token'] = json.dumps(token)
    session['extra'] = params.get('extra')
    return redirect(url_for('main'))

@app.route('/logout')
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('index'))

app.run(debug=True, host="0.0.0.0", port=5000, threaded=True)
