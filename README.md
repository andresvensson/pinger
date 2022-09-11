PINGER

<sub>Monitors uptime for servers as your choosing.</sub>

REQUIREMENTS

<sub>python librarys, SQL database</sub>


INSTALL

<sub>1, clone repo

<sub>2, make sure to set your configuration. Code will create templates if files not exists:

<sub>*/config.py*
 (your local client name and remote database user, pass, hostname)</sub>

<sub>*/server_watchlist.txt*

  <sub>(example.com
		example1.com)</sub>
  
<sub>3, add code executable to crontab</sub>
	
		
FUNCTIONS

<sub>Ping clients
log response (online/offline)
save results in local DB and remote DB</sub>


	
TODO

<sub>present in webpage with graph? and stats?</sub>
