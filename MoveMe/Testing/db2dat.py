#!/usr/bin/env python

'''
Implemented at V2_ Lab, for documentation see

 http://trac.v2.nl/wiki/MoveMeDocumentation

Converts stored buffer from SQLite database to a format that is readable by the
simulator.py program.

Was designed for an older table layout, should be adjusted for new .db files.
'''

import sys, os, getopt
from pysqlite2 import dbapi2 as sqlite
import cPickle
import memory

data_file = None
data_fd = None


def usage():

	print "./db2dat.py [-d FILE --data=FILE] [-h --help]"
	sys.exit()

def main():
	''''''

	global data_file, f

	try:
		opts, args = getopt.getopt(sys.argv[1:],
			"d:h",
			["data=", "help"])

	except getopt.GetoptError: usage()

	for opt, arg in opts:
		if opt in ("-d", "--data"):
			data_file = arg
			if not os.path.isfile(data_file):
				print "'%s' is not a valid data file" % (data_file)
				sys.exit(1)


		elif opt in ("-h", "--help"): usage()
	
	if not data_file: usage()
	else:
		mem = memory.MemoryDBInterface(data_file)

		mem.cursor.execute('select * from sessions')
		results = mem.cursor.fetchall()
		f = open('output.dat', 'w')

		for r in results:
			raw_data = r[2]
			raw_data = str(raw_data)
			buffer = cPickle.loads(raw_data)
			for a in buffer:
				for b in a[1]:
					f.write(str(b))
					f.write('\t')
				f.write('\n')


if  __name__ == '__main__':
	main()
