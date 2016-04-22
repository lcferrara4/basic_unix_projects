#!/usr/bin/env python2.7

import sys
import string
import random
import hashlib
import itertools
import getopt

#constatss

ALPHABET = string.ascii_lowercase + string.digits
LENGTH = int(sys.argv[1])
#ATTEMPTS = int(sys.argv[2]) cause doing it systematically
HASHES = sys.argv[3]
PREFIX = ''


#Utility functions

def usage(exit_code=0):
	print >>sys.stderr, '''Usage: hulk.py [-a ALPHABET -l LENGTH -s HASHES -p PREFIX]

Options:

      -a  ALPHABET    Alphabet used for passwords
      -l  LENGTH      Length for passwords
      -s  HASHES      Path to file containing hashes
      -p  PREFIX      Prefix to use for each candidate password
'''
	sys.exit(exit_code)

def md5sum(s):
	return hashlib.md5(s).hexdigest()



#Main Exacution

if __name__ == '__main__':
	# Parsing the command line
	count = 1
	try:
		options, arguments = getopt.getopt(sys.argv[1:], "a:l:s:p:")
	except getopt.GetoptError as e:
		usage(1)

	for option, value in options:
		if option == '-a':
			ALPHABET = str(value)
			count+=2
		elif option == '-l':
			LENGTH = int(value)
			count+=2
		elif option == '-p':
			PREFIX = str(value)
			count+=2
		elif option == '-s':
			HASHES = str(value)
			cout+=1


	hashes = set([l.strip() for l in open(HASHES)])
	found = set()

	for canidate in itertools.product(ALPHABET, repeat=LENGTH):
		canidate = ''.join(canidate)
		#canidate = ''.join([random.choice(ALPHABET) for _ in range(LENGHT)])

		print canidate # all the canidates that the hash could be

		checksum = md5sum(canidate)
		if checksum in hashes:
			#found.add(candidate) 
			found.add(canidate)
			print "Check sum" ,checksum

	for word in sorted(found):
		print "Word" ,word