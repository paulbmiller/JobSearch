"""
Setup for a database of job applications using SQLite with some useful
functions to store the data and access it.
"""

import sqlite3
from sqlite3 import Error
from sqlite3 import IntegrityError


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
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


def new_application(date, description, company_name, city, internship,
                    link='', status=1, platform='LinkedIn', db=r"jobsearch.db"):
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
    

def get_application(company_name, db=r"jobsearch.db"):
    """
    Note : SQL's UPPER function does not do change the é character, but
    Python's built-in upper does.
    """
    conn = create_connection(db)
    c = conn.cursor()
    
    c.execute("""SELECT applications.id, date, description, name
              FROM applications
              JOIN companies ON applications.company_id = companies.id
              WHERE UPPER(name) LIKE '%{}%'
              ORDER BY date ASC""".format(company_name.upper()))
              
    res = c.fetchall()
              
    conn.close()
    
    return res
    

def set_application_status(application_id, status, db=r"jobsearch.db"):
    conn = create_connection(db)
    c = conn.cursor()
    
    c.execute("""UPDATE applications SET status = {}
              WHERE id = {}""".format(status, application_id))
    
    conn.commit()
    conn.close()


def get_applications(db=r"jobsearch.db"):
    conn = create_connection(db)
    c = conn.cursor()
    
    c.execute("""SELECT * FROM applications ORDER BY date ASC;""")
    
    res = c.fetchall()
    
    conn.close()
    
    return res


def get_event_types(db=r"jobsearch.db"):
    conn = create_connection(db)
    c = conn.cursor()
    
    c.execute("""SELECT * FROM event_types;""")
    
    res = c.fetchall()
    
    conn.close()
    
    return res


def add_event(event_type_id, application_id, date, db=r"jobsearch.db"):
    conn = create_connection(db)
    c = conn.cursor()
    
    c.execute("""INSERT INTO event (application_id, date, event_type)
              VALUES ({}, '{}', {})""".format(application_id,
              date, event_type_id))
    
    conn.commit()
    conn.close()


def add_video_call(application_id, date, db=r"jobsearch.db"):
    add_event(1, application_id, date, db)


def add_phone_call(application_id, date, db=r"jobsearch.db"):
    add_event(2, application_id, date, db)


def add_online_test(application_id, date, db=r"jobsearch.db"):
    add_event(3, application_id, date, db)


def add_interview(application_id, date, db=r"jobsearch.db"):
    add_event(4, application_id, date, db)


def add_offline_test(application_id, date, db=r"jobsearch.db"):
    add_event(5, application_id, date, db)


def add_rejection(application_id, date, db=r"jobsearch.db"):
    add_event(6, application_id, date, db)
    set_application_status(application_id, 3, db)


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
        status text NOT NULL,
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
    
    
    
    