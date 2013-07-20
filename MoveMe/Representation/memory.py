#!/usr/bin/env python

'''
Implemented at V2_ Lab, for documentation see

	* http://trac.v2.nl/wiki/MoveMeDocumentation
'''

from pysqlite2 import dbapi2 as sqlite
import cPickle
import re, getopt, sys


class MemoryDBInterface(object):
	''' Interface to the pysqlite2 database. '''

	def __init__(self, db_file):
		''' The initialization function:

			* initializes connection to either persistent or non-persistant database (see comments).
			* sets cursor.
		'''

		self.connection = sqlite.connect('memory.db')	# persistant db
		#self.connection = sqlite.connect(":memory:")	# or non-persistant db
		#self.newTables() 				# uncomment this line in case of non-persistant db

		self.cursor = self.connection.cursor()


	def quit(self):
		''' Commits changes to the database, closes cursor and connection. '''

		self.connection.commit()
		self.cursor.close()
		self.connection.close()


	def newTables(self):
		'''
		Creates the three tables to store the Context objects:

			* pillows
			* persons
			* sessions
		'''

		self.cursor.execute("create table pillows(name, id, address, host, port, config)")
		self.cursor.execute("create table persons(fullname, firstname, lastname)")
		self.cursor.execute("create table sessions(ts, personname, personrfid, pillowname, pillowid, buffer)")


	def insertPillow(self, pillow):
		'''
		Adds the information contained by the Pillow object to the database.
		Returns True / False on success / failure.
		'''

		result = self.getRow('pillows', 'name', pillow.name)

		if result == []:

			sql = 'insert into pillows(name, id, address, host, port, config) values(?, ?, ?, ?, ?, ?)'
			values = [
				pillow.name,
				pillow.id,
				pillow.address,
				pillow.host,
				pillow.port,
				sqlite.Binary(cPickle.dumps(pillow.config, 2))]

			self.cursor.execute(sql, values)
			self.connection.commit()
			print " * added %s to the database" % pillow.name
			return True
		else:
			return False


	def insertPerson(self, person):
		'''
		Adds the information contained by the Person object to the database.
		Returns True / False on success / failure.
		'''

		results = self.getRow('persons', 'fullname', person.name)

		if results == []:

			values = [person.name, person.firstname, person.lastname]
			sql = "insert into persons(fullname, firstname, lastname) values(?, ?, ?)"

			self.cursor.execute(sql, values)
			self.connection.commit()
			print " * added %s to the database" % person.name
			return True

		else:
			return False


	def insertSession(self, session):
		'''
		Adds the information contained by a Session object to the database.
		The buffer is stored binary using cPickle.
		'''

		values = [
			session.timestamp,
			session.person.name,
			session.person.rfid,
			session.pillow.name,
			session.pillow.id,
			sqlite.Binary(cPickle.dumps(session.buffer, 2))]

		sql = 'insert into sessions(ts, personname, personrfid, pillowname, pillowid, buffer) values(?, ?, ?, ?, ?, ?)'
		self.cursor.execute(sql, values)
		self.connection.commit()

		print " * added session %s to the database" % session.timestamp


	def getAllTables(self, verbose=False):
		''' Nice verbose tables-dump for application startup. '''

		sql = 'select * from %s' % 'pillows'

		try:
			pillows = self.fetchAll(sql)
		except sqlite.OperationalError:
			print '!!!Pillows table doesn\'t exist yet, creating a new one.'
			self.cursor.execute("create table pillows(name, id, address, host, port, config)")
			pillows = []

		sql = 'select * from %s' % 'persons'

		try:
			persons = self.fetchAll(sql)
		except sqlite.OperationalError:
			print '!!!Persons table doesn\'t exist yet, creating a new one.'
			self.cursor.execute("create table persons(fullname, firstname, lastname)")
			persons = []

		sql = 'select * from %s' % 'sessions'

		try:
			sessions = self.fetchAll(sql)
		except sqlite.OperationalError:
			print '!!!Sessions table doesn\'t exist yet, creating a new one.'
			self.cursor.execute("create table sessions(ts, personname, personrfid, pillowname, pillowid, buffer)")
			sessions = []

		if verbose == True:
			print ' * Loading database values'

			if len(pillows) == 0:
				print '   - no known pillows yet'
			else:
				print '   - known pillows:'
				for p in pillows: print '     *', p[0]

			if len(persons) == 0:
				print '   - no known persons yet'
			else:
				print '   - known persons:'
				for p in persons: print '     *',  p[0]

		return pillows, persons, sessions


	def getTable(self, name):
		''' Returns all the contents of a table. '''

		sql = 'select * from %s' % name
		results = self.fetchAll(sql)

		return results


	def getPillowConfig(self, name):
		blob = self.getRow('pillows', 'name', name)[0][-1]
		return cPickle.loads(str(blob))


	def savePillowConfiguration(self, pillow):

		new_config = sqlite.Binary(cPickle.dumps(pillow.config, 2))

		sql = 'update pillows set config=? where name=?'
		self.cursor.execute(sql, (new_config, pillow.name))
		self.connection.commit()

		#checkconfig = self.getPillowConfig(pillow.name)
		#print checkconfig.dict


	def fetchAll(self, sql):
		'''
		Selects all rows in the db that match the query, returns them
		as a list of strings containing all the row info.
		'''

		rows = []

		try:
			self.cursor.execute(sql)
		except Exception:
			print '!!!Passing sqlite execute() exception to caller.'
			raise

		for row in self.cursor.fetchall():
			rows.append(row)

		return rows


	def getRow(self, table, field, value):
		''' Queries a table for a single value, returns a row as a list. '''

		sql = 'select * from %s where %s=?' % (table, field)

		self.cursor.execute(sql, (value,))
		return self.cursor.fetchall()


	def setValue(self, table, field, value, key):
		''' Changes a single value in a table using table, field and key for lookup. '''

		sql = 'update %s set %s=? where name=?' % (table, field)
		self.cursor.execute(sql, (value, key))
		self.connection.commit()


	def deleteRow(self, table, key, value):
		''' Queries a table for a key value, deletes the row if present row. '''

		sql = 'delete from %s where %s=?' % (table, key)
		self.cursor.execute(sql, (value,))
		return self.cursor.fetchall()


	def deleteTable(self, name):
		''' Deletes a single table. '''

		sql = "delete from %s where 1=1" % name
		self.cursor.execute(sql)
		self.connection.commit()


	def wipe(self):
		''' Clears entire database. '''

		sql = 'drop table pillows'
		self.cursor.execute(sql)
		sql = 'drop table persons'
		self.cursor.execute(sql)
		sql = 'drop table sessions'
		self.cursor.execute(sql)
		self.connection.commit()

		self.newTables()


def usage():
	''' Explanation of command line arguments usage. '''

	print "./memory.py -w : wipes the database "
	sys.exit()


if __name__ == '__main__':
	'''
	Called from the commandline to clear (wipe()) the database.
	Run as
		./memory.py -w
	'''

	memory_db_interface = MemoryDBInterface('../memory.db')

	try:
		opts, args = getopt.getopt(sys.argv[1:], "w:n")
	except getopt.GetoptError:
		usage()


	for opt, arg in opts:
		if opt == '-w':
			memory_db_interface.wipe()
		if opt == '-n':
			memory_db_interface.newTables()
