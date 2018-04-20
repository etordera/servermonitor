#!/usr/bin/python3
import ftplib
import http.client
import socket
from datetime import datetime
import os
from configparser import ConfigParser
from collections import OrderedDict
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from argparse import ArgumentParser

# Constants
DEFAULT_ALLOWED_FAILURES = 1
DEFAULT_TIMEOUT = 10

class bcolors:
    """Color code definitions for console output."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def printColour(text, color):
    """Prints message to stdout in color.

    Args:
        text (str): Message to print.
        color (bcolors): Color for the message.
    Returns:
        None
    """
    print(color + text + bcolors.ENDC)


def testFTP(server, port=21, user='anonymous', password='nobody@nowhere.com', directory='/', timeout=DEFAULT_TIMEOUT, secure=False):
    """Test connection to a FTP server.

    Args:
        server (str): FTP server hostname.
        port (int): FTP server port.
        user (str): Username for authentication.
        password (str): Password for authentication.
        directory (str): Existence of this directory will be checked.
        timeout (int): Timeout for network connection (seconds)
        secure (boolean): True for FTPS, False for FTP
    Returns:
        (boolean) True on success, False on error
    """
    result = False
    try:
        print('Testing FTP' + ('S' if secure else '') + ' server: ' + server + ':' + str(port) + '...')
        print('|-> ', end='')
        if secure:
            ftp = ftplib.FTP_TLS()
        else:
            ftp = ftplib.FTP()
        ftp.connect(host=server, port=port, timeout=timeout)
        print('Connected, ', end='')
        ftp.login(user=user, passwd=password)
        print('logged in, ', end='')
        ftp.cwd(directory)
        print(directory + ' directory checked, ', end='')
        ftp.quit()
        printColour('Test OK', bcolors.OKGREEN)
        result = True
    except ftplib.all_errors as err:
        printColour('FTP connection error: ' + str(err), bcolors.FAIL)
    return result


def testWeb(host, port=80, doc='/', isHTTPS=False, timeout=DEFAULT_TIMEOUT):
    """Test connection to a web server.

    Args:
        host (str): Web server's hostname.
        port (int): Web server's port.
        doc (str): Web document to check.
        isHTTPS (boolean): True for https connections, False for http.
        timeout (int): Timeout for network connection (seconds)
    Returns:
        (boolean) True on success, False on error
    """
    result = False
    try:
        print('Testing HTTP' + ('S' if isHTTPS else '') + ' server: ' + host + ':' + str(port) + '...')
        print('|-> ', end='')
        if isHTTPS:
            conn = http.client.HTTPSConnection(host=host, port=port, timeout=timeout)
        else:
            conn = http.client.HTTPConnection(host=host, port=port, timeout=timeout)
        conn.request("HEAD", doc)
        response = conn.getresponse()
        print('\'' + doc + '\' response: ' + str(response.status), end=' ')
        if (response.status == 200):
            printColour('Test OK', bcolors.OKGREEN)
            result = True
        else:
            printColour('Test FAIL', bcolors.FAIL)
    except Exception as err:
        printColour('Web connection error: ' + str(err), bcolors.FAIL)
    return result
        

def testService(description, host, port, timeout=DEFAULT_TIMEOUT):
    """Test connection to a server.

    Args:
        description (str): Description of service under test.
        host (str): Hostname.
        port (int): Port number.
        timeout (int): Timeout for network connection (seconds)
    Returns:
        (boolean) True on success, False on error
    """
    result = False
    try:
        print('Testing ' + description + ' (' + host + ', port ' + str(port) + ')...')
        print('|-> ', end='')
        s = socket.socket()
        s.settimeout(timeout)
        s.connect((host, port))
        s.close()
        printColour('Test OK', bcolors.OKGREEN)
        result = True
    except OSError as err:
        printColour('Service test failed: ' + str(err), bcolors.FAIL)
    return result


def generateHTML(description, result):
    """Generates an HTML table row for the result of a test.

    Args:
        description (str): Description of the test.
        result (boolean): True for success, False for fail.
    Returns:
        (str) HTML table row tag with result data.
    """
    html  = '      <tr>\n'
    html += '        <td>' + description + '</td>\n'
    if result:
        html += '        <td class="ok">OK</td>\n'
    else:
        html += '        <td class="fail">FAIL</td>\n'
    html += '      </tr>\n'
    return html


def generateHTMLReport(config, reportData):
    """Generates HTML report on servers status.

    Args:
        config (ConfigParser): Configuration data
        reportData (dict): Report data. Key (str): name, Value (boolean): result
    Returns:
        (str): HTML report.
    """
    time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    report = ''
    report += '<!DOCTYPE html>\n'
    report += '<html>\n'
    report += '  <head>\n'
    report += '    <meta charset="utf-8">\n'
    report += '    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
    report += '    <link href="https://fonts.googleapis.com/css?family=Roboto" rel="stylesheet">\n'
    report += '    <style>\n'
    report += '       body {\n'
    report += '         font-family: "Roboto", sans-serif;\n'
    report += '         max-width: 600px;\n'
    report += '         margin: auto;\n'
    report += '       }\n'
    report += '       h1,p {\n'
    report += '         text-align: center;\n'
    report += '       }\n'
    report += '       h1 {\n'
    report += '         color: #404060;\n'
    report += '       }\n'
    report += '       table {\n'
    report += '         max-width: 590px;\n'
    report += '         margin: auto;\n'
    report += '         border-collapse: collapse;\n'
    report += '       }\n'
    report += '       th,td {\n'
    report += '         padding: 16px;\n'
    report += '         color: #404040\n'
    report += '       }\n'
    report += '       tr {\n'
    report += '         border: 1px solid #f0f0f0;\n'
    report += '       }\n'
    report += '       tr:nth-child(odd) {\n'
    report += '         background-color: #f8f8f8;\n'
    report += '       }\n'
    report += '       .ok {color: green; text-align: center;}\n'
    report += '       .fail {color: red; text-align: center;}\n'
    report += '       .footer {margin-top: 20px;}\n'
    report += '       .button {\n'
    report += '         padding: 12px 60px;\n'
    report += '         text-decoration: none;\n'
    report += '         color: white;\n'
    report += '         background: linear-gradient(180deg, rgb(90,190,87) 0, rgb(53,146,56) 100%), rgb(90, 190, 87);\n'
    report += '         border: 1px solid #0f9b0f;\n'
    report += '         border-radius: 3px;\n'
    report += '       }\n'
    report += '    </style>\n'
    report += '    <title>Server Status Report</title>\n'
    report += '  </head>\n'
    report += '  <body>\n'
    report += '    <h1>Server Status Report</h1>\n'
    report += '    <p>'+ time + '</p>\n'
    report += '    <table>\n'
    report += '      <tr>\n'
    report += '        <th>Service</th>\n'
    report += '        <th>Status</th>\n'
    report += '      </tr>\n'
    for name, result in reportData.items():
        report += generateHTML(name, result)
    report += '    </table>\n'
    if 'livestatus' in config['servermonitor']:
        report += '    <p class="footer"><a class="button" href="' + config['servermonitor']['livestatus'] + '">Live Status</a></p>\n'
    report += '  </body>\n'
    report += '</html>\n'
    return report


def monitorServices(config):
    """Perform all server tests
    Args:
        config (ConfigParser): servermonitor configuration parser.
    Returns:
        (dict): Report of tests (key (str): test name, value (boolean): test result)
    """
    report = OrderedDict()
    # Perform tests
    for name in config.sections():
        if config[name] == 'servermonitor':
            continue

        typ = config[name].get('type','service')
        hostname = config[name].get('host','')
        port = config[name].getint('port', 0)
        timeout = config[name].getint('timeout', DEFAULT_TIMEOUT)
        secure = 's' in typ

        if hostname == '':
            continue

        if typ == 'ftp' or typ == 'ftps':
            if port == 0:
                port = 21
            user = config[name].get('User', 'anonymous')
            pswd = config[name].get('Password', 'nobody@nowhere.com')
            testdir = config[name].get('TestDir', '/')
            report[name] = testFTP(hostname, port, user, pswd, testdir, timeout, secure)

        elif typ == 'http' or typ == 'https':
            if port == 0:
                port = 443 if secure else 80
            document = config[name].get('Document', '/')
            report[name] = testWeb(hostname, port, document, secure, timeout)

        elif typ == 'service' and port != 0:
            report[name] = testService(name, hostname, port, timeout)

    return report


def evaluateFailureCount(config, reportData):
    """Evaluates failure count for each test and updates statistics. Gets global test success result.

    Args:
        config (ConfigParser): servermonitor configuration parser.
        reportData (dict): Report of tests (key (str): test name, value (boolean): test result)
    Returns:
        (boolean): global tests success result
    """
    globalResult = True
    for name, result in reportData.items():
        allowedFailures = config[name].getint('AllowedFailures', DEFAULT_ALLOWED_FAILURES)
        consecutiveFailures = config[name].getint('ConsecutiveFailures', 0)
        if result:
            consecutiveFailures = 0
        else:
            consecutiveFailures = consecutiveFailures + 1
            if consecutiveFailures > allowedFailures:
                globalResult = False
        config[name]['ConsecutiveFailures'] = str(consecutiveFailures)
            
    return globalResult
    

def sendmail(config, reportHTML):
    """Sends alert e-mail.
    Args:
        config (ConfigParser): servermonitor configuration parser.
        reportHTML (str): HTML alert message
    Returns:
        None
    """
    smtpServer = config['servermonitor'].get("SMTPServer", "")
    smtpUser = config['servermonitor'].get("SMTPUser", "")
    smtpPassword = config['servermonitor'].get("SMTPPassword", "")
    smtpFrom = config['servermonitor'].get("SMTPFrom", "")
    smtpTo = config['servermonitor'].get("SMTPTo", "")

    time = datetime.now().strftime('%d/%m/%Y %H:%M')
    subject = "Server Monitor Alert - " + time
    to = ", ".join(smtpTo.split(','))
    print('To: ' + to)

    message = MIMEMultipart()
    message['From'] = smtpFrom
    message['To'] = to
    message['Subject'] = subject
    message.attach(MIMEText(reportHTML, 'html'))

    try:
        server = smtplib.SMTP_SSL(smtpServer)
        server.login(smtpUser, smtpPassword)
        server.send_message(message)
        server.quit()
        print("Alert mail sent")
    except smtplib.SMTPHeloError as e:
        print("Helo Error")
    except smtplib.SMTPAuthenticationError as e:
        print("Authentication Error")
    except smtplib.SMTPRecipientsRefused as e:
        print("Recipients Refused")
    except smtplib.SMTPSenderRefused as e:
        print("Sender Refused")
    except smtplib.SMTPDataError as e:
        print("Data Error")
    except smtplib.SMTPException as e:
        print("SMTP Exception")


# -------------main-------------------------------------------
if __name__ == "__main__":
    # Get config file path from command line args
    parser = ArgumentParser(description='Server status monitor.')
    parser.add_argument('config_file', help='Configuration file path.')
    args = parser.parse_args()
    configFile = args.config_file

    # Load configuration
    if not os.path.isfile(configFile):
        print('Missing config file: ' + configFile)
        exit(-1)
    config = ConfigParser()
    config.read(configFile)
    if not 'servermonitor' in config.sections():
        print('Missing [servermonitor] section in config file: ' + configFile)
        exit(-1)

    # Monitor and write report
    report = monitorServices(config)
    reportHTML = generateHTMLReport(config, report)
    if 'outputpath' in config['servermonitor']:
        outputpath = config['servermonitor']['outputpath']
        with open(outputpath, 'w') as f:
            f.write(reportHTML)

    # Send alerts on failure
    previousSuccess = True
    if 'success' in config['servermonitor']:
        previousSuccess = config['servermonitor'].getboolean('success')
    success = evaluateFailureCount(config, report)
    if not success and previousSuccess:
        print()
        print("Errors detected. Sending alert email...")
        sendmail(config, reportHTML)

    # Save monitor result in config file
    config['servermonitor']['success'] = '1' if success else '0'
    with open(configFile, 'w') as f:
        config.write(f)
