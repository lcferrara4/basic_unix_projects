#!/usr/bin/env python2.7

import sys
import string
import random
import hashlib
import itertools
import getopt

#constatss

ALPHABET = string.ascii_lowercase + string.digits
LENGTH = 8#!/usr/bin/env python2.7

import sys
import string
import random
import hashlib
import itertools
import getopt

#constatss

ALPHABET = string.ascii_lowercase + string.digits
LENGTH = 8
HASHES = 'hashes.txt'
PREFIX = ''
PREF=False

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

#Parse Command Line

try:
    options, arguments = getopt.getopt(sys.argv[1:], "a:l:s:p:")
except getopt.GetoptError:
    usage(1)

for option, value in options:
    if option == '-a':
        ALPHABET=str(value)
    elif option == '-l':
        LENGTH = int(value)
    elif option == '-p':
        PREFIX=str(value)
        PREF=True
    elif option == '-s':
        HASHES=str(value)
    else:
        usage(1)
#Main Exacution


HASHES = 'hashes.txt'
PREFIX = ''
PREF=False

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

#Parse Command Line

try:
    options, arguments = getopt.getopt(sys.argv[1:], "a:l:s:p:")
except getopt.GetoptError:
    usage(1)

for option, value in options:
    if option == '-a':
        ALPHABET=str(value)
    elif option == '-l':
        LENGTH = int(value)
    elif option == '-p':
        PREFIX=str(value)
        PREF=True
    elif option == '-s':
        HASHES=str(value)
    else:
        usage(1)
#Main Exacution

if __name__ == '__main__':
    hashes = set([l.strip() for l in open(HASHES)])
    found = set()

    for candidate in itertools.product(ALPHABET, repeat=LENGTH):
        candidate = ''.join(candidate)
        if PREF:
            candidate=PREFIX+candidate
        checksum = md5sum(candidate)
        if checksum in hashes:
            found.add(candidate)

    for word in sorted(found):
        print word
