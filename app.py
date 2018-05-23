from flask import Flask, render_template, request, json
from local_database import L_DAO
import ConfigParser
from logger_mod import Logger
import os

# Initialize the app
app = Flask(__name__)

# Send email
def send_mail(sender, receiver, subject, message):
    sendmail_location = "/usr/sbin/sendmail" # sendmail location
    p = os.popen("%s -t" % sendmail_location, "w")
    p.write("From: %s\n" % sender #"krishnachandra.sharma@margonetworks.com")
    p.write("To: %s\n" % receiver # "krishnachandra.sharma@margonetworks.com")
    p.write("Subject: %s\n" % subject)
    p.write("\n") # blank line separating headers from body
    p.write(message)
    status = p.close()
    Logger.logger.info('Email sent with status: {0}'.format(status))

# Read from events data from events, data and user table.
def get_events_data():
    res = d.execute_query('''
      SELECT * FROM events
      LEFT JOIN data d ON events.data_id=d.id
      LEFT JOIN user u ON d.user_id=u.id;
    ''')

    return json.dumps({'result': res})

# Check if the threshold of events update is crossed.
def validate_event_frequency(ts):
    time_interval = config.get("ALERT", "mins_count") * 60
    events_count = config.get("ALERT", "events_count")

    query = '''
    SELECT COUNT(*) FROM events where timestamp {0} and {1};
    '''.format(ts-time_interval, ts)
    res = d.execute_query(query)
    if res[0] > events_count:
        send_mail("krishnachandra.sharma@margonetworks.com",
                  "krishnachandra.sharma@margonetworks.com",
                  "ALERT: subject",
                  "Holy mother of GOD! Threshold reached. Alert! {0} events were updated within {1} minutes.".format(res[0], time_interval/60))
        Logger.logger.error("Alert! {0} events were updated within {1} minutes.".format(res[0], time_interval/60))
        

# The index page.
@app.route("/")
def index():
    Logger.logger.debug("Loading index page.")
    return render_template("index.html")

# The events page.
@app.route("/events")
def show_events():
    Logger.logger.debug("Loading events page.")
    return render_template("events.html")

# Add events from this page.
@app.route('/events_add')
def add_event():
    Logger.logger.debug("Loading events' add page.")
    return render_template("add.html")

# Edit events from this page.
@app.route("/events_edit")
def edit_event():
    Logger.logger.debug("Loading events' edit page.")
    return render_template("edit.html")

# Get all events to show on the Add/Edit page.
def get_all_events():
    Logger.logger.debug("Getting all the events from db.")
    return get_events_data()

# Form to add event in the DB.
@app.route("/add_event_res", methods=['POST'])
def add_event_res():
    Logger.logger.debug("Adding new event to the db.")
    noun = request.form('noun')
    verb = request.form('verb')
    timestamp = request.form('timestamp')
    data_event_type = request.form('event_type')
    data_event_comments = request.form('comments')
    user_name = request.form('name')
    user_role = request.form('role')

    validate_event_frequency(timestamp)

    user_id = 0
    # Get the user if already exists.
    query = "select name from user where name like \"{0}\";".format(user_name)
    res = d.execute_query(query)
    if not res:
        Logger.logger.info("Adding event for new user.")
        query = '''
        INSERT INTO user (name, role)
        VALUES
        ("{0}", "{1}");
        SELECT LAST_INSERT_ID();
        '''.format(user_name, user_role)
        user_id = d.execute_query(query)
    else:
        user_id = res[0][0]
        Logger.logger.info("Adding event for {0} user.".format(user_id))

    query = '''
    INSERT INTO data (event_type, user_id, comments)
    VALUES
    ("{0}", {1}, "{2}");
    SELECT LAST_INSERT_ID();
    '''.format(data_event_type, user_id, data_event_comments)
    data_id = d.execute_query(query)

    query = '''
    INSERT INTO data (noun, verb, timestamp, data_id)
    VALUES
    ("{0}", "{1}", {2}, {3});
    '''.format(noun, verb, timestamp, data_id)
    res = d.execute_query(query)
    Logger.logger.debug("Result of adding query: {0}".format(res))

    return get_events_data()

# Form to edit event in the DB.
@app.route('/edit_event_res/<noun>', methods=['PUT'])
def edit_event_res(noun):
    Logger.logger.info("Editing event with {0} noun.".format(noun))
    verb = request.form('verb')
    data_event_type = request.form('event_type')
    data_event_comments = request.form('comments')

    d = L_DAO()
    event_query = '''
      UPDATE events SET verb="{0}"
      WHERE noun LIKE "{1}";
      SELECT id from events
      WHERE noun like "{1}";
    '''.format(verb, noun)
    data_id = d.execute_query(event_query)

    data_query = '''
    UPDATE data SET event_type="{0}", comments="{1}"
    WHERE id = {2};
    '''.format(data_event_type, data_event_comments, data_id[0][0])
    res = d.execute_query(data_query)
    Logger.logger.debug("Result of edit: {0}".format(res))

    return get_events_data()

# Driver.
if __name__ == "__main__":
    config = ConfigParser.ConfigParser()
    config.read('config.ini')
    d = L_DAO(
        config.get("MySQL_DB_CONFIG", "host"),
        config.get("MySQL_DB_CONFIG", "user"),
        config.get("MySQL_DB_CONFIG", "pwd"),
        config.get("MySQL_DB_CONFIG", "database")
    )
    Logger.logger.info("Starting the app.")
    app.run(debug=True)
