import json, os
from bson.objectid import ObjectId
from datetime import date, datetime
from flask import Flask, url_for, redirect, request, session, render_template, jsonify
from flask_login import (UserMixin, login_required, login_user, logout_user, current_user)
from flask_googlelogin import GoogleLogin
# from flask_weasyprint import HTML, render_pdf
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

def strip_curr(curr_str):
    return filter(type(curr_str).isdigit, curr_str)

def convert_to_datetime(date_ind_string):
    day, month, year = [int(x) for x in date_ind_string.split('/')]
    return datetime(year, month, day)

@app.context_processor
def utility_processor():
    def convert_period_to_text(per_str):
        prev_month_dict = {
            "02" : "Januari",
            "03" : "Februari",
            "04" : "Maret",
            "05" : "April",
            "06" : "Mei",
            "07" : "Juni",
            "08" : "Juli",
            "09" : "Agustus",
            "10" : "September",
            "11" : "Oktober",
            "12" : "November",
            "01" : "Desember"
        }
        month_dict = {
            "01" : "Januari",
            "02" : "Februari",
            "03" : "Maret",
            "04" : "April",
            "05" : "Mei",
            "06" : "Juni",
            "07" : "Juli",
            "08" : "Agustus",
            "09" : "September",
            "10" : "Oktober",
            "11" : "November",
            "12" : "Desember"
        }

        if per_str[:2] == "01":
            first_year = "20%d" % int(per_str[2:])-1
        else:
            first_year = "20%s" % per_str[2:]
        second_year = "20%s" % per_str[2:]
        
        return "21 %s %s - 20 %s %s" % (prev_month_dict[per_str[:2]], \
            first_year, month_dict[per_str[:2]], second_year)
    return dict(convert_period_to_text=convert_period_to_text)

@app.context_processor
def utility_processor():
    def format_currency(amount):
        return "Rp %s,00" % format(amount, ',d').replace(',', '.')
    return dict(format_currency=format_currency)

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
    return render_template('login.htm.j2', g_url=g_url)

@app.route('/main')
# @login_required
def main():
    # return render_template('index.htm.j2', username=current_user.name,
    #     profpic=current_user.picture, email=current_user.email)
    return render_template('index.htm.j2', username="Mohammad Riftadi",
        email="riftadi@jawdat.com")

@app.route('/create_claim', methods=['GET', 'POST'])
# @login_required
def create_claim():
    eh = dbh.employees
    cch = dbh.costcenters
    rch = dbh.reimburse_claims

    # employee = eh.find_one({"username" : current_user.email})
    employee = eh.find_one({"username" : "riftadi@jawdat.com"})
    supervisor = eh.find_one({"username" : employee["supervisor"]})

    today = date.today()
    if today.day <= 20:
        period = "%02d%02d" % (today.month, today.year % 100)
        if today.month == 1:
            prev_period = "%02d%02d" % (12, (today.year % 100) - 1)
        else:
            prev_period = "%02d%02d" % (today.month - 1, today.year % 100)
    else:
        prev_period = "%02d%02d" % (today.month, today.year % 100)
        if today.month == 12:
            period = "%02d%02d" % (1, (today.year % 100) + 1)
        else:
            period = "%02d%02d" % (today.month + 1, today.year % 100)
        
    periodlist = []
    for p in [prev_period, period]:
        qr = rch.find({"$and" : [{"username" : "riftadi@jawdat.com",
            "period" : p, "status" : {"$ne" : "rejected"}}]})
        if qr.count() == 0:
            periodlist.append(p)

    cclist = list(cch.find())

    # return render_template('create-claim.htm.j2', username=current_user.name,
    #     profpic=current_user.picture, email=current_user.email,
    #     empdetail=employee, supdetail=supervisor)
    return render_template('create-claim.htm.j2', username="Mohammad Riftadi",
        email="riftadi@jawdat.com", empdetail=employee, supdetail=supervisor,
        periodlist=periodlist, cclist=cclist)

@app.route('/confirm_claim', methods=['POST'])
# @login_required
def confirm_claim():
    eh = dbh.employees
    cch = dbh.costcenters
    rch = dbh.reimburse_claims

    f = request.form
    expense_list = []
    subtotal = 0
    i = 0
    ccnamemap = {}

    # employee = eh.find_one({"username" : current_user.email})
    employee = eh.find_one({"username" : f["employee-email"]})
    supervisor = eh.find_one({"username" : employee["supervisor"]})
    costcenters = cch.find()

    for cc in costcenters:
        ccnamemap[cc["costcenter_id"]] = cc["costcenter_name"]

    while f.get("expense[%d].date" % i):
        ed = {}
        ed["date"] = convert_to_datetime(f.get("expense[%d].date" % i))
        ed["description"] = f.get("expense[%d].description" % i)
        ed["category"] = f.get("expense[%d].category" % i)
        ed["costcenter"] = f.get("expense[%d].costcenter" % i)
        ed["cost"] = int(strip_curr(f.get("expense[%d].cost" % i)))
        subtotal += ed["cost"]
        expense_list.append(ed)
        i += 1

    claim = {}
    claim["username"] = f["employee-email"]
    claim["fullname"] = f["employee-name"]
    claim["period"] = f["expense-period"]
    claim["approved_by"] = supervisor["username"]
    claim["status"] = "presubmitted"
    claim["expense_list"] = expense_list
    if f["cash-advance"]:
        claim["cash_advance"] = int(strip_curr(f["cash-advance"]))
    else:
        claim["cash_advance"] = 0
    claim["subtotal"] = subtotal
    claim["total"] = claim["subtotal"] - claim["cash_advance"]

    rch.insert_one(claim)

    return render_template('confirm-claim.htm.j2', username="Mohammad Riftadi",
        email="riftadi@jawdat.com", empdetail=employee, supdetail=supervisor,
        claim=claim, ccnamemap=ccnamemap)

@app.route('/submit_claim', methods=['POST'])
# @login_required
def submit_claim():
    f = request.form
    rch = dbh.reimburse_claims

    username = f["employee-email"]
    period = f["period-normalized"]
    date_submitted = datetime.now()

    rch.update({"username" : username, "period" : period}, {"$set" : 
        {"status" : "submitted", "date_submitted" : date_submitted}})

    return redirect(url_for('list_claim'))

@app.route('/view_detail_claim/<claim_id>')
# @login_required
def view_detail_claim(claim_id):
    rch = dbh.reimburse_claims
    cch = dbh.costcenters

    ccnamemap = {}
    costcenters = cch.find()

    for cc in costcenters:
        ccnamemap[cc["costcenter_id"]] = cc["costcenter_name"]

    claim = rch.find_one({"_id" : ObjectId(claim_id)})

    return render_template('view-detail-claim.htm.j2', claim=claim, ccnamemap=ccnamemap)

@app.route('/generate_claim_report/<claim_id>')
# @login_required
def generate_claim_report(claim_id):
    eh = dbh.employees
    cch = dbh.costcenters
    rch = dbh.reimburse_claims
    ccnamemap = {}

    # employee = eh.find_one({"username" : current_user.email})
    employee = eh.find_one({"username" : "riftadi@jawdat.com"})
    supervisor = eh.find_one({"username" : employee["supervisor"]})
    costcenters = cch.find()

    for cc in costcenters:
        ccnamemap[cc["costcenter_id"]] = cc["costcenter_name"]

    claim = rch.find_one({"_id" : ObjectId(claim_id)})

    html = render_template('claim-printed-form.htm.j2', username="Mohammad Riftadi",
        email="riftadi@jawdat.com", empdetail=employee, supdetail=supervisor,
        claim=claim, ccnamemap=ccnamemap)

    return html
    # return render_pdf(HTML(string=html))

@app.route('/cancel_claim', methods=['POST'])
# @login_required
def cancel_claim():
    f = request.form
    rch = dbh.reimburse_claims

    username = f["employee-email"]
    period = f["period-normalized"]

    rch.delete_many({"username" : username,
        "period" : period, "status" : "presubmitted"})

    return redirect(url_for('create_claim'))

@app.route('/list_claim')
# @login_required
def list_claim():
    rch = dbh.reimburse_claims
    claim_list = rch.find({"username" : "riftadi@jawdat.com"})

    return render_template('list-claim.htm.j2', username="Mohammad Riftadi",
        email="riftadi@jawdat.com", claim_list=claim_list)

@app.route('/delete_claim/<claim_id>')
# @login_required
def delete_claim(claim_id):
    rch = dbh.reimburse_claims
    rch.delete_one({"_id" : ObjectId(claim_id)})
    return jsonify({"deleted" : True})

@app.route('/verify_claim')
# @login_required
def verify_claim():
    rch = dbh.reimburse_claims
    claim_list = rch.find({"status" : "submitted"})

    return render_template('verify-claim.htm.j2', username="Mohammad Riftadi",
        email="riftadi@jawdat.com", claim_list=claim_list)

@app.route('/verify_claim/<claim_id>')
# @login_required
def verify_claim_id(claim_id):
    # check if accounting
    rch = dbh.reimburse_claims
    claim = rch.update_one({"_id" : ObjectId(claim_id)}, {"$set" : {"status" : "verified"}})

    return jsonify({"approved" : True})

@app.route('/approve_claim')
# @login_required
def approve_claim():
    rch = dbh.reimburse_claims
    claim_list = rch.find({"status" : "verified"})

    return render_template('approve-claim.htm.j2', username="Mohammad Riftadi",
        email="riftadi@jawdat.com", claim_list=claim_list)

@app.route('/approve_claim/<claim_id>')
# @login_required
def approve_claim_id(claim_id):
    # check if admin
    rch = dbh.reimburse_claims
    date_approved = datetime.now()
    claim = rch.update_one({"_id" : ObjectId(claim_id)}, {"$set" :
        {"status" : "approved", "approval_date" : date_approved}})

    return jsonify({"approved" : True})


@app.route('/reject_claim/<claim_id>', methods=['POST'])
# @login_required
def reject_claim_id(claim_id):
    print request.form
    # check if admin
    rch = dbh.reimburse_claims

    claim = rch.update_one({"_id" : ObjectId(claim_id)}, {"$set" :
        {"status" : "rejected", "reject_msg" : request.form.get('reject_msg')}})

    return jsonify({"rejected" : True})

@app.route('/list_costcenter')
# @login_required
def list_costcenter():
    cch = dbh.costcenters
    rch = dbh.reimburse_claims

    cc_list = list(cch.find())
    cc_total_expense = {}

    for cc in cc_list:
        claim_list = rch.find({"status" : "approved",
            "expense_list.costcenter" : cc["costcenter_id"]})
        total_expense = 0
        for claim in claim_list:
            for exp in claim["expense_list"]:
                total_expense += exp["cost"]
        cc_total_expense[cc["costcenter_id"]] = total_expense

    return render_template('list-costcenter.htm.j2', username="Mohammad Riftadi",
        email="riftadi@jawdat.com", cc_list=cc_list, cc_total_expense=cc_total_expense)

@app.route('/create_costcenter', methods=['GET', 'POST'])
# @login_required
def create_costcenter():
    cch = dbh.costcenters

    if request.method == "POST":
        f = request.form
        user_input = {}

        user_input["costcenter_id"] = f.get("costcenter-id")
        user_input["costcenter_name"] = f.get("costcenter-name")
        user_input["costcenter_budget"] = int(strip_curr(f.get("costcenter-budget")))
        user_input["costcenter_status"] = f.get("costcenter-status")

        cc = cch.find_one({"costcenter_id" : user_input["costcenter_id"]})

        if cc:
            # cost center ID already exist
            return render_template('create-costcenter.htm.j2', username="Mohammad Riftadi",
                email="riftadi@jawdat.com", user_input=user_input)
        else:
            cch.insert_one(user_input)
            return redirect(url_for('list_costcenter'))

    return render_template('create-costcenter.htm.j2', username="Mohammad Riftadi",
        email="riftadi@jawdat.com")

@app.route('/close_costcenter/<cc_id>')
# @login_required
def close_costcenter(cc_id):
    cch = dbh.costcenters
    cch.update_one({"_id" : ObjectId(cc_id)},
        {"$set" : {"costcenter_status" : "closed"}})
    return jsonify({"closed" : True})

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
