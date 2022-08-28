import os
import sys
import platform
import subprocess


# Pinger script as of 2022-08-27
#
# db structure: One database, one row for every server


def start():
    report = {}
    # get servers list from separate text file
    report['server_list'] = get_server_list(report)

    print(report)

    print("ping servers")
    report['server_status'] = get_server_status(report)

    print("save to local db")
    print("save to remote db")
    print(report)


def get_server_list(report):
    print("read server list")

    if os.path.isfile('server_watchlist.txt'):
        with open('server_watchlist.txt') as f:
            content = f.read().splitlines()
        return content
    else:
        print("ERROR: missing file 'server_watchlist.txt' in root directory. Please create the file")
        sys.exit()


def get_server_status1(report):
    print("STATUS")
    for s in report['server_list']:
        report['server_status'] = {str(s): ping(s)}
        if ping(s) == 0:
            report['server_status'] = {str(s): True}
        else:
            report['server_status'] = {str(s): False}
    return report


def get_server_status(report):
    print("STATUS")
    report['server_status'] = {}
    for s in report['server_list']:
        if ping(s) == 0:
            # host online
            report['server_status'] = {str(s): True}
        else:
            # host offline
            report['server_status'] = {str(s): False}
    return report


def ping(host):
    """
        Returns True if host (str) responds to a ping request.
        Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
        """

    # Option for the number of packets as a function of
    param = '-n' if platform.system().lower() == 'windows' else '-c'

    # Building the command. Ex: "ping -c 1 google.com"
    command = ['ping', param, '1', host]

    return subprocess.call(command) == 0






if __name__ == "__main__":
    start()