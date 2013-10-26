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

class accesscache:

	def __init__(self, n):
		self.lock = Lock()
		self.list = {}
		self.n = n
	
	def get(self, host):
		with self.lock:
			return (self.list[host] if self.list.has_key(host) else 0)

	def set(self, host, n):
		with self.lock:
			self.list[host] = n
		
	def unset(self, host):
		with self.lock:
			del self.list[host]
	
	# ---
	
	def increase(self, host):
		self.set(host, self.get(host) + 1)
		
	def decrease(self, host):
		n = max(self.get(host) - 1, 0)
		if n > 0: self.set(host, n)
		else: self.unset(host)
	
	def permit(self, host):
		if self.get(host) < self.n:
			self.increase(host)
			return True
		return False
	
	def end(self, host):
		self.decrease(host)
