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

import config

class log:
	f = None

	@staticmethod
	def out(msg):
		if config.LOG_PRINT: print(msg)
		if not log.f: log.openfile()
		if log.f:
			log.f.write(msg+"\n")
			log.f.flush()
		
	@staticmethod
	def openfile():
		if not config.LOG_FILE: return
		log.f = open(config.LOG_FILE, "a")
	
	@staticmethod
	def closefile():
		if not log.f: return
		log.f.close()
