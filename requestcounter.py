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

class requestcounter:
	KEEP_TIME = 24*60*60

	def __init__(self):
		self.n_differentips = 0
		self.req = []
		self.lock = Lock()
	
	def differentips(self):
		with self.lock:
			return self.n_differentips
	
	def requests(self):
		with self.lock:
			return len(self.req)
		
	def add(self, ip):
		with self.lock:
			t = time.time()
			min_t = t - requestcounter.KEEP_TIME
			dellist = []
			known_ips = []
			for req in self.req:
				(r_time, r_ip) = req
				if r_time < min_t:
					dellist.append(req)
				elif not known_ips.count(r_ip):
					known_ips.append(r_ip)
			for req in dellist:
				self.req.remove(req)
			self.n_differentips = len(known_ips) + (1 if not known_ips.count(ip) else 0)
			self.req.append((t, ip))

