STG DATABASE PROJECT
====================

Written by Albert W. Hamood, former member of the Marder Lab, December 2015.

Original repository @ https://github.com/alhamood/STG-database-project

Have questions? Email me at alhamood@brandeis.edu


OUTLINE
=======

This project includes the files for running a database server to manage data from 
preparations of the stomatogastric ganglion (STG). It manages user account for uploading
of data (anyone can download). In includes privileges for an administrator account
that can activate users for uploads, delete users, and manage all experiments. Users
can enter experiments, which are defined first by metadata. Then they enter processed
data (such as frequency and phase relationships) for a baseline condition. Following 
this users may add more conditions and associated processed data. Users may also upload 
files to associate with these experiments.


REQUIREMENTS
============

This code is written using Python 2.7, and depends on several python modules. Those most
likely to need installation include pandas, Flask, Flask-Login, and WTForms. 


GETTING THE SERVER RUNNING
==========================

The project should run straight away as currently distributed, once all the appropriate
modules are in place in python. It depends on finding the following:

- A config.json file in the main directory, described below
- Directory specified for file uploads in config.json must exit (/files by default)
- A /databases subdirectory must exist and include: user_database.json, containing user
information; user_pdatabase.json, containing hashed user password information for logins;
processed_data.json, containing processed data for all conditions; and metadata.json, 
containing metadata for all entered experiments. Base forms of these files are included
in this distribution in /Database-seeds
- A /static subdirectory including the image file crabs.jpg
- A /templates subdirectory containing all the .html templates used to serve webpages

All these files should be in the basic distribution on github.

When ready, start the server from the terminal by running:

**sudo python app.py**

This must be run as sudo, or the server will not be able to create and remove directories,
or save uploaded files. It will crash in this case.


WORKFLOW FOR EXPERIMENTERS
==========================

To include your data in the STG database, you will first need to create an account on the
server. This can be done by the "Create new account" link on the homepage. Following this,
your account will need to be activated for uploads by the administrator before you are
allowed to upload files or enter new experiments. Email the administrator to ask for this
activation; a link to send the administrator an email is on the homepage.

Once you have followed this procedure and have an activated account, you may log in and 
enter experiments. Basic details about accounts such as user info and password can be
edited by following links from the home page once signed in.

Remember to sign-out from the home page when finished! Currently there is no auto-sign-out
functionality.


Entering a new experiment
-------------------------

From the homepage, click on the "My Experiments Page" link. This takes you to a page that
shows the metadata for all the experiments you have entered so far. Under "Other options",
click "Enter a new experiment". 

You will then be prompted to enter metadata for the experiment including a name (such as 
lab notebook page), experiment date, species and saline information, lab, as well as a free-
form space for entering notes about your experiment. The only required field here is 
experiment date, but please enter all data that are available.

The next step is to enter processed data for a "baseline" condition. PLEASE MAKE SURE 
BASELINE DATA ARE FROM A FRONT-END ON, UNMANIPULATED PREP! Other conditions should be 
entered as new conditions. There are no required fields for processed data.

After submitting you will be taken to the experiment page.


Experiment page
---------------

This page first shows you a list of all the conditions of your experiment. Upon creating 
a new experiment, this will include only baseline data. If you also have processed data
from another condition (such as after decentralization, or in the presence of a drug),
enter this by clicking on the link for "new condition" in "More options". This will take
you to a page to enter a new set of processed data that will be associated with this 
condition. 


Uploading files
---------------

The experiment page shows you a list of all uploaded files for this experiment. You may
delete or upload a new file by following the links under "More options". Please note, 
there is a maximum filesize (100 MB by default), a maximum number of files per experiment
(15 by default), and a set of allowed file extensions. These parameters can be changed
by editing the config.json file.


Editing and deleting conditions
-------------------------------

You can edit or delete previously entered condition processed data by entering a
condition: enter its index (leftmost column of the html table), choose your option
from the dropdown "Action" button, and click "Act on condition".


Editing and deleting experiments and metadata
---------------------------------------------

To delete or edit a previously entered experiment, select the experiment by entering its
index (on the experiments page), choose the appropriate option from the "Action" dropdown,
and click "Act on experiment". The "Edit / Upload Data (conditions and files)" option will
take you to the Experiment page as described above.


DOWNLOADING DATA
================

No log-in is required to download metadata, processed data, or uploaded files. These 
options can be found by following a link for the "Download Page", for example from the
home page.


Metadata and processed data for all conditions
----------------------------------------------

These can be viewed or downloaded as .json or .csv files. For metadata, there is also an
option to download without the "Notes" field. This field allows large text inputs and 
may make .csv files unwieldy. 


Uploaded files
--------------

Following this link first prompts the user to select an experiment by metadata. It then
displays a list of uploaded files associated with this experiment, which may be selected
and downloaded by entering the file index and clicking the download button.


ADMINISTRATOR FUNCTIONS
=======================

config.json
-----------

This file can be edited with a text editor (nothing fancy! TextEdit on Mac, for example,
tends to change the " marks to something python will no longer understand). The parameters
are:

- "FilePath" : This specifies the path where uploaded files are stored. Must exist!
- "AllowedFiletypes" : The extensions that are allowable for user file uploads
- "MaxUsers" : This is the maximum number of allowed user accounts that can be created.
- "MaxFilesizeMB" : Maximum allowed filesize for uploaded files, in megabytes
- "MaxFiles" : The maximum number of files that may be uploaded per experiment
- "MaxUserExperiments" : Maximum number of experiments that may be created by one user
- "UploadsAllowed" : 1 allows uploads, anything else disables all uploads
- "DownloadsAllowed" : 1 allows downloads, anything else disables all downloads
- "EditsAllowed" : 1 allows editing, anything else disables all editing


Admin server account
--------------------

This account is named "Admin". It must exist and the server itself will not allow it to be
deleted. Logging in as Admin grants full privileges over all uploaded experiments 
including editing, deleting, and uploading files and metadata. It also allows access to
the Admin page (from a link on the home page).


Admin page
----------

From here user accounts can be edited, activated and deactivated for uploads, and deleted.
The admin may also reset the password for any user, whereupon the server generates a 
new random password. This password must be manually supplied to the user! The server
will not send an email to the user with this password. The Admin should email this 
password to the user who should then log in and immediate change it.

Note: Deleting a user does not delete all of the user's uploaded experiments. At 
present, if you want to delete all of a user's experiments, it must be done one by one
from the experiments page. Admin can do this. One may also write a script to remove them
from the .json file processed_data.json, but be careful not to screw up the file! Simply
removing the entries with keys containing the deleted username will not upset anything
if done properly. 

Remember to sign-out from the home page when finished! Currently there is no auto-sign-out
functionality.


password_tool.py
----------------

This is a simple script that resets the Admin password, if it is ever forgotten. Run it
from the terminal in the main project directory by $ python password_tool.py