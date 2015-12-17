# -*- coding: utf-8 -*-
"""
Created on Tue Dec 15 00:46:35 2015

Simple tool to reset Admin password for STG database server
Run from command line (terminal), restart server after (app.py)

@author: alhamood
"""

import getpass
import hashlib
import json

print('This tool resets the password for Admin.')
print('Admin account can control all data and users on the server')

new_password = getpass.getpass('New Admin password: ')
confirm = getpass.getpass('Confirm new password: ')

if new_password == confirm:
	with open('databases/user_pdatabase.json') as json_data:
		user_pdatabase = json.load(json_data)
		json_data.close()
	user_pdatabase['Admin']=hashlib.sha256(new_password).hexdigest()
	with open('databases/user_pdatabase.json', 'w') as outfile:
		json.dump(user_pdatabase, outfile)
	print('Password reset.')
else:
	print('Passwords did not match! Did nothing.')