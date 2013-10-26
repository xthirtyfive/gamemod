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
#    along with gamemod.  If not, see <http:#www.gnu.org/licenses/>.

import sys
import traceback
from threading import Lock
import time
import config
from log import log
import types

class debug:	
	PRINT_LOCK = Lock()
	RECORD_LOCK = Lock()
	
	RECMSG = []
	RECPOS = 0
	
	@staticmethod
	def tagenabled(tag): # all tags enabled by default, except if set to False explicitly in enable_msg
		return (not tag) or (not config.DEBUG_ENABLE.has_key(tag)) or config.DEBUG_ENABLE[tag]
			
	@staticmethod
	def record(msg):
		with debug.RECORD_LOCK:
			if not config.DEBUG_RECORD_MESSAGES: return
			if len(debug.RECMSG) < config.DEBUG_RECORD_MESSAGES:
				debug.RECMSG.append(msg)
			else:
				if not (debug.RECPOS < len(debug.RECMSG)):
					debug.RECPOS = 0
				debug.RECMSG[debug.RECPOS] = msg
				debug.RECPOS += 1
			
	@staticmethod
	def outrecordedmessages():
		with debug.RECORD_LOCK:
			l = len(debug.RECMSG)
			n = 0
			i = debug.RECPOS
			while n < l:
				if not (i < l): i = 0
				log.out("\t%s" % debug.RECMSG[i])
				i += 1
				n += 1

	@staticmethod
	def exc(instance = None):
		with debug.PRINT_LOCK:
			#print("%s: %s" % (str(instance), str(sys.exc_info())))
			log.out("[%s] EXCEPTION: %d kept messages:" % (time.strftime("%a, %d.%m.%Y (%b), %H:%M:%S"), len(debug.RECMSG)))
			debug.outrecordedmessages()
			log.out(traceback.format_exc())
			
	@staticmethod
	def msg(tag, s):
		with debug.PRINT_LOCK:
			msg = "[%s] %s: %s" % (time.strftime("%a, %d.%m.%Y (%b), %H:%M:%S"), (str(tag) if (type(tag) == types.StringType) else "MAIN"), str(s))
			debug.record(msg)
			if (tag == True) or debug.tagenabled(tag): log.out(msg)
