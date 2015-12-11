# -*- coding: utf-8 -*-
"""
Created on Tue Dec  8 14:02:36 2015

Pyloric Database Web Server

@author: alhamood
"""

from flask import Flask, render_template, request, redirect, url_for, g
from flask.ext.login import LoginManager, UserMixin, login_required
from wtforms import Form, validators, fields
import os
import sys
import logging
import hashlib
import flask.ext.login
import simplejson as json


app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)


app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)


with open('user_pdatabase.txt') as json_data:
	user_pdatabase = json.load(json_data)
	json_data.close()
		

with open('user_database.txt') as json_data:
	user_database = json.load(json_data)
	json_data.close()
				
		
class User(UserMixin):	
	pass


class LoginForm(Form):
	username = fields.TextField('Username')
	password = fields.PasswordField('Password')


class UserForm(Form):
	username = fields.TextField('Username', [
		validators.Length(max=20, message='Under 20 characters please!'),
		validators.InputRequired(message='Username is required')
		])
	email = fields.TextField('email', [
		validators.Email(message='Not an email address.')
		])
	surname = fields.TextField('Surname', [
		validators.Length(max=25, message='Sorry 25 characters max'),
		validators.InputRequired(message='Surname required')
		])
	lab = fields.TextField('Lab PI surname', [
		validators.Length(max=20, message='20 characters max'),
		validators.InputRequired(message='Lab PI surname required')
		])
	

class NewUserForm(UserForm):
	password = fields.PasswordField('Password', [
		validators.InputRequired(message='Password Field(s) Empty'),
		validators.EqualTo('confirm', message='Passwords unmatched.')
	])
	confirm = fields.PasswordField('Password')
	

@login_manager.user_loader
def load_user(user_id):
	if user_id not in user_pdatabase:
		return		
	user=User()
	user.id = user_id
	user.email = user_database[user_id][0]
	user.surname = user_database[user_id][1]	
	user.lab = user_database[user_id][2]
	g.user = user
	return user


@login_manager.unauthorized_handler
def nope():
	return render_template('unauthorized-page.html')


@app.route('/login', methods=['POST'])
def login():
	form = LoginForm(request.form)
	if form.validate():
		user = load_user(form.username.data)
		if user == None:
			return render_template('/unauthorized-page.html')
		if hashlib.sha256(form.data['password']).hexdigest() \
				== user_pdatabase[user.id]:
			flask.ext.login.login_user(user)
			return redirect(url_for('index'))
	return render_template('/unauthorized-page.html')


@app.route('/download-page', methods=['GET', 'POST'])
def download_page():
	return render_template('download-page.html')

	
@app.route('/upload-page')
@login_required
def upload_page():
	return render_template('upload-page.html')
	
	
@app.route('/new-user', methods=['GET', 'POST'])
def new_user():
	if request.method == 'GET':
		# get new user information, then come back as a post
		form = NewUserForm()
		return render_template('new-user.html', form=form)
	else:
		# create the user with validated user information
		form = NewUserForm(request.form)
		if form.validate():
			user_database[form.data['username']] = \
				(form.data['email'], form.data['surname'],
				form.data['lab'])
			user_pdatabase[form.data['username']] = \
				(hashlib.sha256(form.data['password']).hexdigest())
			with open('user_database.txt', 'w') as outfile:
				json.dump(user_database, outfile)
			with open('user_pdatabase.txt', 'w') as outfile:
				json.dump(user_pdatabase, outfile)
			return redirect(url_for('sign_in'))
		else:
			return render_template('new-user.html', form=form)


@app.route('/admin-page')
@login_required
def admin_page():
	if g.user.id == "Admin":
		return render_template('admin-page.html')
	else:
		return redirect(url_for('index'))


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