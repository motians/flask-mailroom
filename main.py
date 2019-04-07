import os
import base64

from flask import Flask, render_template, request, redirect, url_for, session
from model import Donation, Donor, User
from passlib.hash import pbkdf2_sha256

import peewee

app = Flask(__name__)
# app.secret_key = b'\x9d\xb1u\x08%\xe0\xd0p\x9bEL\xf8JC\xa3\xf4J(hAh\xa4\xcdw\x12S*,u\xec\xb8\xb8'
app.secret_key = os.environ.get('SECRET_KEY').encode()


@app.route('/')
def home():
    return redirect(url_for('all'))


@app.route('/donations/')
def all():
    """ Function to display list of all donations """

    donations = Donation.select()
    return render_template('donations.jinja2', donations=donations)


@app.route('/allfordonor/', methods=['GET', 'POST'])
def allfordonor():
    """ Function to get donor name and obtain list of donations """

    if request.method == 'POST':
        try:
            donor_lookup = Donor.select().where(Donor.name == request.form['name']).get()
            donations = Donation.select().where(Donation.donor == donor_lookup)
            donation_list = [donation.value for donation in donations]

            session['donations'] = donation_list
            session['donor_name'] = request.form['name']

            return redirect(url_for('displaydonordonations'))
        except peewee.DoesNotExist:
            return render_template('allfordonor.jinja2', error='Donor not found.')

    return render_template('allfordonor.jinja2')


@app.route('/displaydonordonations/')
def displaydonordonations():
    """ Displays list of donations for donor """

    return render_template('displaydonordonations.jinja2', donations=session['donations'], name=session['donor_name'])


@app.route('/create/', methods=['GET', 'POST'])
def create():
    """
    Function for creating new donation
    User must be signed in
    """

    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            donor_lookup = Donor.select().where(Donor.name == request.form['name']).get()

            if donor_lookup:
                Donation.create(donor=donor_lookup, value=request.form['value'])
                return redirect(url_for('all'))
        except peewee.DoesNotExist:
            return render_template('create.jinja2', error='Donor does not exist.')

    return render_template('create.jinja2')


@app.route('/login/', methods=['GET', 'POST'])
def login():
    """ User login """

    if request.method == 'POST':
        try:
            got_user = User.select().where(User.name == request.form['name']).get()

            if got_user and pbkdf2_sha256.verify(request.form['password'], got_user.password):
                session['username'] = request.form['name']
                return redirect(url_for('create'))
            else:
                return render_template('login.jinja2', error='Login failure.')
        except peewee.DoesNotExist:
            return render_template('login.jinja2', error='Login failure.')

    return render_template('login.jinja2')


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 6738))
    app.run(host='127.0.0.1', port=port)

