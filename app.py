# -*- coding: utf-8 -*-
"""
Created on Tue Dec  8 14:02:36 2015

@author: alhamood
"""

from flask import Flask, Response, render_template
from flask.ext.login import LoginManager, UserMixin, login_required
from itsdangerous import JSONWebSignatureSerializer
from wtforms import Form, TextField, PasswordField, validators
import os
import sys
import logging

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
#login_manager.login_view = 'login'

app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)


class User(UserMixin):
	# Replace this with loading of database, and hash passwords
	user_database = {'MarderUser': ('MarderUser', 'crabs'),
		'Admin': ('Admin', 'admin')}
		
	def __init__(self, username, password):
		self.id = username
		self.password = password
	
	@classmethod
	def get(cls, id):
		return cls.user_database.get(id)


class LoginForm(Form):
	username = TextField('Username')
	password = PasswordField('Password')


@login_manager.user_loader
def load_user(request):
	token = request.args.get('token')
	s = JSONWebSignatureSerializer('secret-key')
	credential = s.loads(token)	
	username, password = credential
	user_entry = User.get(username)
	if (user_entry is not None):
		user = User(user_entry[0], user_entry[1])
		if user.password == password:
			return user
	return None
	

# dummy route here to terminate during early testing phase	
@app.route('/nope', methods=['get', 'post'])
def nope():
	return Response(response="NOPE")

		
@app.route('/')
def index():
	form = LoginForm()
	return render_template('login-page.html', form=form)

	
@app.route('/protected-page', methods=['POST'])
@login_required
def protected():
	return Response(response="Hello Protected World!", status=200)


if __name__ == '__main__':
	#app.config["SECRET_KEY"] = "ITSASECRET"
	port = int(os.environ.get("PORT", 5000))	
	app.run(host='0.0.0.0', port=port, debug=True)