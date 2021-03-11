"""
Setup for a database of job applications using SQLite with some useful
functions to store the data and access it.
"""

import sqlite3
from sqlite3 import Error
from sqlite3 import IntegrityError
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


def new_application(description, company_name, city, internship,
                    date=datetime.now().strftime('%Y-%m-%d'), link='',
                    status=1, platform='LinkedIn', db=r"jobsearch.db"):
    """
    Add a row to the ´applications´ table. Date format is YYYY-MM-DD.
    """
    conn = create_connection(db)
    c = conn.cursor()
    
    c.execute("""SELECT name FROM companies;""")
    
    companies = [row[0] for row in c.fetchall()]
    
    if company_name not in companies:
        c.execute("""INSERT INTO companies (name) VALUES ('{}');""".format(
            company_name))
    
    c.execute("""SELECT id FROM companies WHERE name = '{}';""".format(
        company_name))
    
    company_id = c.fetchone()[0]
    
    c.execute("""INSERT INTO applications (date, description, company_id,
              internship, city, status, link, platform) VALUES ('{}', '{}', {},
                 {}, '{}', '{}', '{}', '{}');""".format(date, description,
                    company_id, internship, city, status, link, platform))
    
    conn.commit()
    conn.close()
    

def get_application(company_name, ignore_rejected=True, db=r"jobsearch.db"):
    """
    Note : SQL's UPPER function does not do change the é character, but
    Python's built-in upper does.
    """
    if not ignore_rejected:
        return exec_sql("""SELECT applications.id, date, description, name, link
                        FROM applications
                        JOIN companies ON applications.company_id = companies.id
                        WHERE UPPER(name) LIKE '%{}%'
                        ORDER BY date ASC""".format(company_name.upper()))
                        
    else:
        return exec_sql("""SELECT applications.id, date, description, name, link
                        FROM applications
                        JOIN companies ON applications.company_id = companies.id
                        WHERE UPPER(name) LIKE '%{}%' AND status != 3
                        ORDER BY date ASC""".format(company_name.upper()))


def get_application_from_id(application_id, db=r"jobsearch.db"):
    app = exec_sql("""SELECT * FROM applications 
                   JOIN companies  ON applications.company_id = companies.id
                   JOIN status ON applications.status = status.id
                   WHERE applications.id = {};
                   """.format(
                   application_id))
    
    return app[0]


def app_details(application_id, db=r"jobsearch.db"):
    app_list = list(get_application_from_id(application_id, db))
    
    # Delete unwanted values
    del app_list[3]
    del app_list[5]
    del app_list[7]
    del app_list[8]
    
    # Yes and no for internship instead of 1 and 0
    app_list[3] = 'Yes' if app_list[3] == 1 else 'No'
    
    output = 'Application id: {}\n'
    output += 'Date of application: {}\n'
    output += 'Description: {}\n'
    output += 'Is internship: {}\n'
    output += 'City: {}\n'
    output += 'Link: {}\n'
    output += 'Platform: {}\n'
    output += 'Company name: {}\n'
    output += 'Status: {}\n'
    
    print(output.format(*app_list))


def set_application_status(application_id, status, db=r"jobsearch.db"):
    exec_sql("""UPDATE applications SET status = {}
             WHERE id = {}""".format(status, application_id))


def get_applications(db=r"jobsearch.db"):
    return exec_sql("""SELECT * FROM applications ORDER BY date ASC;""")


def get_event_types(db=r"jobsearch.db"):
    return exec_sql("""SELECT * FROM event_types;""")


def add_event(event_type_id, application_id,
              date=datetime.now().strftime('%Y-%m-%d'), db=r"jobsearch.db"):
    conn = create_connection(db)
    c = conn.cursor()
    
    c.execute("""INSERT INTO events (application_id, date, event_type)
              VALUES ({}, '{}', {})""".format(application_id,
              date, event_type_id))
    
    conn.commit()
    conn.close()


def add_video_call(application_id, date=datetime.now().strftime('%Y-%m-%d'),
                   db=r"jobsearch.db"):
    add_event(1, application_id, date, db)
    set_application_status(application_id, 2, db)


def add_phone_call(application_id, date=datetime.now().strftime('%Y-%m-%d'),
                   db=r"jobsearch.db"):
    add_event(2, application_id, date, db)
    set_application_status(application_id, 2, db)


def add_online_test(application_id, date=datetime.now().strftime('%Y-%m-%d'),
                    db=r"jobsearch.db"):
    add_event(3, application_id, date, db)
    set_application_status(application_id, 2, db)


def add_interview(application_id, date=datetime.now().strftime('%Y-%m-%d'),
                  db=r"jobsearch.db"):
    add_event(4, application_id, date, db)
    set_application_status(application_id, 2, db)


def add_offline_test(application_id, date=datetime.now().strftime('%Y-%m-%d'),
                     db=r"jobsearch.db"):
    add_event(5, application_id, date, db)
    set_application_status(application_id, 2, db)


def add_rejection(application_id, date=datetime.now().strftime('%Y-%m-%d'),
                  db=r"jobsearch.db"):
    add_event(6, application_id, date, db)
    set_application_status(application_id, 3, db)


def add_ask_more_info(application_id, date=datetime.now().strftime('%Y-%m-%d'),
                      db=r"jobsearch.db"):
    add_event(7, application_id, date, db)
    set_application_status(application_id, 2, db)


def add_offer(application_id, date=datetime.now().strftime('%Y-%m-%d'),
              db=r"jobsearch.db"):
    add_event(8, application_id, date, db)
    set_application_status(application_id, 2 ,db)


def time_to_respond(application_id, ignore_ongoing=True, db=r"jobsearch.db"):
    res = exec_sql(
        """SELECT applications.date, events.date FROM applications
        JOIN events ON events.application_id = applications.id
        JOIN event_types ON event_types.id = events.event_type
        WHERE applications.id = {}
        ORDER BY events.date ASC;""".format(application_id),
        db=db)
    
    if len(res) > 0:
        apply_date = datetime.strptime(res[0][0], '%Y-%m-%d')
        response_date = datetime.strptime(res[0][1], '%Y-%m-%d')
        return (response_date - apply_date).days
        
    else:
        if ignore_ongoing:
            return None
        else:
            today_dt = datetime.today()
            apply_date = datetime.strptime(
                get_application_from_id(application_id)[1],'%Y-%m-%d')
            return (today_dt - apply_date).days


def plot_rejections(dates):
    for date in dates.keys():
        dates[date] = sum(dates[date])/len(dates[date])
    
    x, y = zip(*sorted(dates.items()))
    
    plt.plot(x, y)
    plt.show()


def stats_rejections(ignore_ongoing=True, db=r"jobsearch.db"):
    res = exec_sql("""SELECT id FROM applications;""")
    
    res = [el[0] for el in res]
    
    max_time = 0
    max_app_id = None
    reject_times = []
    # Dictionary containing dates to datetime objects of rejection times
    dates = {}
    
    for app_id in res:
        date = datetime.strptime(get_application_from_id(app_id, db)[1],
                                 '%Y-%m-%d')
        time = time_to_respond(app_id, ignore_ongoing)
        reject_times.append(time)
        
        if time:
            if time > max_time:
                max_time = time
                max_app_id = app_id
            if date in dates.keys():
                dates[date].append(time)
            else:
                dates[date] = [time]
    
    reject_times = np.array([time for time in reject_times if time])
    
    max_time = reject_times.max()
    
    stats = (reject_times.mean(), reject_times.std(), reject_times.max(),
             max_app_id)
    
    print("{}/{} Rejection stats".format(len(reject_times), len(res)))
    print("Average : {:.2f}".format(stats[0]))
    print("Standard deviation : {:.2f}".format(stats[1]))
    print("Max : {}".format(stats[2]))
    print("Application with max time : {}".format(
        get_application_from_id(max_app_id)))
    
    plot_rejections(dates)
    
    return stats


def exec_sql(command, db=r"jobsearch.db"):
    conn = create_connection(db)
    c = conn.cursor()
    
    c.execute(command)
    
    res = c.fetchall()
    
    conn.commit()
    conn.close()
    
    return res


def get_events(ignore_rejected=False, ignore_rejections=True,
               db=r"jobsearch.db"):
    command = """SELECT
        applications.id,
        events.id,
        applications.description,
        applications.city,
        companies.name,
        events.date,
        event_types.description
        FROM events
        JOIN event_types ON event_types.id = event_type
        JOIN applications ON applications.id = events.application_id
        JOIN companies ON companies.id = applications.company_id"""
    
    if ignore_rejected:
        command += """ WHERE applications.status != 3"""
        if ignore_rejections:
            command += """ AND events.event_type != 6"""
        command += ";"
        
    else:
        if ignore_rejections:
            command += """ WHERE events.event_type != 6"""
        command += ";"
    
    res = exec_sql(command)
    
    res.sort(key=lambda x: x[5])
    
    return res


def get_app_events(application_id, db=r"jobsearch.db"):
    command = """SELECT
        applications.id,
        events.id,
        applications.description,
        applications.date,
        applications.city,
        companies.name,
        events.date,
        event_types.description
        FROM events
        JOIN event_types ON event_types.id = event_type
        JOIN applications ON applications.id = events.application_id
        JOIN companies ON companies.id = applications.company_id
        WHERE applications.id = {};""".format(application_id)
        
    res = exec_sql(command)
    
    if len(res) < 1:
        print("No events for application with id {}".format(application_id))
    else:
        res.sort(key=lambda x: x[5])
        
        print("Application id: {}".format(res[0][0]))
        print("Application description: {}".format(res[0][2]))
        print("Date of application: {}".format(res[0][3]))
        print("City: {}".format(res[0][4]))
        print("Company: {}".format(res[0][5]))
        
        for event in res:
            print("Event id: {}".format(event[1]))
            print("Event date: {}".format(event[6]))
            print("Event: {}".format(event[7]))


def get_formatted_events(ignore_rejected=False, ignore_rejections=True,
                         db=r"jobsearch.db"):
    res = get_events(ignore_rejected, ignore_rejections, db)
    
    output = ""
    
    for event in res:
        output += 'Application id : {}\n'.format(event[0])
        output += 'Event id : {}\n'.format(event[1])
        output += 'Desc : {}\n'.format(event[2])
        output += 'City : {}\n'.format(event[3])
        output += 'Company : {}\n'.format(event[4])
        output += 'Date : {}\n'.format(event[5])
        output += 'Event type : {}\n'.format(event[6])
        output += '\n'
    
    print(output)


def get_running_apps():
    get_formatted_events(True)


if __name__ == '__main__':
    db = r"jobsearch.db"
    
    conn = create_connection(db)
    
    c = conn.cursor()
    
    create_applications = """CREATE TABLE IF NOT EXISTS applications (
        id integer PRIMARY KEY NOT NULL,
        date text NOT NULL,
        description text NOT NULL,
        company_id integer,
        internship integer NOT NULL,
        city text NOT NULL,
        status integer NOT NULL,
        link text NOT NULL,
        platform text NOT NULL,
        FOREIGN KEY (company_id) REFERENCES companies(id)
    ); """
    
    create_companies = """CREATE TABLE IF NOT EXISTS companies (
        id integer PRIMARY KEY NOT NULL,
        name text NOT NULL
    ); """
    
    create_event_types = """CREATE TABLE IF NOT EXISTS event_types (
        id integer PRIMARY KEY NOT NULL,
        description text NOT NULL
    ); """
    
    create_events = """CREATE TABLE IF NOT EXISTS events (
        id integer PRIMARY KEY NOT NULL,
        application_id integer,
        date text NOT NULL,
        event_type integer,
        FOREIGN KEY (application_id) REFERENCES applications(id),
        FOREIGN KEY (event_type) REFERENCES event_types(id)
    ); """
                                                                
    create_status = """CREATE TABLE IF NOT EXISTS status (
        id integer PRIMARY KEY NOT NULL,
        status text NOT NULL
    ); """
    
    create_table(conn, create_applications)
    create_table(conn, create_companies)
    create_table(conn, create_event_types)
    create_table(conn, create_events)
    create_table(conn, create_status)
    
    try:
        c.execute("""INSERT INTO event_types (id, description)
                  VALUES (1, 'VIDEO CALL');""")
    except IntegrityError:
        pass
    
    try:
        c.execute("""INSERT INTO event_types (id, description)
                  VALUES (2, 'PHONE CALL');""")
    except IntegrityError:
        pass
    
    try:
        c.execute("""INSERT INTO event_types (id, description)
                  VALUES (3, 'ONLINE TEST');""")
    except IntegrityError:
        pass
    
    try:
        c.execute("""INSERT INTO event_types (id, description)
                  VALUES (4, 'INTERVIEW');""")
    except IntegrityError:
        pass
    
    try:
        c.execute("""INSERT INTO event_types (id, description)
                  VALUES (5, 'OFFLINE TEST');""")
    except IntegrityError:
        pass
    
    try:
        c.execute("""INSERT INTO event_types (id, description)
                  VALUES (6, 'REJECTED');""")
    except IntegrityError:
        pass
    
    try:
        c.execute("""INSERT INTO event_types (id, description)
                  VALUES (7, 'ASK MORE INFO');""")
    except IntegrityError:
        pass
    
    try:
        c.execute("""INSERT INTO event_types (id, description)
                  VALUES (8, 'OFFER');""")
    except IntegrityError:
        pass
    
    try:
        c.execute("""INSERT INTO status (id, status)
                  VALUES (1, 'no response');""")
    except IntegrityError:
        pass
    
    try:
        c.execute("""INSERT INTO status (id, status)
                  VALUES (2, 'ongoing');""")
    except IntegrityError:
        pass
    
    try:
        c.execute("""INSERT INTO status (id, status)
                  VALUES (3, 'negative');""")
    except IntegrityError:
        pass
    
    conn.commit()
    conn.close()
    
    
    
    