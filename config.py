#    Copyright 2013 X35
#
#    This file is part of gamemod.
#
#    gamemod is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    gamemod is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with gamemod.  If not, see <http://www.gnu.org/licenses/>.

LISTEN_ADDR = "0.0.0.0"
LISTEN_PORT = 28787

MASTER_ADDR = "sauerbraten.org" # the masterserver to fetch servers from
MASTER_PORT = 28787
MASTER_FETCH_INTERVAL = 15*60 # interval to fetch servers from another masterserver, in seconds

OWN_ADDRESS = "example.com" # my own address (e.g. master.crapmod.net)

LOG_PRINT = True
LOG_FILE = "gamemod.log"

DEBUG_RECORD_MESSAGES = 100 # amount of messages to keep for the case of an exception

# production configuration
_DEBUG_ENABLE_PRODUCTION = {
	"netserver/replytext": False,
	"server/read": False,
	"server/bufdump": False,
	"server/clientcnsdump": False,
	"server/clientdump": False,
	"server/readinfo": False,
	"server/readfail": False,
	"servercommunicator/recv": False,
	"servercommunicator/succreg": False,
	"servercommunicator/ping": False,
	"servercommunicator/sent": False,
	"servercommunicator/kick": False,
	"servercommunicator/kickserver": False,
	"serverlist/invalidport": False,
	"masterclient/fetched": False,
	"guiline/dumpparts": False,
	"netserver": False,
	"netserver/traffic": False,
	"netserver/reply": False,
}

# netdebug configuration
_DEBUG_ENABLE_NETDEBUG = {
	"netserver/replytext": False,
	"server/read": False,
	"server/bufdump": False,
	"server/clientcnsdump": False,
	"server/clientdump": False,
	"server/readinfo": False,
	"server/readfail": False,
	"servercommunicator/recv": False,
	"servercommunicator/succreg": False,
	"servercommunicator/ping": False,
	"servercommunicator/sent": False,
	"servercommunicator/kick": False,
	"servercommunicator/kickserver": False,
	"serverlist/invalidport": False,
	"masterclient/fetched": False,
	"guiline/dumpparts": False,
	"netserver": True,
	"netserver/traffic": True,
	"netserver/reply": True,
}

# debug configuration
_DEBUG_ENABLE_DEBUG = {
	"netserver/replytext": True,
	"server/read": True,
	"server/bufdump": False,
	"server/clientcnsdump": False,
	"server/clientdump": False,
	"server/readinfo": True,
	"server/readfail": True,
	"servercommunicator/recv": True,
	"servercommunicator/succreg": True,
	"servercommunicator/ping": True,
	"servercommunicator/sent": True,
	"servercommunicator/kick": True,
	"servercommunicator/kickserver": True,
	"serverlist/invalidport": True,
	"masterclient/fetched": True,
	"guiline/dumpparts": False,
	"netserver": True,
	"netserver/traffic": True,
	"netserver/reply": True,
}

DEBUG_ENABLE = _DEBUG_ENABLE_DEBUG
#DEBUG_ENABLE = _DEBUG_ENABLE_NETDEBUG
#DEBUG_ENABLE = _DEBUG_ENABLE_PRODUCTION

# system
PING_INTERVAL = 8 # time between pinging servers (in seconds)
PING_SPREADRATIO = 1 # maximum value PING_INTERVAL will be multiplied with and added to the default PING_INTERVAL (this will be applied to the last server in the list (who's got the least players connected))
PINGS_GIVEUP = 5 # amount of pings before giving up

MAX_CONNECTIONS_PER_IP = 5 # maximum number of connections an IP-address can make at the same time

CACHED_CMDS = ["list", "readablelist", "stats"]
CACHE_TIME = 2 # max age (in seconds) for cached replies until they get invalid and are rebuilt

