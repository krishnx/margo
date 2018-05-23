# margo
The events project.

app.py is the main driver file.
Run the following command:
python app.py

The logs will be available at the following directory:
/tmp/margo.log

Project Structure:
app.py : This program runs the application.

config.ini : This file stores the configurations needed for the application.

local_database.py : Connects to the local events database.

logger_mod.py : This is the logger module.

requirements.txt : Lists all the required modules. Run `pip -r requirements.txt` to install all the required modules.

static/custom_form.js : This js file has included the essential functions needed across the web pages.

static/jquery-3.3.1.min.js : To include jQuery.

templates/add.html : The HTML form to add events to the database.

templates/edit.html : The HTML form to edit events to the database.

templates/events.html : The list of all events.

templates/index.html : The home page.

events.sql : is the sql dump file. Load this file to create the database.
