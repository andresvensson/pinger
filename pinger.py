

# Pinger script as of 2022-08-27
#
# db structure: One database, one row for every server


def start():
    report = dict
    print("get servers list")
    get_server_list(report)
    print("ping servers")
    print("save to local db")
    print("save to remote db")


def get_server_list(report):
    print("read server list")


def create_report(data):
    report = "Server Report\n"
    data['report'] = report
    for p in data['logfile']:
        # print(p + ":", data['logfile'][p])
        with open(data['logfile'][p]) as f:
            content = f.readlines()
            print("CONTENT:", content)
            txt = p + "\n" + str(content)
            data['report'] += txt

    return data









if __name__ == "__main__":
    start()