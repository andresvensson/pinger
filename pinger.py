import os
import sqlite3
import sys
import platform
import subprocess
import time

import config
import pymysql
from datetime import datetime


# Pinger script as of 2022-08-27
#
# Notes
# db structure: One database, one table, one row for every server
# data is saved as report at one timestamp containing all servers checked

# CONFIG
save_to_database = True
# seconds delay execute (free cpu cycles due to other codes running at same time)
DELAY = 0
# output information in terminal
print_information = False
# create log file
log_file = True


def start():
    # delay execute to free cpu cycles due to other codes running at same time.
    time.sleep(DELAY)

    # read servers list from separate text file, timestamp
    if os.path.isfile(config.install_dir + 'config.py'):
        report = {'source': config.source, 'server_list': get_server_list(), 'timestamp': datetime.now()}
    else:
        msg("ERROR: missing file 'config.py' in root directory. Please create file")
        sys.exit()

    # ping servers
    report['server_online'] = get_server_status(report)
    msg("checked " + str(len(report['server_online'])) + " servers")

    # save to local database and push to remote database
    if save_to_database:
        save_values(report)
    else:
        # print dict
        print("\n\nREPORT DICT:\n", report)
        print("\n\nEnd")
    msg("Code successfully executed!\n")
    # print("\nCode successfully executed!")


def get_server_list():

    if os.path.isfile(config.install_dir + 'server_watchlist.txt'):
        with open(config.install_dir + 'server_watchlist.txt') as f:
            content = f.read().splitlines()
        return content
    else:
        msg("ERROR: missing file 'server_watchlist.txt' in root directory. Please create file")
        sys.exit()


def get_server_status(report):
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

    # Remote sql save (if online)
    msg("try connection to remote database")
    if ping(config.domain):
        msg("remote database online, check if theres missing values")
        # First add missing values to remote database
        get_missing_values()
        save_remote(report)
    else:
        msg("FAILED: remote host offline")
        save_missing_values(report)


def save_local(report):
    """
    can browse this in shell. Useful commands:
    sqlite3
    .open database.db
    .tables
    select * from status;
    """
    conn_sqlite = sqlite3.connect(config.install_dir + 'database.db')
    c3 = conn_sqlite.cursor()
    c3.execute("""CREATE TABLE IF NOT EXISTS status (id INTEGER NOT NULL PRIMARY KEY, source TEXT, timestamp 
    CURRENT_TIMESTAMP, online INTEGER, host TEXT);""")
    conn_sqlite.commit()

    for s in report['server_online']:
        values = (report['source'], report['timestamp'], report['server_online'][s], s)
        c3.execute("INSERT INTO status VALUES (NULL, ?, ?, ?, ?);", values)

    conn_sqlite.commit()
    conn_sqlite.close()
    msg("saved " + str(len(report['server_online'])) + " values, local")


def save_missing_values(report):
    conn_sqlite = sqlite3.connect(config.install_dir + 'database.db')
    c3 = conn_sqlite.cursor()
    c3.execute("""CREATE TABLE IF NOT EXISTS missing_values (id INTEGER NOT NULL PRIMARY KEY, source TEXT, timestamp 
    CURRENT_TIMESTAMP, online INTEGER, host TEXT);""")
    conn_sqlite.commit()

    for s in report['server_online']:
        values = (report['source'], report['timestamp'], report['server_online'][s], s)
        c3.execute("INSERT INTO missing_values VALUES (NULL, ?, ?, ?, ?);", values)

    msg("saved " + str(len(report['server_online'])) + " missing values, local")
    conn_sqlite.commit()
    conn_sqlite.close()


def get_missing_values():
    conn_sqlite = sqlite3.connect('database.db')
    c3 = conn_sqlite.cursor()
    try:
        c3.execute("SELECT * FROM missing_values;")
        data = c3.fetchall()
        conn_sqlite.commit()
    except sqlite3.OperationalError:
        msg("No missing values (no local table named 'missing_values')")
        data = None

    if data:
        msg("found" + str(len(data)) + "missing values")
        report = {'source': config.source, 'timestamp': data[0][2]}
        status = {}
        for row in data:
            # gather all ping results from the same timestamp (one report)
            if report['timestamp'] == row[2]:
                status[str(row[4])] = row[3]
                report['server_online'] = status
            else:
                # new time series coming, save report first
                save_remote(report)
                report['timestamp'] = row[2]
                status[str(row[4])] = row[3]
                report['server_online'] = status
        # save last report
        save_remote(report)

        # clean up missing table
        c3.execute("DROP TABLE IF EXISTS missing_values;")
        conn_sqlite.close()
        msg("removed local missing_values table")
    else:
        return


def save_remote(report):
    db = pymysql.connect(host=config.domain, user=config.username, password=config.password, db="ping")
    cursor = db.cursor()

    sql_string = "CREATE TABLE IF NOT EXISTS status (value_id INT NOT NULL AUTO_INCREMENT, source TEXT, timestamp " \
                 "DATETIME, online BOOLEAN, host TEXT, PRIMARY KEY(value_id));"
    try:
        cursor.execute(sql_string)
        db.commit()
        """
        strftime - Datetime to String
        strptime - String to Datetime
        """

        # Programming with time is a nightmare
        if isinstance(report['timestamp'], datetime):
            tid = report['timestamp']
        else:
            format_tid = "%Y-%m-%d %H:%M:%S.%f"
            tid = datetime.strptime(report['timestamp'], format_tid)

        for s in report['server_online']:
            values = None, report['source'], tid, report['server_online'][s], s
            sql_string = "INSERT INTO status VALUES (%s, %s, %s, %s, %s);"
            cursor.execute(sql_string, values)
        db.commit()
        db.close()
        msg("saved " + str(len(report['server_online'])) + " values, remote")

    except pymysql.Error as e:
        db.rollback()
        msg("Error saving remote")
        print("Error %d: %s" % (e.args[0], e.args[1]))


def msg(x):
    ts = datetime.now()
    text = "[" + str(ts) + "] " + str(x) + "\n"
    if print_information:
        print(text)
    if log_file:
        ts_day = ts.strftime('%Y-%m-%d')
        filename = config.log_dir + "log_" + ts_day + ".txt"
        fp = open(filename, 'a')
        fp.write(text)
        fp.close()
    else:
        pass


if __name__ == "__main__":
    start()
