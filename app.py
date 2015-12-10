# -*- coding: utf-8 -*-
"""
Created on Tue Dec  8 14:02:36 2015

@author: alhamood
"""

from flask import Flask, Response, render_template, request, redirect, url_for
from flask.ext.login import LoginManager, UserMixin, login_required
from itsdangerous import JSONWebSignatureSerializer
from wtforms import Form, TextField, PasswordField, validators
import os
import sys
import logging
import flask.ext.login 

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)

app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

user_pdatabase = {'MarderUser': 'crabs',
		'Admin': 'admin'}
		
user_database = {'MarderUser': ('marder_email', 'marder_phone')}
		
		
class User(UserMixin):	
	pass


class LoginForm(Form):
	username = TextField('Username')
	password = PasswordField('Password')


@login_manager.user_loader
def load_user(user_id):
	print('hello from user_loader!')
	if user_id not in user_pdatabase:
		return		
	user=User()
	user.id = user_id
	user.email = user_database[user_id][0]
	user.phone = user_database[user_id][1]
	return user
	

@app.route('/login', methods=['post'])
def login():
	form = LoginForm(request.form)
	if form.validate():
		user=load_user(form.username.data)
		if user == None:
			return render_template('/unauthorized-page.html')		
		if form.password.data == user_pdatabase[user.id]:
			flask.ext.login.login_user(user)
			return redirect(url_for('index'))		
	return render_template('/unauthorized-page.html')


@login_manager.unauthorized_handler
def nope():
	form = LoginForm()
	return render_template('unauthorized-page.html')


@app.route('/download-page', methods=['get', 'post'])
def download_page():
	return render_template('download-page.html')

	
@app.route('/upload-page')
@login_required
def upload_page():
	return render_template('upload-page.html')
	

@app.route('/')
def index():
	return render_template('index.html')

		
@app.route('/sign-in')
def sign_in():
	form = LoginForm()
	return render_template('sign-in.html', form=form)


@app.route('/sign-out')
def sign_out():
	flask.ext.login.logout_user()
	return render_template('sign-out.html')


if __name__ == '__main__':
	app.config["SECRET_KEY"] = "ITSASECRET"
	port = int(os.environ.get("PORT", 5000))	
	app.run(host='0.0.0.0', port=port, debug=True)