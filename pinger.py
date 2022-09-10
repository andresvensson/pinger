import os
import sqlite3
import sys
import platform
import subprocess
import time

import config
import _sqlite3
import pymysql
from datetime import datetime


# Pinger script as of 2022-08-27
#
# Notes
# db structure: One database, one table, one row for every server
#

# CONFIG
save_to_database = True


def start():
    # delay execute to free cpu cycles due to other codes running at same time.
    #time.sleep(5)
    # read servers list from separate text file, timestamp
    if os.path.isfile('config.py'):
        report = {'source': config.source, 'server_list': get_server_list(), 'timestamp': datetime.now()}
    else:
        print("ERROR: missing file 'config.py' in root directory. Please create the file")
        sys.exit()

    # ping servers
    report['server_online'] = get_server_status(report)

    # save to local database and push to remote database
    if save_to_database:
        save_values(report)
    else:
        # print dict
        print("\n\nREPORT DICT:\n", report)
        print("\n\nEnd")


def get_server_list():
    print("read server list")

    if os.path.isfile('server_watchlist.txt'):
        with open('server_watchlist.txt') as f:
            content = f.read().splitlines()
        return content
    else:
        print("ERROR: missing file 'server_watchlist.txt' in root directory. Please create the file")
        # add a helper? Maybe later
        sys.exit()


def get_server_status(report):
    print("STATUS")
    status = {}
    for s in report['server_list']:
        if ping(s) == 0:
            # host offline
            status[str(s)] = 0
        else:
            # host online
            status[str(s)] = 1
    return status


def ping(host):
    """
        Returns True if host (str) responds to a ping request.
        Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
        """

    # Option for the number of packets as a function of
    param = '-n' if platform.system().lower() == 'windows' else '-c'

    # Building the command. Ex: "ping -c 1 google.com"
    command = ['ping', param, '1', host]
    # command = ['ping', param, '1', host, '2>&1 > /dev/null']

    return subprocess.call(command) == 0


def save_values(report):
    # Local sqlite3 save
    save_local(report)
    print("\nLocal save ok\n\nREPORT DICT:\n", report)

    # Remote sql save (if online)
    if report['server_online'][config.domain]:
        # First add missing values to remote database
        get_missing_values()
        save_remote(report)
        print("\nRemote save ok")
    else:
        print("remote host offline")
        save_missing_values(report)


def save_local(report):
    """
    can browse this in shell. Useful commands:
    sqlite3
    .open database.db
    .tables
    select * from status;
    """
    conn_sqlite = sqlite3.connect('database.db')
    c3 = conn_sqlite.cursor()
    c3.execute("""CREATE TABLE IF NOT EXISTS status (id INTEGER NOT NULL PRIMARY KEY, source TEXT, timestamp 
    CURRENT_TIMESTAMP, online INTEGER, host TEXT);""")
    conn_sqlite.commit()

    for s in report['server_online']:
        values = (report['source'], report['timestamp'], report['server_online'][s], s)
        c3.execute("INSERT INTO status VALUES (NULL, ?, ?, ?, ?);", values)

    conn_sqlite.commit()
    conn_sqlite.close()


def save_missing_values(report):
    conn_sqlite = sqlite3.connect('database.db')
    c3 = conn_sqlite.cursor()
    c3.execute("""CREATE TABLE IF NOT EXISTS missing_values (id INTEGER NOT NULL PRIMARY KEY, source TEXT, timestamp 
    CURRENT_TIMESTAMP, online INTEGER, host TEXT);""")
    conn_sqlite.commit()

    for s in report['server_online']:
        values = (report['source'], report['timestamp'], report['server_online'][s], s)
        c3.execute("INSERT INTO status VALUES (NULL, ?, ?, ?, ?);", values)

    conn_sqlite.commit()
    conn_sqlite.close()


def get_missing_values():
    print("get missing values pls")
    conn_sqlite = sqlite3.connect('database.db')
    c3 = conn_sqlite.cursor()
    try:
        c3.execute("SELECT * FROM missing_values;")
        data = c3.fetchall()
        conn_sqlite.commit()
    except sqlite3.OperationalError:
        print("No missing values (no database named 'missing_values')")
        data = None

    if data:
        report = {'source': config.source}
        status = {}
        for row in data:
            report['timestamp'] = row[2]
            status[str(row[4])] = row[3]

        report['server_online'] = status
        save_remote(report)
        print("saved missing values")

        # clean up missing table
        c3.execute("DROP TABLE IF EXISTS missing_values;")
        conn_sqlite.close()
    else:
        return


def save_remote(report):
    db = pymysql.connect(host=config.domain, user=config.username, password=config.password, db="ping")
    cursor = db.cursor()

    # Check below! Error 1064: You have an error in your SQL syntax
    sql_string = "CREATE TABLE IF NOT EXISTS status (value_id INT NOT NULL AUTO_INCREMENT, source TEXT, timestamp " \
                 "DATETIME, online BOOLEAN, host TEXT, PRIMARY KEY(value_id));"
    try:
        cursor.execute(sql_string)
        db.commit()

        format_tid = "%d-%m-%y %H:%M:%S.%f"
        tid = datetime.strftime(report['timestamp'], format_tid)

        for s in report['server_online']:
            values = None, report['source'], tid, report['server_online'][s], s
            sql_string = "INSERT INTO status VALUES (%s, %s, %s, %s, %s);"
            print("\nSQL LINE:", sql_string, "\nVALUES:", values)
            cursor.execute(sql_string, values)
        db.commit()
        db.close()

    except pymysql.Error as e:
        db.rollback()
        print("Error %d: %s" % (e.args[0], e.args[1]))


if __name__ == "__main__":
    start()
