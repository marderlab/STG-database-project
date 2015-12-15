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
import time
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
global exp_name_global

app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)


with open('user_pdatabase.json') as json_data:
	user_pdatabase = json.load(json_data)
	json_data.close()


with open('user_database.json') as json_data:
	user_database = json.load(json_data)
	json_data.close()
	
	
with open('config.json') as json_data:
	config = json.load(json_data)
	json_data.close()
	
	
with open('metadata.json') as json_data:
	metadata = json.load(json_data)
	json_data.close()
	
	
with open('notes.json') as json_data:
	notes = json.load(json_data)
	json_data.close()
	
	
with open('processed_data.json') as json_data:
	proc_data = json.load(json_data)
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


class DeleteForm(Form):
	verify = fields.TextField('Type DELETE to confirm.')
	
	
class AdminActionForm(Form):
	username = fields.TextField('Username', [
		validators.AnyOf(user_database.keys())])
	action = fields.SelectField('Action', choices = [
		('edit', 'Edit User'), ('delete', 'Delete User'),
		('password', 'Reset Password')])
		
		
class UploadActionForm(Form):
	identifier = fields.IntegerField('Experiment index (number in left column)', [
		validators.Optional()])
	action = fields.SelectField('Action', choices=[
		('editM', 'Edit Metadata (what you see here)'),
		('editP', 'Edit Processed Data (such as frequency)'),
		('delete', 'Delete Experiment')])
		
		
class MetadataForm(Form):
	exp_date = fields.DateField('Experiment Date',  [
		validators.InputRequired(message='Experiment Date is Required')], format='%m/%d/%Y')
	animal_date = fields.DateField('Animal Arrival Date', [
		validators.Optional()], format='%m/%d/%Y')
	experimenter = fields.TextField('Experimenter Surname', [
		validators.Length(max=15, message='15 characters max')])
	lab = fields.TextField('Lab PI Surname', [
		validators.Length(max=15, message='15 characters max')])	
	temp = fields.IntegerField('Temperature in C', [validators.Optional()])
	species = fields.SelectField('Species', choices = [
		('crab', 'Crab'), ('lobster', 'Lobster')])
	saline = fields.SelectField('Saline', choices = [
		('std', 'Standard'), ('alt', 'Altered (describe in notes)')])
	notes = fields.TextAreaField('Purpose / Notes', [
		validators.length(max=500, message='500 characters max')])
		

class NewMetadataForm(MetadataForm):
	exp_id = fields.TextField('Experiment ID (such as lab notebook and page)', [
		validators.Length(max=10, message='10 characters max'),
		validators.InputRequired(message='You must provide a unique ID')])
		
		
class ProcessedDataForm(Form):
	pyl_hz = fields.DecimalField('Pyloric frequency (Hz)', [validators.Optional()])
	pyl_cycvar = fields.DecimalField('Pyloric cyc-to-cyc var (%)', [validators.Optional()])
	pyl_niqr = fields.DecimalField('Pyloric frequency NIQR', [validators.Optional()])
	gas_hz = fields.DecimalField('Gastric frequency (Hz)', [validators.Optional()])
	gas_cycvar = fields.DecimalField('Gastric cyc-to-cyc var (%)', [validators.Optional()])
	gas_niqr = fields.DecimalField('Gastric frequency NIQR', [validators.Optional()])
	pd_off = fields.DecimalField('PD off phase (duty cycle, 0-1)', [
		validators.NumberRange(min=0, max=1, message='0-1 please, not radians!'), validators.Optional()])
	pd_spikes = fields.DecimalField('PD spikes/burst', [validators.Optional()])
	lp_on = fields.DecimalField('LP on phase (0-1, from PD start)', [validators.Optional()])	
	lp_off = fields.DecimalField('LP off phase (0-1, from PD start)', [validators.Optional()])
	lp_spikes = fields.DecimalField('LP spikes/burst', [validators.Optional()])
	py_on = fields.DecimalField('PY on phase (0-1, from PD start)', [validators.Optional()])	
	py_off = fields.DecimalField('PY off phase (0-1, from PD start)', [validators.Optional()])
	py_spikes = fields.DecimalField('PY spikes/burst', [validators.Optional()])	
	vd_on = fields.DecimalField('VD on phase (0-1, from PD start)', [validators.Optional()])	
	vd_off = fields.DecimalField('VD off phase (0-1, from PD start)', [validators.Optional()])
	vd_spikes = fields.DecimalField('VD spikes/burst', [validators.Optional()])
	lg_off = fields.DecimalField('Gastric LG off phase (duty cycle, 0-1', [validators.Optional()])
	lg_spikes = fields.DecimalField('Gastric LG spikes/burst', [validators.Optional()])	
	dg_on = fields.DecimalField('Gastric DG on phase (0-1, from LG start)', [validators.Optional()])	
	dg_off = fields.DecimalField('Gastric DG off phase (0-1, from LG start)', [validators.Optional()])
	dg_spikes = fields.DecimalField('Gastric DG spikes/burst', [validators.Optional()])
	gm_on = fields.DecimalField('Gastric GM on phase (0-1, from LG start)', [validators.Optional()])	
	gm_off = fields.DecimalField('Gastric GM off phase (0-1, from LG start)', [validators.Optional()])
	gm_spikes = fields.DecimalField('Gastric GM spikes/burst', [validators.Optional()])
	mg_on = fields.DecimalField('Gastric MG on phase (0-1, from LG start)', [validators.Optional()])	
	mg_off = fields.DecimalField('Gastric MG off phase (0-1, from LG start)', [validators.Optional()])
	mg_spikes = fields.DecimalField('Gastric MG spikes/burst', [validators.Optional()])	
	
			
def MakeDF(data, column_names):
	df = pd.DataFrame(data.values(), columns = column_names)
	df.index = user_database.keys()	
	return df


def MakeMetaDF(data, column_names):
	df = pd.DataFrame(data.values(), columns = column_names)
	df = df.sort_values(by='Exp Date')
	df.index = range(len(df)) 
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


@app.route('/upload-page', methods=['GET', 'POST'])
@login_required
def upload_page():
	global exp_name_global
	if config['UploadsAllowed'] != 1:
		return render_template('feature-disabled.html')
	if request.method == 'GET':
		metadata_df=MakeMetaDF(metadata, ['User', 'Exp ID', 'Exp Date',
			'Animal Date', 'Experimenter', 'Lab', 'Temp (C)', 'Species', 'Saline'])
		if g.user.id != 'Admin':
			metadata_df=metadata_df.loc[metadata_df.loc[:,'User']==g.user.id,:]
		table_html = metadata_df.to_html()
		form = UploadActionForm()
		return render_template('upload-page.html', table_html=table_html, form=form)
	else:
		form = UploadActionForm(request.form)
		metadata_df=MakeMetaDF(metadata, ['User', 'Exp ID', 'Exp Date',
			'Animal Date', 'Experimenter', 'Lab', 'Temp (C)', 'Species', 'Saline'])
		if g.user.id != 'Admin':
			metadata_df=metadata_df.loc[metadata_df.loc[:,'User']==g.user.id,:]	
		if form.validate():
			print(form.data['identifier'])
			if form.data['identifier']<0 or form.data['identifier']>(len(metadata_df)-1) or form.data['identifier']==None:
				return render_template('upload-message.html', msg='Invalid identifier')
			exp_name_global = metadata_df.loc[form.data['identifier'], 'User']+':'+metadata_df.loc[form.data['identifier'], 'Exp ID']	
			if form.data['action'] == 'editP':
				return redirect(url_for('processed_data'))
			if form.data['action'] == 'editM':
				return redirect(url_for('edit_metadata'))
			if form.data['action'] == 'delete':
				return redirect(url_for('delete_experiment'))


@app.route('/delete-experiment', methods=['GET', 'POST'])
@login_required
def delete_experiment():
	global exp_name_global
	if config['EditsAllowed'] != 1:
		return render_template('feature-disabled.html')
	if request.method == 'GET':
		form = DeleteForm()
		return render_template('delete-experiment.html', name=exp_name_global, form=form)
	else:
		form = DeleteForm(request.form)
		if form.data['verify'] == 'DELETE':
			metadata.pop(exp_name_global)
			notes.pop(exp_name_global)
			proc_data.pop(exp_name_global)
			with open('metadata.json', 'w') as outfile:
				json.dump(metadata, outfile)
			with open('notes.json', 'w') as outfile:
				json.dump(notes, outfile)
			with open('processed_data.json', 'w') as outfile:
				json.dump(proc_data, outfile)			
			msg='Deleted experiment '+exp_name_global
			return render_template('upload-message.html', msg=msg)
		else:
			msg='Did not delete, DELETE was not received.'
			return render_template('upload-message.html', msg=msg)


@app.route('/new-experiment', methods=['GET', 'POST'])
@login_required
def new_experiment():
	global exp_name_global
	if config['UploadsAllowed'] != 1:
		return render_template('feature-disabled.html')
	if request.method == 'GET':
		form = NewMetadataForm()
		return render_template('new-experiment.html', name=g.user.id, form=form)
	else:
		form = NewMetadataForm(request.form)
		if form.validate():
			if g.user.id+':'+form.data['exp_id'] in metadata.keys():
				return render_template('upload-message.html', msg='Experiment ID already exists')	
			exp_name_global = g.user.id+':'+form.data['exp_id']	
			metadata[g.user.id+':'+form.data['exp_id']] = [
				g.user.id, form.data['exp_id'], str(form.data['exp_date']),
				str(form.data['animal_date']), form.data['experimenter'],
				form.data['lab'], form.data['temp'], form.data['species'],
				form.data['saline']]
			notes[g.user.id+':'+form.data['exp_id']] = form.data['notes']
			proc_data[g.user.id+':'+form.data['exp_id']] = [None]*28
			with open('metadata.json', 'w') as outfile:
				json.dump(metadata, outfile)
			with open('notes.json', 'w') as outfile:
				json.dump(notes, outfile)
			with open('processed_data.json', 'w') as outfile:
				json.dump(proc_data, outfile)
			return redirect(url_for('processed_data'))
		else:
			return render_template('new-experiment.html', name=g.user.id, form=form)

			
@app.route('/edit-metadata', methods=['GET', 'POST'])
@login_required
def edit_metadata():
	global exp_name_global
	if config['EditsAllowed'] != 1:
		return render_template('feature-disabled.html')
	if request.method == 'GET':
		data = metadata[exp_name_global]
		form = MetadataForm(experimenter=data[4], notes=notes[exp_name_global],
			lab=data[5], temp=data[6], species=data[7], saline=data[8])
		return render_template('edit-metadata.html', form=form, name=exp_name_global, oldexpdate=data[2], oldandate=data[3])
	else:
		form = MetadataForm(request.form)
		if form.validate():
			metadata[exp_name_global][2] = str(form.data['exp_date'])
			metadata[exp_name_global][3] = str(form.data['animal_date'])
			metadata[exp_name_global][4] = form.data['experimenter']
			metadata[exp_name_global][5] = form.data['lab']
			metadata[exp_name_global][6] = form.data['temp']
			metadata[exp_name_global][7] = form.data['species']
			metadata[exp_name_global][8] = form.data['saline']
			notes[exp_name_global] = form.data['notes']
			with open('metadata.json', 'w') as outfile:
				json.dump(metadata, outfile)
			with open('notes.json', 'w') as outfile:
				json.dump(notes, outfile)
			return redirect(url_for('upload_page'))
		else:
			return render_template('edit-metadata.html', name=exp_name_global, form=form)


@app.route('/processed-data', methods=['GET', 'POST'])
@login_required
def processed_data():
	if config['EditsAllowed'] != 1:
		return render_template('feature-disabled.html')
	global exp_name_global
	if request.method == 'GET':
		data = proc_data[exp_name_global]
		form = ProcessedDataForm(pyl_hz=data[0], pyl_cycvar=data[1], pyl_niqr=data[2],
			gas_hz=data[3], gas_cycvar=data[4], gas_niqur=data[5], pd_off=data[6],
			pd_spikes=data[7], lp_on=data[8], lp_off=data[9], lp_spikes=data[10],
			py_on=data[11], py_off=data[12], py_spikes=data[13], vd_on=data[14],
			vd_off=data[15], vd_spikes=data[16], lg_off=data[17], lg_spikes=data[18],
			dg_on=data[19], dg_off=data[20], dg_spikes=data[21], gm_on=data[22],
			gm_off=data[23], gm_spikes=data[24], mg_on=data[25], mg_off=data[26],
			mg_spikes=data[27])
		return render_template('processed-data.html', form=form, name=exp_name_global)
	else:
		form = ProcessedDataForm(request.form)
		if form.validate():
			proc_data[exp_name_global] = [form.data['pyl_hz'],
				form.data['pyl_cycvar'], form.data['pyl_niqr'], form.data['gas_hz'],
				form.data['gas_cycvar'], form.data['gas_niqr'], form.data['pd_off'],
				form.data['pd_spikes'], form.data['lp_on'], form.data['lp_off'],
				form.data['lp_spikes'], form.data['py_on'], form.data['py_off'],
				form.data['py_spikes'], form.data['vd_on'], form.data['vd_off'],
				form.data['vd_spikes'], form.data['lg_off'], form.data['lg_spikes'],
				form.data['dg_on'], form.data['dg_off'], form.data['dg_spikes'],
				form.data['gm_on'], form.data['gm_off'], form.data['gm_spikes'],
				form.data['mg_on'], form.data['mg_off'], form.data['mg_spikes']]
			with open('processed_data.json', 'w') as outfile:
				json.dump(proc_data, outfile)
			return redirect(url_for('upload_page'))
		else:
			return render_template('processed-data.html', form=form, name=exp_name_global)


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
			with open('user_database.json', 'w') as outfile:
				json.dump(user_database, outfile)
			with open('user_pdatabase.json', 'w') as outfile:
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
			with open('user_database.json', 'w') as outfile:
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
			with open('user_pdatabase.json', 'w') as outfile:
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
				with open('user_database.json', 'w') as outfile:
					json.dump(user_database, outfile)
				with open('user_pdatabase.json', 'w') as outfile:
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
			with open('user_pdatabase.json', 'w') as outfile:
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
