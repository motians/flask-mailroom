import os
import base64

from flask import Flask, render_template, request, redirect, url_for, session
from model import Donation, Donor
import peewee

app = Flask(__name__)


@app.route('/')
def home():
    return redirect(url_for('all'))


@app.route('/donations/')
def all():
    """ Function to display list of all donations """

    donations = Donation.select()
    return render_template('donations.jinja2', donations=donations)


@app.route('/create/', methods=['GET', 'POST'])
def create():
    """ Function for creating donation """

    if request.method == 'POST':
        try:
            donor_lookup = Donor.select().where(Donor.name == request.form['name']).get()

            if donor_lookup:
                Donation.create(donor=donor_lookup, value=request.form['value'])
                return redirect(url_for('all'))
        except peewee.DoesNotExist:
            return render_template('create.jinja2', error='Donor does not exist.')

    return render_template('create.jinja2')


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 6738))
    app.run(host='127.0.0.1', port=port)

