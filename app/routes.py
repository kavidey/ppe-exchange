from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from werkzeug import secure_filename
from app import app, db, crypto, email
from app.forms import LoginForm, RegistrationForm, VerifyForm, ChangePassword, ResetPassword, EditUserProfileForm
from app.models import User, PPE, Hospital, Wants, Has, Exchanges, Exchange, EXCHANGE_COMPLETE, EXCHANGE_COMPLETE_TEXT, EXCHANGE_COMPLETE_ADMIN, EXCHANGE_COMPLETE_ADMIN_TEXT, EXCHANGE_COMPLETE_HOSPITAL_CANCELED, EXCHANGE_COMPLETE_HOSPITAL_CANCELED_TEXT, EXCHANGE_COMPLETE_ADMIN_CANCELED, EXCHANGE_COMPLETE_ADMIN_CANCELED_TEXT, EXCHANGE_UNVERIFIED, EXCHANGE_UNVERIFIED_TEXT, EXCHANGE_IN_PROGRESS, EXCHANGE_IN_PROGRESS_TEXT, EXCHANGE_NOT_ACCEPTED, EXCHANGE_ACCEPTED_NOT_SHIPPED, EXCHANGE_ACCEPTED_SHIPPED, EXCHANGE_ACCEPTED_RECEIVED, EXCHANGE_HOSPITAL_CANCELED, EXCHANGE_ADMIN_CANCELED, EXCHANGE_ADMIN_NOT_VERIFIED
from app import crypto
from app import email
from datetime import datetime
from sqlalchemy import desc, and_, or_, asc
from sqlalchemy.orm import contains_eager

import json
import os
import math
import inspect


import logging
logging.basicConfig()
# logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

@app.route('/')
@app.route('/index')
@login_required
def index():

    # user --> row for this user
    user = User.query.\
        filter_by(username=current_user.username).\
        join(Hospital).\
        options(contains_eager(User.hospital)).\
        first()

    if user.is_admin:
        return render_template('admin_index.html', title='Home')
    elif not user.is_verified:
        return render_template("404.html")

    # ppe_types --> 
    ppe_types = PPE.query.\
        outerjoin(Wants, and_(Wants.hospital_id == user.hospital.id, Wants.ppe_id == PPE.id)).\
        outerjoin(Has, and_(Has.hospital_id == user.hospital.id, Has.ppe_id == PPE.id)).\
        options(contains_eager(PPE.wants)).\
        options(contains_eager(PPE.has)).\
        all()

        # filter(or_(Exchange.hospital1==user.hospital.id, Exchange.hospital2 == user.hospital.id)).\
    exchange_subquery = Exchange.query.\
        join(PPE).\
        join(Hospital, or_(Exchange.hospital1 == Hospital.id, Exchange.hospital2 == Hospital.id)).\
        options(contains_eager(Exchange.ppe_ref)).\
        options(contains_eager(Exchange.hospital1_ref)).\
        options(contains_eager(Exchange.hospital2_ref)).\
        subquery()
    
    exchanges = Exchanges.query.\
        filter(Exchanges.status.in_([EXCHANGE_COMPLETE_HOSPITAL_CANCELED, EXCHANGE_COMPLETE_ADMIN_CANCELED, EXCHANGE_COMPLETE, EXCHANGE_COMPLETE_ADMIN, EXCHANGE_IN_PROGRESS, EXCHANGE_UNVERIFIED])).\
        join(exchange_subquery, Exchange.exchange_id == Exchanges.id).\
        options(contains_eager(Exchanges.exchange)).\
        order_by(Exchanges.id.asc()).\
        all()

    # print(exchanges)

    items = { 'actionable': [], 'pending': [], 'complete': [] }
    for ex in exchanges:
        status = 'pending'
        found_incompleteness = False

        # FIXME: I can't figure out how to do an SQL filter on Exchanges that determines if any
        #        Exchange references this hospital. So, right now, we return *all* the exchanges
        #        in the entire system and loop through them here. THIS IS BAD.
        found_user = False

        for inner in ex.exchange:
            if user.hospital.id != inner.hospital1 and user.hospital.id != inner.hospital2:
                continue
            found_user = True
            actionable = False

            if user.hospital.id == inner.hospital1:
                actionable = (
                    (
                        (inner.status == EXCHANGE_NOT_ACCEPTED or ex.status == EXCHANGE_UNVERIFIED) and
                        not inner.is_h1_verified
                    ) or
                    (
                        (
                            (inner.is_h1_verified and inner.is_h2_verified) or
                            inner.status == EXCHANGE_ACCEPTED_NOT_SHIPPED
                        ) and
                        not inner.is_h1_shipped
                    )
                )
            elif user.hospital.id == inner.hospital2:
                actionable = (
                    (
                        (inner.status == EXCHANGE_NOT_ACCEPTED or ex.status == EXCHANGE_UNVERIFIED) and
                        not inner.is_h2_verified
                    ) or
                    (
                        (inner.is_h1_shipped or inner.status == EXCHANGE_ACCEPTED_SHIPPED) and
                        not inner.is_h2_received
                    )
                )

            # These are the only states which permit `inner` to be actionable
            if inner.status in [EXCHANGE_NOT_ACCEPTED, EXCHANGE_ACCEPTED_NOT_SHIPPED, EXCHANGE_ACCEPTED_SHIPPED] and not inner.is_h2_received:
                found_incompleteness = True
                if actionable:
                    status = 'actionable'

        # If it's any of these four statuses, we overrule everything else to say it's complete
        if not found_incompleteness or ex.status in [EXCHANGE_COMPLETE, EXCHANGE_COMPLETE_ADMIN, EXCHANGE_COMPLETE_HOSPITAL_CANCELED, EXCHANGE_COMPLETE_ADMIN_CANCELED]:
            status = 'complete'

        if found_user:
            # reordering swaps so that swaps that include this hospital come first
            includes_me = []
            not_includes_me = []
            for inner in ex.exchange:
                if inner.hospital1 == user.hospital.id or inner.hospital2 == user.hospital.id:
                    includes_me.append(inner)
                else:
                    not_includes_me.append(inner)
            ex.exchange = includes_me + not_includes_me
            items[status].append(ex)
 
    return render_template('index.html', title='Home', user=user, ppe_types=ppe_types, exchanges=items)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    form.hospital_name.choices = [(h.id, h.name) for h in Hospital.query.all() if h.name != "admin"]
    if form.validate_on_submit():
        user = User(username=form.username.data,
                    email=form.email.data,
                    is_admin=False,
                    is_verified=False,
                    hospital_street=form.street.data,
                    hospital_city=form.city.data,
                    hospital_state=form.state.data,
                    hospital_zipcode=form.zipcode.data,
                    hospital_contact=form.contact.data,
                    hospital_id=form.hospital_name.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user! Please wait for the admin to verify your account to access this site. You should recieve a verification email shortly')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/edit_user_profile', methods=['GET', 'POST'])
def edit_user_profile():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    form = EditUserProfileForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=current_user.username).first()
        user.email = form.email.data
        user.hospital_contact = form.contact.data
        user.username = form.username.data
        
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit_user_profile.html', title='Edit User Profile', form=form, current_user=current_user)

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if not current_user.is_authenticated:
        return redirect(url_for('login',next='/verify?key='+request.args.get("key")))

    user = User.query.filter_by(username=current_user.username).first()
    if request.args.get("key") == user.verification_key and user.verification_key != "":
        form = VerifyForm()
        if form.validate_on_submit():
            # Mark user as verified
            q = db.session.query(User)
            q = q.filter(User.id == user.id)
            record = q.first()
            record.is_verified = True
            record.verification_key = None
            db.session.commit()

            flash('Congratulations, you are now a verified user!')
            return redirect(url_for('index'))
        return render_template('verify.html', title='Verify', form=form)
    elif user.is_verified:
        return redirect(url_for("index"))
    else:
        return render_template('404.html')

@app.route('/wants', methods=['GET', 'POST'])
def wants():
    return redirect(url_for('index'))

@app.route('/has', methods=['GET', 'POST'])
def has():
    return redirect(url_for('index'))


@app.route('/update-ppe/<name>', methods=['POST'])
def update_ppe(name):
    if not current_user.is_authenticated:
        return redirect(url_for("login", next="/"))
    
    Model = None

    if name == "wants":
        Model = Wants
    elif name == "has":
        Model = Has
    else:
        return 404

    OtherModel = Has if Model is Wants else Wants
    
    user = User.query.filter_by(username=current_user.username).first()
    user_hospital = Hospital.query.filter_by(id=user.hospital_id).first()

    for key, quantity in request.form.items():
        # key format is in ppe-XX for quantities, so make sure we're looking at the right thing.
        if not key[:4] == "ppe-": continue
        ppe_id = key[4:]
        quantity = int(quantity)

        current = Model.query.filter_by(hospital_id=user_hospital.id, ppe_id=ppe_id).first()

        if quantity != 0:
            other = OtherModel.query.filter_by(hospital_id=user_hospital.id, ppe_id=ppe_id).first()
            if other is not None: db.session.delete(other)

        if current is None:
            if quantity == 0: continue # don't need to add a nonexistant entry
            db.session.add(Model(hospital_id=user_hospital.id, ppe_id=ppe_id, count=quantity))
        elif quantity == 0:
            db.session.delete(current)
        else:
            current.count = quantity

    db.session.commit()
    return redirect(url_for('index'))

@app.route('/update_want_need', methods=['GET', 'POST'])
def update_want_need():
    data = json.loads(request.get_data())
    if not current_user.is_authenticated:
        return jsonify(target="login?next="+data['state'])
    
    user = User.query.filter_by(username=current_user.username).first()
    user_hospital = Hospital.query.filter_by(id=user.hospital_id).first()

    if data["state"] == "wants":
        q = db.session.query(Wants)
        for item in data["items"]:
            ppe_id = PPE.query.filter_by(sku=item["sku"]).first().id

            old_count = 0
            count_query = Wants.query.filter_by(hospital_id=user_hospital.id, ppe_id=ppe_id).first()
            if count_query:
                old_count = count_query.count
            
            if old_count > 0 and item["count"] > 0:
                f = q.filter(Wants.ppe_id == ppe_id)
                record = f.first()
                record.count = item["count"]
            elif old_count > 0 and item["count"] == 0:
                Wants.query.filter_by(hospital_id=user_hospital.id, ppe_id=ppe_id).delete()
            elif old_count == 0 and item["count"] > 0:
                w = Wants(hospital_id=user_hospital.id, ppe_id=ppe_id, count=item["count"])
                db.session.add(w)
        db.session.commit()
    elif data["state"] == "has":
        q = db.session.query(Has)
        for item in data["items"]:
            ppe_id = PPE.query.filter_by(sku=item["sku"]).first().id

            old_count = 0
            count_query = Has.query.filter_by(hospital_id=user_hospital.id, ppe_id=ppe_id).first()
            if count_query:
                old_count = count_query.count
            
            if old_count > 0 and item["count"] > 0:
                f = q.filter(Has.ppe_id == ppe_id)
                record = f.first()
                record.count = item["count"]
            elif old_count > 0 and item["count"] == 0:
                Has.query.filter_by(hospital_id=user_hospital.id, ppe_id=ppe_id).delete()
            elif old_count == 0 and item["count"] > 0:
                h = Has(hospital_id=user_hospital.id, ppe_id=ppe_id, count=item["count"])
                db.session.add(h)
        db.session.commit()
    return jsonify(target=data['state'])

@app.route('/admin_sku', methods=['GET', 'POST'])
def admin_sku():
    if (not current_user.is_authenticated) or (not User.query.filter_by(username=current_user.username).first().is_admin):
        return redirect(url_for('login',next='/admin_sku'))

    skus = PPE.query.all()
    items = []
    for item in skus:

        ha = []
        for have in Has.query.filter_by(ppe_id=item.id):
            hosp = Hospital.query.filter_by(id=have.hospital_id).first()
            ha.append({
                "hospital": hosp.name,
                "count": have.count,
            })
        wa = []
        for want in Wants.query.filter_by(ppe_id=item.id):
            hosp = Hospital.query.filter_by(id=want.hospital_id).first()
            wa.append({
                "hospital": hosp.name,
                "count": want.count
            })

        items.append({
            "sku": item.sku,
            "desc": item.desc,
            "manufacturer": item.manu,
            "img": item.img.decode(),
            "haves": ha,
            "wants": wa
        })
    return render_template('admin_sku.html', title='Have', items=items)

@app.route('/update_admin_sku', methods=['GET', 'POST'])
def update_admin_sku():
    data = json.loads(request.get_data())
    if not current_user.is_authenticated:
        return jsonify(target="login?next="+data['state'])
    if data["task"] == "add":
        q = PPE.query.filter_by(sku = data["sku"])
        if q.count() > 0:
            return "SKU already exists"
        else:
            p = PPE(sku=data["sku"], desc=data["desc"], img=str.encode(data["img"]), manu=data["manu"])
            db.session.add(p)
            db.session.commit()
    elif data["task"] == "remove":
        PPE.query.filter_by(sku=data["sku"]).delete()
        db.session.commit()
    elif data["task"] == "edit":
        q = db.session.query(PPE)
        q = q.filter(PPE.sku == data["sku"])
        record = q.first()
        record.desc = data["desc"]
        record.img = str.encode(data["img"])
        record.manu = data["manu"]
        db.session.commit()
    return jsonify(target="index")

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    form  = ChangePassword()
    if current_user.is_authenticated:
        user = User.query.filter_by(username=current_user.username).first()
        if form.validate_on_submit():
            user.set_password(form.password.data)
            user.password_reset_key = ""
            db.session.commit()
            flash('Password succesfully updated')
            return redirect(url_for('index'))
        return render_template('change_password.html', title='Change Password', form=form)
        
    else:
        user = User.query.filter_by(password_reset_key=request.args.get("key")).first()
        
        if user is not None and request.args.get("key") != "":
            
            if form.validate_on_submit():
                user.set_password(form.password.data)
                user.password_reset_key = ""
                db.session.commit()
                flash('Password succesfully updated')
                return redirect(url_for('login'))
            return render_template('change_password.html', title='Change Password', form=form)
        else:
            return render_template('404.html')

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    form  = ResetPassword()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        key = crypto.generate_key()
        user.password_reset_key = key
        db.session.commit()
        
        email.send_reset_password(app.config.get("PPE_HOSTNAME"), user.email, key, user.username)
        flash('You should recieve an email with instructions on how to reset your password soon')
        return redirect(url_for('login'))
    return render_template('reset_password.html', title='Reset Password', form=form)

@app.route('/admin_users', methods=['GET', 'POST'])
def admin_users():
    if (not current_user.is_authenticated) or (not User.query.filter_by(username=current_user.username).first().is_admin):
        return redirect(url_for('login',next='/admin_users'))
    
    users = User.query.all()
    items = []
    for user in users:
        user_hospital = Hospital.query.filter_by(id=user.hospital_id).first()
        item = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "hospital": "N/A",
            "contact": "N/A",
            "address": "N/A",
            "is_verified": user.is_verified,
            "verification_pending": user.verification_key is not None,
            "is_admin": user.is_admin
        }
        if user_hospital is not None and not user.is_admin:
            item["hospital"] = user_hospital.name
            item["contact"] = user.hospital_contact
            item["address"] = user.hospital_street + ", " + user.hospital_city + ", " + user.hospital_state + " " + user.hospital_zipcode
        items.append(item)
    return render_template('admin_users.html', title='Users Dashboard', users=items)


@app.route('/update_admin_users', methods=['GET', 'POST'])
def update_admin_users():
    data = json.loads(request.get_data())
    if not current_user.is_authenticated:
        return jsonify(target="login?next="+data['state'])
    if data["task"] == "remove":
        User.query.filter_by(id=data["user_id"]).delete()
        db.session.commit()
    elif data["task"] == "verify":
        # Set user as generate verification key for user
        q = db.session.query(User)
        q = q.filter(User.id == data["user_id"])
        record = q.first()
        record.is_verified = False
        key = crypto.generate_key()
        record.verification_key = key

        # Update hospitals database
        user = User.query.filter_by(id=data["user_id"]).first()
        q = db.session.query(Hospital)
        q = q.filter(Hospital.id == user.hospital_id)
        record = q.first()
        record.contact = user.hospital_contact
        record.street = user.hospital_street
        record.city = user.hospital_city
        record.state = user.hospital_state
        record.zipcode = user.hospital_zipcode
        
        db.session.commit()

        email.send_user_verification(
            User.query.filter_by(id=data["user_id"]).first().username,
            key,
            app.config.get("PPE_HOSTNAME"),
            User.query.filter_by(id=data["user_id"]).first().email)
        
    elif data["task"] == "cancel":
        q = db.session.query(User)
        q = q.filter(User.id == data["user_id"])
        record = q.first()
        record.is_verified = False
        record.verification_key = None
        db.session.commit()
    return jsonify(target="index")


@app.route('/admin_hospitals', methods=['GET', 'POST'])
def admin_hospitals():
    if (not current_user.is_authenticated) or (not User.query.filter_by(username=current_user.username).first().is_admin):
        return redirect(url_for('login',next='/admin_hospitals'))

    hospitals = Hospital.query.all()
    items = []
    for item in hospitals:
        if item.name != "admin":
            print("id",item.id,"credit",item.credit)
            ha = []
            for have in Has.query.filter_by(hospital_id=item.id):
                ppe = PPE.query.filter_by(id=have.ppe_id).first()
                ha.append({
                    "ppe": ppe.sku,
                    "tooltip": ppe.manu + " " + ppe.desc,
                    "count": have.count,
                    "img": ppe.img.decode()
                })
            wa = []
            for want in Wants.query.filter_by(hospital_id=item.id):
                ppe = PPE.query.filter_by(id=want.ppe_id).first()
                wa.append({
                    "ppe": ppe.sku,
                    "tooltip": ppe.manu + " " + ppe.desc,
                    "count": want.count,
                    "img": ppe.img.decode()
                })
            items.append({
                "id": item.id,
                "name": item.name,
                "address": item.street+", "+item.city+", "+item.state+", "+item.zipcode,
                "credit": item.credit,
                "haves": ha,
                "wants": wa
            })
    return render_template('admin_hospitals.html', items=items)

@app.route('/update_admin_hospital', methods=['GET', 'POST'])
def update_admin_hospital():
    data = json.loads(request.get_data())
    if not current_user.is_authenticated:
        return jsonify(target="login?next=admin_hospital")
    if data["task"] == "add":
        q = Hospital.query.filter_by(name = data["name"])
        if q.count() > 0:
            return "Hospital already exists"
        else:
            h = Hospital(name=data["name"])
            db.session.add(h)
            db.session.commit()
    elif data["task"] == "remove":
        Hospital.query.filter_by(id=data["id"]).delete()
        db.session.commit()
    elif data["task"] == "edit":
        q = db.session.query(Hospital)
        q = q.filter(Hospital.id == data["id"])
        record = q.first()
        record.name = data["name"]
        db.session.commit()
    return jsonify(target="index")

@app.route('/admin_exchange', methods=['GET', 'POST'])
def admin_exchange():
    if (not current_user.is_authenticated) or (not User.query.filter_by(username=current_user.username).first().is_admin):
        return redirect(url_for('login',next='/admin_exchange'))
    
    exchanges = Exchanges.query.order_by(desc(Exchanges.updated_timestamp)).all()
    print(len(exchanges))
    items = []
    for ex in exchanges:
        its = []
        exchange = Exchange.query.filter_by(exchange_id=ex.id)
        
        stat = ""
        if ex.status==EXCHANGE_COMPLETE:
            stat=EXCHANGE_COMPLETE_TEXT
        elif ex.status==EXCHANGE_COMPLETE_ADMIN:
            stat=EXCHANGE_COMPLETE_ADMIN_TEXT
        elif ex.status==EXCHANGE_COMPLETE_HOSPITAL_CANCELED:
            stat=EXCHANGE_COMPLETE_HOSPITAL_CANCELED_TEXT
        elif ex.status==EXCHANGE_COMPLETE_ADMIN_CANCELED:
            stat=EXCHANGE_COMPLETE_ADMIN_CANCELED_TEXT
        elif ex.status==EXCHANGE_IN_PROGRESS:
            stat=EXCHANGE_IN_PROGRESS_TEXT
        elif ex.status==EXCHANGE_UNVERIFIED:
            stat=EXCHANGE_UNVERIFIED_TEXT

        for x in exchange:
            ppe = PPE.query.filter_by(id = x.ppe).first()
            i = {
                "h1": Hospital.query.filter_by(id = x.hospital1).first().name,
                "h2": Hospital.query.filter_by(id = x.hospital2).first().name,
                "ppe": ppe.sku,
                "count": x.count,
                "tooltip": ppe.manu + " " + ppe.desc,
                "img": ppe.img.decode()
            }
            its.append(i)
        item = {
            "id": ex.id,
            "created_timestamp": ex.created_timestamp,
            "updated_timestamp": ex.updated_timestamp,
            "exchanges": its,
            "status": ex.status,
            "status_text": stat
        }
        items.append(item)
    return render_template('admin_exchange.html', title='Exchanges Dashboard', exchanges=items)

@app.route('/update_admin_exchanges', methods=['GET', 'POST'])
def update_admin_exchanges():
    data = json.loads(request.get_data())
    print(data)
    if not current_user.is_authenticated:
        return jsonify(target="login?next="+data['state'])
    if data["task"] == "cancel":
        q = db.session.query(Exchanges)
        q = q.filter(Exchanges.id==(int(data["exchange_id"])))
        record = q.first()
        record.status = EXCHANGE_COMPLETE_ADMIN_CANCELED
        record.updated_timestamp = datetime.now()
        exchange = Exchange.query.filter_by(exchange_id=int(data["exchange_id"]))

        h_list = []
        for x in exchange:
            h_list.append(x.hospital1)
            h_list.append(x.hospital2)
            x.status=EXCHANGE_ADMIN_CANCELED
        
        h_list = list(set(h_list))

        for hid in h_list:
            h_user = User.query.filter_by(hospital_id=hid).first()
            email.send_hospital_admin_canceled(
                h_user.username,
                app.config.get("PPE_HOSTNAME"),
                h_user.email,
                data["exchange_id"])
        db.session.commit()
    elif data["task"] == "cancel_pre_verify":
        q = Exchanges.query.filter_by(id=int(data["exchange_id"])).first()
        q.status = EXCHANGE_COMPLETE_ADMIN_CANCELED
        q.updated_timestamp = datetime.now()
        exchange = Exchange.query.filter_by(exchange_id=int(data["exchange_id"]))
        for x in exchange:
            x.status=EXCHANGE_ADMIN_CANCELED
            # undo has and wants
            transfer = x.count
            has = Has.query.filter_by(hospital_id=x.hospital1)\
                .filter_by(ppe_id=x.ppe).first()
            has.count += transfer
            wants = Wants.query.filter_by(hospital_id=x.hospital2)\
                .filter_by(ppe_id=x.ppe).first()
            wants.count += transfer

            # undo credit transfers
            tx = Hospital.query.filter_by(id=x.hospital1).first()
            tx.credit -= transfer

            rx = Hospital.query.filter_by(id=x.hospital2).first()
            rx.credit += transfer
        db.session.commit()
    elif data["task"] == "verify":
        q = db.session.query(Exchanges)
        q = q.filter(Exchanges.id==(int(data["exchange_id"])))
        record = q.first()
        record.status = EXCHANGE_UNVERIFIED
        record.updated_timestamp = datetime.now()
        db.session.commit()

        # send email to all unique hospitals in newly verified exchange
        h_list = []
        # get all hospitals in newly verified exchange
        xs = Exchange.query.filter_by(exchange_id=(int(data["exchange_id"])))
        for x in xs:
            h_list.append(x.hospital1)
            h_list.append(x.hospital2)
        
        # only keep the unique ones
        unique_h_list = list(set(h_list))
        
        for h in unique_h_list:
                email.send_hospital_exchange_creation(
                    User.query.filter_by(hospital_id=h).first().username,
                    app.config.get("PPE_HOSTNAME"),
                    User.query.filter_by(hospital_id=h).first().email,
                    data["exchange_id"])
        
    return jsonify(target="index")

@app.route('/exchanges', methods=['GET', 'POST'])
def exchanges():
    return redirect(url_for('index'))

# exchanges logic
# loop through exchanges
#   find ones that have this user's hospital id somewhere in the linked exchange --> grab whole "exchanges"
#   exchange id --> exchanges.id
#   when created --> exchanges.creation_timestamp
#   when updated --> exchanges.updated_timestamp
#   loop through exchanges
#     print out exchange
#     print out status
#     depending on status, show optional button

# Exchange ID   when created    when updated    exchange part 1     status part 1: optional button (verify/shipped/received)
#                                               exchange part 2     status part 2: optional button
#                                               ...                 ...

@app.route('/update_exchange', methods=['GET', 'POST'])
def update_exchange():
    data = json.loads(request.get_data())
    if not current_user.is_authenticated:
        return jsonify(target="login?next="+data['state'])
    hospital_id = User.query.filter_by(username=current_user.username).first().hospital_id
    if not (hospital_id == int(data["hospital_id"])):
        return jsonify(target="login")
        
    if data["task"] == "verify":
        # get all swaps that match this exchange id
        exchanges = db.session.query(Exchange).filter_by(exchange_id=int(data["exchange_id"]))
        eid = -1
        try:
            eid = int(data['e_id'])
        except:
            pass
        if eid >= 0:
            exchanges = exchanges.filter_by(id=eid) 

        # loop through swaps
        for ex in exchanges:
            # if hospital1 just verified
            if ex.hospital1 == int(data["hospital_id"]):
                ex.updated_timestamp=datetime.now()
                ex.is_h1_verified = True
                # if both members of 
                if ex.is_h1_verified and ex.is_h2_verified:
                    ex.status = EXCHANGE_ACCEPTED_NOT_SHIPPED
            elif ex.hospital2 == int(data["hospital_id"]):
                ex.updated_timestamp=datetime.now()
                ex.is_h2_verified = True
                if ex.is_h1_verified and ex.is_h2_verified:
                    ex.status = EXCHANGE_ACCEPTED_NOT_SHIPPED            

        done = True # are all the swaps verified?
        for ex in exchanges:
            if not (ex.is_h1_verified and ex.is_h2_verified):
                print(ex.is_h1_verified, ex.is_h2_verified)
                done = False
        print(int(data["hospital_id"]),done)
        if done:
            e = db.session.query(Exchanges).filter_by(id=int(data["exchange_id"])).first()
            e.updated_timestamp=datetime.now()
            e.status=EXCHANGE_IN_PROGRESS
            # send email to all unique hospitals in newly verified exchange
            h_list = []
            # get all hospitals in newly verified exchange
            xs = Exchange.query.filter_by(exchange_id=(int(data["exchange_id"])))

            # 1 is sending 2 is receiving
            for x in xs:
                shipping_user = User.query.filter_by(hospital_id=x.hospital1).first()
                receiving_hospital = Hospital.query.filter_by(id=x.hospital2).first()
                email.send_hospital_exchange_verified_ship_address(shipping_user.username,
                    app.config.get("PPE_HOSTNAME"),
                    shipping_user.email,
                    data["exchange_id"],
                    x.count,
                    PPE.query.filter_by(id=x.ppe).first().sku,
                    [receiving_hospital.street, receiving_hospital.city, receiving_hospital.state, receiving_hospital.zipcode],
                    receiving_hospital.name)

        db.session.commit()

    elif data["task"] == "cancel":
        exchanges = db.session.query(Exchange).filter_by(exchange_id=int(data["exchange_id"]))
        eid = -1
        try:
            eid = int(data['e_id'])
        except:
            pass
        if eid >= 0:
            exchanges = exchanges.filter_by(id=eid) 

        for ex in exchanges:
            ex.updated_timestamp=datetime.now()
            ex.status=EXCHANGE_HOSPITAL_CANCELED

            # undo has and wants
            transfer = ex.count
            has = Has.query.filter_by(hospital_id=ex.hospital1)\
                .filter_by(ppe_id=ex.ppe).first()
            has.count += transfer
            wants = Wants.query.filter_by(hospital_id=ex.hospital2)\
                .filter_by(ppe_id=ex.ppe).first()
            wants.count += transfer

            # undo credit transfers
            tx = Hospital.query.filter_by(id=ex.hospital1).first()
            tx.credit -= transfer

            rx = Hospital.query.filter_by(id=ex.hospital2).first()
            rx.credit += transfer

        e = db.session.query(Exchanges).filter_by(id=int(data["exchange_id"])).first()

        e.updated_timestamp=datetime.now()
        e.status=EXCHANGE_COMPLETE_HOSPITAL_CANCELED
        db.session.commit()
    elif data["task"] == "shipped":
        exchange = db.session.query(Exchange)
        exchange = exchange.filter_by(id=int(data["e_id"])).first()
        exchange.is_h1_shipped = True
        exchange.updated_timestamp=datetime.now()
        exchange.status=EXCHANGE_ACCEPTED_SHIPPED
        db.session.commit()
        email.send_hospital_exchange_partner_shipped(
            User.query.filter_by(hospital_id=exchange.hospital2).first().username,
            app.config.get("PPE_HOSTNAME"),
            User.query.filter_by(hospital_id=exchange.hospital2).first().email,
            data["exchange_id"],
            Hospital.query.filter_by(id=exchange.hospital1).first().name,
            exchange.count,
            PPE.query.filter_by(id=exchange.ppe).first().sku)
    elif data["task"] == "received":
        exchange = db.session.query(Exchange)
        exchange = exchange.filter_by(id=int(data["e_id"])).first()
        exchange.is_h2_received = True
        exchange.updated_timestamp=datetime.now()
        exchange.status=EXCHANGE_ACCEPTED_RECEIVED
        email.send_hospital_exchange_partner_received(
            User.query.filter_by(hospital_id=exchange.hospital1).first().username,
            app.config.get("PPE_HOSTNAME"),
            User.query.filter_by(hospital_id=exchange.hospital1).first().email,
            data["exchange_id"],
            Hospital.query.filter_by(id=exchange.hospital2).first().name,
            exchange.count,
            PPE.query.filter_by(id=exchange.ppe).first().sku)
  
        exchanges = db.session.query(Exchange)
        print("here")
        print(data["exchange_id"])
        print("here2")
        exchanges = exchanges.filter_by(exchange_id=int(data["exchange_id"]))
        done = True
        for ex in exchanges:
            if ex.status != EXCHANGE_ACCEPTED_RECEIVED:
                done = False
        print(done)
        print(data["exchange_id"])
        if done == True:
            q = db.session.query(Exchanges)
            q = q.filter_by(id=int(data["exchange_id"]))
            print(data["exchange_id"])
            record = q.first()
            record.status = EXCHANGE_COMPLETE
            record.updated_timestamp = datetime.now()
        db.session.commit()
    return jsonify(target="index")


@app.route('/admin_create_exchange', methods=['GET', 'POST'])
def admin_create_exchange():
    if (not current_user.is_authenticated) or (not User.query.filter_by(username=current_user.username).first().is_admin):
        return redirect(url_for('login',next='/admin_exchange'))

    positive_credits_exchange = None

    # First Pass of the Exchange Algorithm
    # * Creates any exchanges between hospitals that have a positive number of credits

    exchanges = []
    hospitals = Hospital.query.order_by(desc(Hospital.credit))

    for h in hospitals:
        # We ignore any hospitals who don't have a positive amount of credits in this algorithm pass
        if h.credit <= 0:
            continue
        # get all the wants for this hospital
        hws = Wants.query.filter_by(hospital_id=h.id)
        # iterate through hospital wants looking at each ppe wanted
        for hw in hws:
            # get all haves for this ppe -- AKD: add sort in ascending order of has.count
            hhs = Has.query.filter_by(ppe_id=hw.ppe_id)
            # iterate through all haves
            for hh in hhs:
                # determine the amount of PPE to move: minimum of credits, want, has
                moving = min(h.credit, hw.count, hh.count)
                print(moving, h.credit, hw.count, hh.count)
                # if anything to xfer
                if moving > 0:
                    # update want count, has count, rx hospital credits
                    hw.count -= moving
                    hh.count -= moving
                    h.credit -= moving
                    # create exchange
                    exchanges.append({
                                "tx_hospital": hh.hospital_id,
                                "rx_hospital": hw.hospital_id,
                                "ppe": hh.ppe_id,
                                "count": moving
                            })
                    print("exchange:", moving, hh.hospital_id, hw.hospital_id, hh.ppe_id)
                    if hw.count <= 0 or h.credit <= 0:
                        break
            if h.credit <= 0:
                break

    # update tx hospital credits and exchange in d/b
    if len(exchanges) > 0:
        es = Exchanges()
        eid = es.id
        db.session.add(es)
        # loop through created exchanges
        for exchange in exchanges:
            transfer = exchange["count"]

            # first credits
            tx = Hospital.query.filter_by(id=exchange["tx_hospital"]).first()
            tx.credit += transfer

            # already handled udpdating want counts above
            e = Exchange(exchange_id=es.id,hospital1=exchange["tx_hospital"],hospital2=exchange["rx_hospital"],ppe=exchange["ppe"],count=transfer)
            db.session.add(e)
        db.session.commit()
        positive_credits_exchange = es    


    # Second Pass of the Exchange Algorithm
    # * Creates any exchanges between hospitals that have 0 or fewer credits 
 
    # Determine total available supply/has for each hospital
    hospital_has = {}
    hospitals = Hospital.query.all()
    for h in hospitals:
        total_has = 0
        h_has = Has.query.filter_by(hospital_id=h.id)
        for hh in h_has:
            total_has += hh.count

        hospital_has[h.id] = total_has
    print("Total has per hospital:", hospital_has)

    hospitals = Hospital.query.order_by(Hospital.credit)
    ppes = PPE.query.all()

    # Exchanges are created per SKU, so we loop through all of them
    for ppe in ppes:
        exchanges = []

        # Query for haves and wants of this SKU
        haves = Has.query.filter_by(ppe_id=ppe.id)
        wants = Wants.query.filter_by(ppe_id=ppe.id)

        # Calculate the total amount of haves and wants for this SKU
        # * This used to figure out whether it is possible to create an exchange or not
        #### TODO: need to add code to only add to total_wants if you have PPE to give - not used, so can delete
        have_total = 0
        want_total = 0
        for have in haves:
            have_total = have_total + have.count
        for want in wants:
            want_total = want_total + want.count
        
        # Calculate the maximum amount that each hospital can ask for (per PPE)
        # * want_max for each hospital is the min of hospital_has (total has for this hospital) and what this hospital wants for this SKU)
        want_max = {}
        done = {}
        total_want = 0
        for want in wants:
            done[want.hospital_id]=False
            want_max[want.hospital_id] = min(hospital_has[want.hospital_id], want.count)
            total_want += want_max[want.hospital_id]

        # If there is both has and want for this ppe, create a swap. Otherwise, skip it
        if total_want > 0 and have_total > 0:
            print("Creating exchanges for ppe:", ppe.sku)

            # Calculate ratio of total Has/Wants for this PPE
            ratio = 1
            if have_total >= total_want:
                ratio = 1
            else:
                ratio = have_total/total_want
            print(" * Have/Want ratio:", ratio)

            # Sort haves based on hospital credits. 
            haves = []
            hospitals = Hospital.query.order_by(Hospital.credit)
            for h in hospitals:
                ha = Has.query.filter_by(hospital_id=h.id, ppe_id=ppe.id)
                if ha.count() > 0:
                    haves.append(ha.first())
            
            print(" * Sorted haves:", haves)

            for have in haves:
                send_amount = have.count

                for want in wants:
                    if not done[want.hospital_id]:
                        # We already took the min while calculating want_max, so we don't need to take it again
                        # want_amount = min(want_max[want.hospital_id], hospital_has[want.hospital_id])
                        want_amount = int(want_max[want.hospital_id]*ratio)

                        sending = min(send_amount, want_amount)
                        send_amount = send_amount - sending
                        want_amount = want_amount - sending
                        want_max[want.hospital_id] = want_max[want.hospital_id] - sending
                        if want_amount == 0:
                            done[want.hospital_id]=True
                        want.count = want.count - sending
                        if sending > 0:
                            swap = {
                                "tx_hospital": have.hospital_id,
                                "rx_hospital": want.hospital_id,
                                "ppe": have.ppe_id,
                                "count": sending
                            }
                            exchanges.append(swap)
                        if send_amount == 0:
                            break    
                    # not enough supply to meet demand


            # update credits and has and wants
            if len(exchanges) > 0:
                es = None
                if positive_credits_exchange == None:
                    es = Exchanges()
                else:
                    es = positive_credits_exchange

                eid = es.id
                db.session.add(es)
                # loop through created exchanges
                print(" * Swaps:")
                for exchange in exchanges:
                    print("    *", exchange)
                    transfer = exchange["count"]

                    # first credits
                    tx = Hospital.query.filter_by(id=exchange["tx_hospital"]).first()
                    tx.credit += transfer

                    rx = Hospital.query.filter_by(id=exchange["rx_hospital"]).first()
                    rx.credit -= transfer

                    # then has
                    tx_has = Has.query.filter_by(hospital_id=exchange["tx_hospital"], ppe_id=exchange["ppe"]).first()
                    tx_has.count -= transfer

                    # already handled udpdating want counts above
                    e = Exchange(exchange_id=es.id,hospital1=exchange["tx_hospital"],hospital2=exchange["rx_hospital"],ppe=ppe.id,count=transfer)
                    db.session.add(e)
                db.session.commit()
        else:
            print("Could not create exchange for ppe:", ppe.sku)
    print("")
    return redirect(url_for('admin_exchange'))