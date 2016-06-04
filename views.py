#!/usr/bin/python
# by: Mohammad Riftadi <riftadi@jawdat.com>

import hashlib, json, os, random, string
from bson.objectid import ObjectId
from datetime import date, datetime, timedelta
from flask import Flask, abort, url_for, redirect, request, session, render_template, jsonify
# from flask_weasyprint import HTML, render_pdf
from functools import wraps
from pymongo import MongoClient
from Queue import Queue
from threading import Thread
import email, imaplib, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.message import MIMEMessage

client = MongoClient('mongodb://localhost:27017/')
dbh = client.jawdat_internal

app = Flask(__name__)
app.secret_key = 'Bgh3wtiA*(EG78wegBYt36BFYE7qg3fEFGG&31knj5e'

def logged_in(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login', next=request.path))

    return decorated_function

def process_config_queue(q):
    while True:
        recipient_list, subject, mail_text, mailer_from = q.get()

        con_flag = True

        IMAP_SERVER = 'imap.gmail.com'
        MAIL_USERNAME = 'no-reply@jawdat.com'
        MAIL_PASSWORD = 'H7sUB3hda8!x92d'

        rec_name_addr_list = []
        rec_addr_list = []
        for recipient in recipient_list:
            rec_name_addr_list.append("%s <%s>" % (recipient["name"], recipient["address"]))
            rec_addr_list.append(recipient["address"])
        recpt_to_string = ", ".join(rec_name_addr_list)

        smtph = smtplib.SMTP('smtp.gmail.com:587')
        #smtph.set_debuglevel(1)
        smtph.starttls()
        smtph.login(MAIL_USERNAME, MAIL_PASSWORD)

        new = MIMEMultipart("mixed")
        body = MIMEMultipart("alternative")
        msg = mail_text
        body.attach(MIMEText(msg, "plain"))
        #body.attach(MIMEText("<html>reply body text</html>", "html"))
        new.attach(body)

        new["Message-ID"] = email.utils.make_msgid()
        new["Subject"] = subject
        new["To"] = recpt_to_string
        new["From"] = mailer_from

        try:
            smtph.sendmail(new["From"], rec_addr_list, new.as_string())
            # print new
        except:
            print "Sending mail to %s failed..." % recpt_to_string

        smtph.quit()

        q.task_done()

def send_mail(recipient_list, subject, mail_text, mailer_from="JBot Expense Claim <no-reply@jawdat.com>"):
    cpeq = Queue(maxsize=0)
    worker = Thread(target=process_config_queue, args=(cpeq,))
    worker.setDaemon(True)
    worker.start()

    cpeq.put([recipient_list, subject, mail_text, mailer_from])

def strip_curr(curr_str):
    return filter(type(curr_str).isdigit, curr_str)

def convert_to_datetime(date_ind_string):
    day, month, year = [int(x) for x in date_ind_string.split('/')]
    return datetime(year, month, day)

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
    
    return "21 %s %s - 20 %s %s" % (prev_month_dict[per_str[:2]],
        first_year, month_dict[per_str[:2]], second_year)

def format_currency(amount):
    return "Rp %s,00" % format(amount, ',d').replace(',', '.')

@app.context_processor
def utility_processor():
    return dict(convert_period_to_text=convert_period_to_text)

@app.context_processor
def utility_processor():
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

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    eh = dbh.employees

    if request.method == "POST":
        f = request.form
        user = eh.find_one({"username" : f.get("username"),
            "secret" : hashlib.md5(f.get("password")).hexdigest()})
        if user:
            session['username'] = user['username']
            session['fullname'] = user['fullname']
            session['roles'] = user['roles']
            session['profpic'] = user.get('profpic')

            next = request.args.get('next')
            return redirect(next or url_for('list_claim'))
        else:
            return render_template('login.htm.j2', err=True,
                msg="Username and password do not match")

    return render_template('login.htm.j2')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/main')
@logged_in
def main():
    return render_template('index.htm.j2', fullname=session['fullname'],
        username=session['username'], profpic=session['profpic'], roles=session['roles'])

@app.route('/create_claim', methods=['GET', 'POST'])
@logged_in
def create_claim():
    eh = dbh.employees
    cch = dbh.costcenters
    rch = dbh.reimburse_claims

    employee = eh.find_one({"username" : session["username"]})
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
        qr = rch.find({"$and" : [{"username" : session["username"],
            "period" : p, "status" : {"$ne" : "rejected"}}]})
        if qr.count() == 0:
            periodlist.append(p)

    cclist = list(cch.find({"costcenter_status" : "active"}))

    return render_template('create-claim.htm.j2', fullname=session['fullname'],
        username=session['username'], profpic=session['profpic'],
        roles=session['roles'], empdetail=employee, supdetail=supervisor,
        periodlist=periodlist, cclist=cclist)

@app.route('/confirm_claim', methods=['POST'])
@logged_in
def confirm_claim():
    eh = dbh.employees
    cch = dbh.costcenters
    rch = dbh.reimburse_claims

    f = request.form
    expense_list = []
    subtotal = 0
    i = 0
    ccnamemap = {}

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

    return render_template('confirm-claim.htm.j2', fullname=session['fullname'],
        username=session['username'], profpic=session['profpic'], roles=session['roles'],
        empdetail=employee, supdetail=supervisor,
        claim=claim, ccnamemap=ccnamemap)

@app.route('/submit_claim', methods=['POST'])
@logged_in
def submit_claim():
    f = request.form
    rch = dbh.reimburse_claims
    sh = dbh.settings
    settings_dict = sh.find_one()

    username = f["employee-email"]
    fullname = f["employee-name"]
    period = f["period-normalized"]
    date_submitted = datetime.now()

    rch.update_one({"username" : username, "period" : period,
        "status" : "presubmitted"}, {"$set" : 
        {"status" : "submitted", "date_submitted" : date_submitted}})

    if settings_dict["email_notifications"] == "on":
        # send mail to accounting and the claimer
        recipient_list = [
            {"name": "Afilia Ratna", "address": "afilia@jawdat.com"},
            {"name": fullname, "address": username},
        ]
        subject = "[JBot] Expense Claim Submission"
        TEMPLATE = '''Dear %s,

%s has submitted an expense claim for period %s.
Please verify the expense claim.

On behalf of the claimer,
Jawdat Expense Reimbursement Bot
'''
        mail_text = TEMPLATE % ("Afilia Ratna", fullname, convert_period_to_text(period))
        send_mail(recipient_list, subject, mail_text)
    
    return redirect(url_for('list_claim'))

@app.route('/view_detail_claim/<claim_id>')
@logged_in
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
@logged_in
def generate_claim_report(claim_id):
    eh = dbh.employees
    cch = dbh.costcenters
    rch = dbh.reimburse_claims
    ccnamemap = {}

    employee = eh.find_one({"username" : session["username"]})
    supervisor = eh.find_one({"username" : employee["supervisor"]})
    costcenters = cch.find()

    for cc in costcenters:
        ccnamemap[cc["costcenter_id"]] = cc["costcenter_name"]

    claim = rch.find_one({"_id" : ObjectId(claim_id)})

    html = render_template('claim-printed-form.htm.j2', fullname=session['fullname'],
        username=session['username'], profpic=session['profpic'], roles=session['roles'],
        empdetail=employee, supdetail=supervisor,
        claim=claim, ccnamemap=ccnamemap)

    return html
    # return render_pdf(HTML(string=html))

@app.route('/cancel_claim', methods=['POST'])
@logged_in
def cancel_claim():
    f = request.form
    rch = dbh.reimburse_claims

    username = f["employee-email"]
    period = f["period-normalized"]

    rch.delete_many({"username" : username,
        "period" : period, "status" : "presubmitted"})

    return redirect(url_for('create_claim'))

@app.route('/list_claim')
@logged_in
def list_claim():
    rch = dbh.reimburse_claims
    claim_list = rch.find({"username" : session["username"], "$ne" : {"status" : "presubmitted"}})

    return render_template('list-claim.htm.j2', fullname=session['fullname'],
        username=session['username'], profpic=session['profpic'], roles=session['roles'], claim_list=claim_list)

@app.route('/list_all_claim')
@logged_in
def list_all_claim():
    rch = dbh.reimburse_claims
    claim_list = rch.find({"$ne" : {"status" : "presubmitted"}})

    return render_template('list-claim.htm.j2', fullname=session['fullname'],
        username=session['username'], profpic=session['profpic'], roles=session['roles'], claim_list=claim_list)

@app.route('/delete_claim/<claim_id>')
@logged_in
def delete_claim(claim_id):
    rch = dbh.reimburse_claims
    rch.delete_one({"_id" : ObjectId(claim_id)})
    return jsonify({"deleted" : True})

@app.route('/verify_claim')
@logged_in
def verify_claim():
    rch = dbh.reimburse_claims
    claim_list = rch.find({"status" : "submitted"})

    return render_template('verify-claim.htm.j2', fullname=session['fullname'],
        username=session['username'], profpic=session['profpic'], roles=session['roles'], claim_list=claim_list)

@app.route('/verify_claim/<claim_id>')
@logged_in
def verify_claim_id(claim_id):
    # check if accounting
    rch = dbh.reimburse_claims
    res = rch.update_one({"_id" : ObjectId(claim_id)}, {"$set" : {"status" : "verified"}})
    sh = dbh.settings
    settings_dict = sh.find_one()

    claim = rch.find_one({"_id" : ObjectId(claim_id)})

    if settings_dict["email_notifications"] == "on":
        # send mail to accounting and the claimer
        recipient_list = [
            {"name": "Tedhi Achdiana", "address": "tedhi@jawdat.com"},
            {"name": "Afilia Ratna", "address": "afilia@jawdat.com"},
            {"name": claim["fullname"], "address": claim["username"]},
        ]
        subject = "[JBot] Expense Claim Verified"
        TEMPLATE = '''Dear %s,

%s's expense claim for period %s has been verified by %s.
Total claim amount is %s.
Please approve the expense claim.

On behalf of the claimer,
Jawdat Expense Reimbursement Bot
'''
        mail_text = TEMPLATE % ("Tedhi Achdiana", claim["fullname"], \
            convert_period_to_text(claim["period"]), session['fullname'], \
            format_currency(claim["total"]))
        send_mail(recipient_list, subject, mail_text)

    return jsonify({"verified" : True})

@app.route('/approve_claim')
@logged_in
def approve_claim():
    rch = dbh.reimburse_claims
    claim_list = rch.find({"status" : "verified"})

    return render_template('approve-claim.htm.j2', fullname=session['fullname'],
        username=session['username'], profpic=session['profpic'], roles=session['roles'], claim_list=claim_list)

@app.route('/approve_claim/<claim_id>')
@logged_in
def approve_claim_id(claim_id):
    # check if admin
    rch = dbh.reimburse_claims
    date_approved = datetime.now()
    res = rch.update_one({"_id" : ObjectId(claim_id)}, {"$set" :
        {"status" : "approved", "approval_date" : date_approved}})
    sh = dbh.settings
    settings_dict = sh.find_one()

    claim = rch.find_one({"_id" : ObjectId(claim_id)})

    if settings_dict["email_notifications"] == "on":
        # send mail
        recipient_list = [
            {"name": "Tedhi Achdiana", "address": "tedhi@jawdat.com"},
            {"name": "Afilia Ratna", "address": "afilia@jawdat.com"},
            {"name": claim["fullname"], "address": claim["username"]},
        ]
        subject = "[JBot] Expense Claim Approved"
        TEMPLATE = '''Dear %s,

Your expense claim for period %s has been approved by %s.
Total claim amount is %s.

On behalf of Jawdat Management,
Jawdat Expense Reimbursement Bot
'''
        mail_text = TEMPLATE % (claim["fullname"], \
            convert_period_to_text(claim["period"]), session['fullname'], \
            format_currency(claim["total"]))
        send_mail(recipient_list, subject, mail_text)

    return jsonify({"approved" : True})


@app.route('/pay_claim')
@logged_in
def pay_claim():
    rch = dbh.reimburse_claims
    claim_list = rch.find({"status" : "approved"})

    return render_template('pay-claim.htm.j2', fullname=session['fullname'],
        username=session['username'], profpic=session['profpic'], roles=session['roles'], claim_list=claim_list)

@app.route('/pay_claim/<claim_id>')
@logged_in
def pay_claim_id(claim_id):
    # check if admin
    rch = dbh.reimburse_claims
    date_paid = datetime.now()
    res = rch.update_one({"_id" : ObjectId(claim_id)}, {"$set" :
        {"status" : "paid", "payment_date" : date_paid}})
    sh = dbh.settings
    settings_dict = sh.find_one()

    claim = rch.find_one({"_id" : ObjectId(claim_id)})

    if settings_dict["email_notifications"] == "on":
        # send mail
        recipient_list = [
            {"name": "Tedhi Achdiana", "address": "tedhi@jawdat.com"},
            {"name": "Afilia Ratna", "address": "afilia@jawdat.com"},
            {"name": claim["fullname"], "address": claim["username"]},
        ]
        subject = "[JBot] Expense Claim Paid"
        TEMPLATE = '''Dear %s,

Your expense claim for period %s has been paid by %s.
Total amount paid is %s.

On behalf of Jawdat Management,
Jawdat Expense Reimbursement Bot
'''
        mail_text = TEMPLATE % (claim["fullname"], \
            convert_period_to_text(claim["period"]), session['fullname'], \
            format_currency(claim["total"]))
        send_mail(recipient_list, subject, mail_text)

    return jsonify({"paid" : True})

@app.route('/reject_claim/<claim_id>', methods=['POST'])
@logged_in
def reject_claim_id(claim_id):
    print request.form
    # check if admin
    rch = dbh.reimburse_claims

    res = rch.update_one({"_id" : ObjectId(claim_id)}, {"$set" :
        {"status" : "rejected", "reject_msg" : request.form.get('reject_msg')}})

    claim = rch.find_one({"_id" : ObjectId(claim_id)})
    sh = dbh.settings
    settings_dict = sh.find_one()

    if settings_dict["email_notifications"] == "on":
        # send mail
        recipient_list = [
            {"name": "Tedhi Achdiana", "address": "tedhi@jawdat.com"},
            {"name": "Afilia Ratna", "address": "afilia@jawdat.com"},
            {"name": claim["fullname"], "address": claim["username"]},
        ]
        subject = "[JBot] Expense Claim Rejection"
        TEMPLATE = '''Dear %s,

Your expense claim for period %s has been rejected by %s.
Message from %s: %s

On behalf of Jawdat Management,
Jawdat Expense Reimbursement Bot
    '''
        mail_text = TEMPLATE % (claim["fullname"], convert_period_to_text(claim["period"]), \
            session['fullname'], session['fullname'], request.form.get('reject_msg'))
        send_mail(recipient_list, subject, mail_text)

    return jsonify({"rejected" : True})


@app.route('/medical_summary')
@logged_in
def medical_summary():
    eh = dbh.employees
    rch = dbh.reimburse_claims

    year = datetime.now().year
    emp_list = list(eh.find())
    emp_medical_expense = {}
    year = date.today().year

    for emp in emp_list:
        claim_list = rch.find({"username" : emp["username"],
            "status" : "approved",
            "expense_list.category" : "medical"})
        total_expense = 0
        for claim in claim_list:
            for exp in claim["expense_list"]:
                if exp["category"] == "medical":
                    total_expense += exp["cost"]
        emp_medical_expense[emp["username"]] = total_expense

    return render_template('medical-summary.htm.j2', fullname=session['fullname'],
        username=session['username'], profpic=session['profpic'], roles=session['roles'],
        emp_list=emp_list, emp_medical_expense=emp_medical_expense, year=year)

@app.route('/list_costcenter')
@logged_in
def list_costcenter():
    cch = dbh.costcenters
    rch = dbh.reimburse_claims

    cc_list = list(cch.find())
    cc_total_expense = {}

    for cc in cc_list:
        claim_list = rch.find({"$or" : [{"status" : "approved"}, {"status" : "paid"}],
            "expense_list.costcenter" : cc["costcenter_id"]})
        total_expense = 0
        for claim in claim_list:
            for exp in claim["expense_list"]:
                if exp["costcenter"] == cc["costcenter_id"]:
                    total_expense += exp["cost"]
        cc_total_expense[cc["costcenter_id"]] = total_expense

    return render_template('list-costcenter.htm.j2', fullname=session['fullname'],
        username=session['username'], profpic=session['profpic'], roles=session['roles'],
        cc_list=cc_list, cc_total_expense=cc_total_expense)

@app.route('/create_costcenter', methods=['GET', 'POST'])
@logged_in
def create_costcenter():
    cch = dbh.costcenters

    if request.method == "POST":
        f = request.form
        user_input = {}

        user_input["costcenter_id"] = f.get("costcenter-id")
        user_input["costcenter_name"] = f.get("costcenter-name")
        user_input["costcenter_budget"] = int(strip_curr(f.get("costcenter-budget")))
        user_input["costcenter_category"] = f.get("costcenter-category")
        user_input["costcenter_status"] = f.get("costcenter-status")

        cc = cch.find_one({"costcenter_id" : user_input["costcenter_id"]})

        if cc:
            # cost center ID already exist
            return render_template('create-costcenter.htm.j2', fullname=session['fullname'],
        username=session['username'], profpic=session['profpic'], roles=session['roles'], user_input=user_input)
        else:
            cch.insert_one(user_input)
            return redirect(url_for('list_costcenter'))

    return render_template('create-costcenter.htm.j2', fullname=session['fullname'],
        username=session['username'], profpic=session['profpic'], roles=session['roles'])

@app.route('/close_costcenter/<cc_id>')
@logged_in
def close_costcenter(cc_id):
    cch = dbh.costcenters
    cch.update_one({"_id" : ObjectId(cc_id)},
        {"$set" : {"costcenter_status" : "closed"}})
    return jsonify({"closed" : True})

@app.route('/basic_settings', methods=['GET', 'POST'])
@logged_in
def basic_settings():
    sh = dbh.settings
    email_notifications = ""

    if request.method == "POST":
        f = request.form
        if f.get("email-notifications"):
            email_notifications = "on"
        else:
            email_notifications = "off"

        sh.update_one({}, {"$set" : {"email_notifications" : email_notifications}})

    settings_dict = sh.find_one()

    return render_template('basic-settings.htm.j2', fullname=session['fullname'],
        username=session['username'], profpic=session['profpic'], roles=session['roles'],
        settings_dict=settings_dict)

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == "POST":
        f = request.form
        username = f.get("user-email")

        eh = dbh.employees
        emp = eh.find_one({"username" : username})
        if emp:
            reset_url = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(80))
            now = datetime.now()
            next15minutes = now + timedelta(minutes = 15)

            rph = dbh.resetpass
            rph.insert_one({"username" : username, "reset_url" : reset_url,
                "valid_until" : next15minutes, "used" : False})

            goto_url =  "%srpext/%s" % (request.url_root, reset_url)

            # send mail
            recipient_list = [
                {"name": emp["fullname"], "address": emp["username"]},
            ]
            subject = "[JBot] Reset Password"
            TEMPLATE = '''Dear %s,

Please reset your password here:

%s

The URL above is only valid for the next 15 minutes.

Bip bip bep bop,
Jawdat Expense Reimbursement Bot
'''
            mail_text = TEMPLATE % (emp["fullname"], goto_url)
            send_mail(recipient_list, subject, mail_text)

            return render_template('reset-password.htm.j2',
                msg="Proceed to your e-mail inbox", redirect=url_for('login'))
        else:
            return render_template('reset-password.htm.j2', err=True,
                msg="Username is not found")

    return render_template('reset-password.htm.j2')

@app.route('/rpext/<reset_url>', methods=['GET', 'POST'])
def rpext(reset_url):
    if request.method == "POST":
        f = request.form
        new_password = f.get("new-password")
        confirm_new_password = f.get("confirm-new-password")

        if new_password == confirm_new_password:
            rph = dbh.resetpass
            now = datetime.now()
            reset = rph.find_one({"reset_url" : reset_url, "valid_until" : {"$gt": now}})

            eh = dbh.employees
            emp = eh.update_one({"username" : reset["username"]},
                {"$set" : {"secret" : hashlib.md5(new_password).hexdigest()}})

            rph.delete_one({"reset_url" : reset_url})

            return render_template('create-new-password.htm.j2',
                msg="Password is changed", redirect=url_for('login'))
        else:
            return render_template('create-new-password.htm.j2',
                err=True, msg="Passwords do not match!")

    rph = dbh.resetpass
    now = datetime.now()
    reset = rph.find_one({"reset_url" : reset_url, "valid_until" : {"$gt": now}})

    if reset:
        return render_template('create-new-password.htm.j2')
    else:
        abort(401)

app.run(debug=True, host="0.0.0.0", port=5000, threaded=True)
