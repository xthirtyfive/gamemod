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

class lockedlist:
	def __init__(self):
		self.lock = Lock()
		self.list = []
	
	def exchange(self, newlist):
		with self.lock:
			self.list = newlist
	
	def iterator(self):
		with self.lock:
			for item in self.list:
				yield item
	
	def releasingiterator(self):
		self.lock.acquire()
		for item in self.list:
			self.lock.release()
			yield item
			self.lock.acquire()
		self.lock.release()
	
	def sort(self, func):
		with self.lock:
			self.list.sort(key=func)
	
	def len(self):
		with self.lock:
			return len(self.list)
	
	def append(self, item):
		with self.lock:
			self.list.append(item)
		
	def clear(self):
		with self.lock:
			del self.list[:]
			
	def remove(self, item):
		with self.lock:
			self.list.remove(item)
	
	def removeall(self, item):
		with self.lock:
			for i in range(self.list.count(item)): # NOT self.count! (would acquire lock again and therefore deadlock)
				self.list.remove(item) # NOT self.remove! (would acquire lock again and therefore deadlock)
	
	def count(self, item):
		with self.lock:
			return self.list.count(item)
			
