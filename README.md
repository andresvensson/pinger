PINGER

Monitors uptime for servers as your chosing.

INSTALL

1, clone repo

2, make sure to set your configuration. Code will create templates if files not exists:
/config.py
  your local unit and remote database user, pass, hostname
/server_watchlist.txt
  example.com
  example1.com
  
3, add code executable to crontab

FUNCTIONS
Ping clients
log response (online/offline)
save results in local DB and remote DB

TODO
present in webpage with graph? and stats?
