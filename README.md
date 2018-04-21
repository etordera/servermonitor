# servermonitor
A python script for monitoring services on your servers.

### Description
The script verifies that your servers are up and running and sends an alert e-mail if something is wrong. It also generates an HTML report of servers status. You can place the HTML report inside your http server's document root and make it accessible for remote status checking.

The script needs a configuration file in INI format (see below for details).

---

### Usage
Call the script with just one parameter: the path to the configuration file.
```
./servermonitor.py config.ini
```
You can set up a cron job and call the script periodically for continuous monitorization. For instance, if you want to check your servers every 5 minutes, add something like this to your `crontab`:
```
*/5 * * * * root /path/to/servermonitor.py /path/to/config.ini
```

---

### The configuration file
The configuration file is an INI file:
* A mandatory `[servermonitor]` section is required, with main configuration data.
* Add new sections for every service you want to check. Name of the service definition sections can be whatever you want, except `[servermonitor]`.
* A basic sample of a configuration file is included in the project (`sample_config.ini`)

#### [servermonitor] section
**outputpath** = _Optional_ Path to output HTML report.  
**livestatus** = _Optional_ URL where output HTML report will be accessible.  
**smtpserver** = SMTP server (for alert e-mails)  
**smtpuser** = SMTP user for authentication  
**smtppassword** = STMP password for authentication  
**smtpfrom** = FROM address for e-mails  
**smtpto** = Comma separated list of destination e-mails for alerts  

#### [service] sections
Common keys:  
**type** = _Optional_ ftp, ftps, http, https or service. Default: service.  
**host** = Server's hostname  
**port** = Port number for service being monitored. Mandatory for type=service, defaults provided for other types.  
**timeout** = _Optional_ Timeout for connection attempts (seconds). Default: 10 seconds.  
**allowedfailures** = _Optional_ Number of failed checks allowed before sending an alert. Defaults to 1.
  
Keys for types ftp and ftps:  
**user** = _Optional_ Username for FTP/FTPS authentication. Defaults to anonymous.  
**password** = _Optional_ Password for FTP/FTPS authentication. Defaults to anonymous.  
**testdir** = _Optional_ Path to directory to be checked after connection to FTP server.  
  
Keys for types http and https:  
**document** = _Optional_ Document to check on http(s) server. Defaults to root document ('/').  
