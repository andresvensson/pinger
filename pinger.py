import os
import sys
import platform
import subprocess


# Pinger script as of 2022-08-27
#
# Notes
# db structure: One database, one row for every server
# How to determinate missing values in remote db?


def start():
    # read servers list from separate text file
    report = {'server_list': get_server_list()}

    # ping servers
    report['server_online'] = get_server_status(report)

    print("\nsave to local db")  # sqlite3?
    print("save to remote db")
    print("\nPrint result:\n", report)


def get_server_list():
    print("read server list")

    if os.path.isfile('server_watchlist.txt'):
        with open('server_watchlist.txt') as f:
            content = f.read().splitlines()
        return content
    else:
        print("ERROR: missing file 'server_watchlist.txt' in root directory. Please create the file")
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


if __name__ == "__main__":
    start()
