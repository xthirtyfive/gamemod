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

from threading import Lock
import time

import config

class replycache:

	@staticmethod
	def enabled(line):
		return config.CACHED_CMDS.count(line) > 0
	
	# ---
	
	def __init__(self):
		self.lock = Lock()
		self.list = {}
	
	def set(self, line, r):
		with self.lock:
			self.list[line] = r
	
	def get(self, line):
		with self.lock:
			return (self.list[line] if self.list.has_key(line) else None)
	
	def unset(self, line):
		with self.lock:
			del self.list[line]
		
	# ---

	def cache(self, line, reply, close):
		if replycache.enabled(line):
			self.set(line, (time.time(), (reply, close)))
	
	def find(self, line):
		r = self.get(line)
		if r:
			if (time.time() - r[0]) <= config.CACHE_TIME:
				return r[1]
			else:
				self.unset(line)
		return None
