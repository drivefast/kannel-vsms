import sys
import syslog
import os
import json


# quick ref to the directory where the application is installed
APP_DIR = os.path.dirname(os.path.realpath(__file__))

DEBUG_MODE = True

# if running in standalone mode, these are the parameters of the web server 
# where the kannel proxy app listens to (in production mode, they would be
# ineffective, as they are part of the external web server configuration)
LISTEN_HOST = "127.0.0.1"
LISTEN_PORT = "13001"
LISTEN_URL_PATH = "/cgi-bin/sendsms"
# where the actual Kannel is listening to, for http requests that generate 
# SMS messages; see the settings in the "core" group of your kannel gateway
KANNEL_URL = "http://localhost:13131/cgi-bin/sendsms"

# access to the vSMS API requires either an API key, or a file containing 
# credentials for a Google service account (only define one method)
#VSMS_AUTH_APIKEY = "YOUR_API_KEY_HERE"
VSMS_AUTH_SERVICEACCOUNT = json.loads(open(
    APP_DIR + "/credentials.json"
).read())

# each of the vSMS agents you use will have their data as individual files, 
# with JSON content, in this directory; file names are <agent_id>.json
AGENT_DATA = "file://" + APP_DIR + "/agents/"
# alternatively, same data can be obtained from a web service, that provides 
# GET and POST capabilities
#AGENT_DATA = "https://api.example.com/vsms_agents"
# you may need authentication for the agent service
AGENT_DATA_AUTH = ("agent", "zzyzx")
# typically, the kannel proxy app loads (caches) all the agent info into the 
# application memory; however, setting this to `False` will force a query to 
# the agent data storage on every SMS request (only recommended if you have a 
# lot of agents, and you fetch the agent data via http)
CACHE_AGENT_DATA = True

# propagate a request for an SMS, even though a vSMS hash could not be posted
SEND_UNVERIFIED = True



###############    no more user settings below this point   ################

try: x = VSMS_AUTH_APIKEY
except NameError: VSMS_AUTH_APIKEY = None

AGENT_FOR, AGENT = None, None

def load_config():
    # will provide code here if we load the config from a file
    pass


LOG_IDENT = "vsms_kannel"
LOG_FACILITY = syslog.LOG_LOCAL6
LOG_LEVEL = "WARNING"

class Logger:
    def __init__(self, ident=None, facility=None):
        self.ident = ident or ""
        self.facility = facility or syslog.LOG_LOCAL0
        syslog.openlog(
            ident=self.ident,
            facility=self.facility
        )
    def debug(self, message):
        if LOG_LEVEL in [ "DEBUG", "INFO", "WARNING", "ERROR", "ALARM" ]: return
        syslog.syslog(syslog.LOG_DEBUG, "[DEBUG] " + str(message))
    def info(self, message):
        if LOG_LEVEL in [ "INFO", "WARNING", "ERROR", "ALARM" ]: return
        syslog.syslog(syslog.LOG_INFO, "[INFO] " + str(message))
    def warning(self, message):
        if LOG_LEVEL in [ "WARNING", "ERROR", "ALARM" ]: return
        syslog.syslog(syslog.LOG_WARNING, "[WARNING] " + str(message))
    def error(self, message):
        if LOG_LEVEL in [ "ERROR", "ALARM" ]: return
        syslog.syslog(syslog.LOG_ERR, "[ERROR] " + str(message))
    def alarm(self, message):
        if LOG_LEVEL in [ "ALARM" ]: return
        syslog.syslog(syslog.LOG_ALERT, "[ALARM] " + str(message))

log = Logger(LOG_IDENT or "", facility=(LOG_FACILITY or syslog.LOG_LOCAL6))
log.warning("Logger started")

