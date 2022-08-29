import os
import sqlite3
import sys
import platform
import subprocess
import config
import _sqlite3
import pymysql


# Pinger script as of 2022-08-27
#
# Notes
# db structure: One database, one table, one row for every server
#

# CONFIG
save_to_database = False

conn_sqlite = sqlite3.connect('database.db')
c3 = conn_sqlite.cursor()


def start():
    # read servers list from separate text file
    report = {'server_list': get_server_list()}

    # ping servers
    report['server_online'] = get_server_status(report)

    # save to local database and push to remote database
    if save_to_database:
        save_values(report)
    else:
        print("\nPrint result:\n", report)


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
            status[str(s)] = False
        else:
            # host online
            status[str(s)] = True
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
    # local sqlite3 save
    #save_local(report)


def save_local(report):
    print("SAVE??")
    c3.execute("""CREATE TABLE IF NOT EXISTS status (id INTEGER NOT NULL PRIMARY KEY, host TEXT, online INTEGER)""")
    conn_sqlite.commit()

    for s in report['server_online']:
        print("insert all values")

    sql_statement = "INSERT INTO status VALUES (", report[]
    c3.execute("INSERT INTO status VALUES ()")


if __name__ == "__main__":
    start()
