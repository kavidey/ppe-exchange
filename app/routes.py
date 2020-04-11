from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, VerifyForm
from app.models import User

import json


@app.route('/')
@app.route('/index')
@login_required
def index():
    hospital = {
        "hospital_name": "UW"
    }
    return render_template('index.html', title='Home', hospital=hospital)


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
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if not current_user.is_authenticated:
        return redirect(url_for('login',next='/verify?uid='+request.args.get("uid")))
    form = VerifyForm()
    if form.validate_on_submit():
        '''
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        '''
        print("user id:", request.args.get("uid"), "contact:",form.contact.data,"hospital name:", form.hospital_name.data)
        flash('Congratulations, you are now a verified user!')
        return redirect(url_for('index'))
    return render_template('verify.html', title='Verify', form=form)

@app.route('/wants', methods=['GET', 'POST'])
def wants():
    if not current_user.is_authenticated:
        return redirect(url_for('login',next='/want'))
    hospital = {
        "hospital_name": "UW"
    }
    items = [
        {
            "sku": 1,
            "count": 5
        },
        {
            "sku": 2,
            "count": 3
        },
        {
            "sku": 3,
            "count": 7
        }
    ]
    return render_template('item_base.html', title='Wants', hospital=hospital, state="Wants", items=items)

@app.route('/has', methods=['GET', 'POST'])
def has():
    if not current_user.is_authenticated:
        return redirect(url_for('login',next='/has'))
    hospital = {
        "hospital_name": "UW"
    }
    items = [
        {
            "sku": 1,
            "count": 2
        },
        {
            "sku": 2,
            "count": 4
        },
        {
            "sku": 3,
            "count": 0
        }
    ]
    return render_template('item_base.html', title='Have', hospital=hospital, state="Has", items=items)

@app.route('/update_want_need', methods=['GET', 'POST'])
def update_want_need():
    data = json.loads(request.get_data())
    print(data)
    if not current_user.is_authenticated:
        return jsonify(target="login?next="+data['state'])
    return jsonify(target="index")