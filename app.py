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
import random
import string
import logging
import hashlib
import flask.ext.login
import simplejson as json
import pandas as pd


app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
global editusername_global

app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)


with open('user_pdatabase.txt') as json_data:
	user_pdatabase = json.load(json_data)
	json_data.close()


with open('user_database.txt') as json_data:
	user_database = json.load(json_data)
	json_data.close()
	
	
with open('config.txt') as json_data:
	config = json.load(json_data)
	json_data.close()


class User(UserMixin):
	pass


class LoginForm(Form):
	username = fields.TextField('Username')
	password = fields.PasswordField('Password')
	
	
class EditUserForm(Form):
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
		

class UserForm(EditUserForm):
	username = fields.TextField('Username', [
		validators.Length(max=20, message='Under 20 characters please!'),
		validators.InputRequired(message='Username is required')
		])


class NewUserForm(UserForm):
	password = fields.PasswordField('Password', [
		validators.InputRequired(message='Password Field(s) Empty'),
		validators.EqualTo('confirm', message='Passwords unmatched.')
	])
	confirm = fields.PasswordField('Password')
	

class PasswordChangeForm(Form):
	oldpassword = fields.PasswordField('Old Password', [
		validators.InputRequired(message='Please enter old password')])
	password = fields.PasswordField('New Password', [
		validators.InputRequired(message='Password Field(s) Empty'),
		validators.EqualTo('confirm', message='Passwords unmatched.')
	])
	confirm = fields.PasswordField('New Password (reenter)')	

	
class AdminActionForm(Form):
	username = fields.TextField('Username', [
		validators.AnyOf(user_database.keys())])
	action = fields.SelectField('Action', choices = [
		('edit', 'Edit User'), ('delete', 'Delete User'),
		('password', 'Reset Password')])
		

def MakeDF(data, column_names):
	print(data.values())
	df = pd.DataFrame(data.values(), columns = column_names)
	df.index = user_database.keys()	
	return df
	

@login_manager.user_loader
def load_user(user_id):
	if user_id not in user_database:
		return
	user = User()
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
	global editusername_global
	form = LoginForm(request.form)
	if form.validate():
		user = load_user(form.username.data)
		if user is None:
			return render_template('/unauthorized-page.html')
		if hashlib.sha256(form.data['password']).hexdigest() \
				== user_pdatabase[user.id]:
			flask.ext.login.login_user(user)
			editusername_global = g.user.id
			return redirect(url_for('index'))
	return render_template('/unauthorized-page.html')


@app.route('/download-page', methods=['GET', 'POST'])
def download_page():
	if config['DownloadsAllowed'] != 1:
		return render_template('feature-disabled.html')
	return render_template('download-page.html')


@app.route('/upload-page')
@login_required
def upload_page():
	if config['UploadsAllowed'] != 1:
		return render_template('feature-disabled.html')
	return render_template('upload-page.html')


@app.route('/new-user', methods=['GET', 'POST'])
def new_user():
	if config['NewUsersAllowed'] != 1:
		return render_template('feature-disabled.html')
	if request.method == 'GET':
		# get new user information, then come back as a post
		if len(user_database) > (config['MaxUsers']-1):
			return render_template('too-many-users.html')
		form = NewUserForm()
		return render_template('new-user.html', form=form)
	else:
		# create the user with validated user information
		form = NewUserForm(request.form)
		if form.validate():
			if form.data['username'] in user_database.keys():
				return render_template('username-collision.html')
			user_database[form.data['username']] = \
				[form.data['email'], form.data['surname'],
				form.data['lab']]
			user_pdatabase[form.data['username']] = \
				(hashlib.sha256(form.data['password']).hexdigest())
			with open('user_database.txt', 'w') as outfile:
				json.dump(user_database, outfile)
			with open('user_pdatabase.txt', 'w') as outfile:
				json.dump(user_pdatabase, outfile)
			user = load_user(form.data['username'])
			flask.ext.login.login_user(user)
			return redirect(url_for('index'))
		else:			
			return render_template('new-user.html', form=form)


@app.route('/edit-user', methods=['GET', 'POST'])
@login_required
def edit_user():
	global editusername_global
	if request.method == 'GET':
		# get old user information, then come back as a post
		form = EditUserForm(surname=user_database[editusername_global][1], \
			email=user_database[editusername_global][0], \
			lab=user_database[editusername_global][2])
		return render_template('edit-user.html', form=form, name=editusername_global)
	else:
		# re-save the user with validated user information
		form = EditUserForm(request.form)
		if form.validate():
			user_database[editusername_global] = \
				[form.data['email'], form.data['surname'],
				form.data['lab']]
			with open('user_database.txt', 'w') as outfile:
				json.dump(user_database, outfile)
			return redirect(url_for('index'))
		else:
			return render_template('edit-user.html', form=form, name=editusername_global)


@app.route('/password-change', methods=['GET', 'POST'])
@login_required
def password_change():
	global editusername_global
	if request.method == 'GET':
		# get new password, then come back as a post
		form = PasswordChangeForm()
		return render_template('password-change.html', form=form, msg=editusername_global+' password change')
	else:
		# re-save the user's hashed new password with validated user information
		form = PasswordChangeForm(request.form)
		if hashlib.sha256(form.data['oldpassword']).hexdigest() \
				!= user_pdatabase[editusername_global]:
			return render_template('password-change.html', form=form, msg='Wrong password for '+editusername_global)
		if not form.validate():
			return render_template('password-change.html', form=form, msg=editusername_global+' password change')						
		else:
			user_pdatabase[editusername_global] = \
				(hashlib.sha256(form.data['password']).hexdigest())
			with open('user_pdatabase.txt', 'w') as outfile:
				json.dump(user_pdatabase, outfile)	
			return redirect(url_for('index'))


@app.route('/admin-page', methods=['GET', 'POST'])
@login_required
def admin_page():
	global editusername_global
	if g.user.id != "Admin":
		return redirect(url_for('index'))
	if request.method == "GET":
		users_df = MakeDF(user_database, ['Email', 'Surname', 'Lab'])
		table_html = users_df.to_html()
		form = AdminActionForm()
		return render_template('admin-page.html', table_html=table_html, \
			form=form)
	else:
		form = AdminActionForm(request.form)		
		if not form.validate():
			users_df = MakeDF(user_database, ['Email', 'Surname', 'Lab'])
			table_html = users_df.to_html()
			return render_template('admin-page.html', \
				table_html=table_html, form=form)
		if form.data['username'] not in user_database.keys():
			msg = 'User not found'
			return render_template('admin-message.html', msg=msg)		
		if form.data['action'] == 'delete':
			if form.data['username'] == "Admin":
				msg = 'You cannot delete Admin, Admin.'
			else:
				user_database.pop(form.data['username'])
				user_pdatabase.pop(form.data['username'])
				with open('user_database.txt', 'w') as outfile:
					json.dump(user_database, outfile)
				with open('user_pdatabase.txt', 'w') as outfile:
					json.dump(user_pdatabase, outfile)
				msg = 'User ' + form.data['username'] + ' deleted.'
			return render_template('admin-message.html', msg=msg)
		if form.data['action'] == 'edit':
			editusername_global = form.data['username']
			form = EditUserForm(surname=user_database[editusername_global][1], \
				email=user_database[editusername_global][0], \
				lab=user_database[editusername_global][2])
			return render_template('edit-user.html', form=form, name=editusername_global)
		if form.data['action'] == 'password':
			new_random_password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8))
			user_pdatabase[form.data['username']] = \
				(hashlib.sha256(new_random_password).hexdigest())
			with open('user_pdatabase.txt', 'w') as outfile:
				json.dump(user_pdatabase, outfile)
			msg = ('Password for '+form.data['username']+' set to '+new_random_password)
			msg2 = ('\nPlease email this password to '+user_database[form.data['username']][0])
			return render_template('admin-message.html', msg=msg+msg2)			
		return redirect(url_for('new_user'))


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
