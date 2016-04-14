#!/usr/bin/env python2.7

import getopt
import logging
import os
import socket
import sys

# Constants

ADDRESS  = '127.0.0.1'
PORT     = 9234
PROGRAM  = os.path.basename(sys.argv[0])
LOGLEVEL = logging.INFO

# Utility Functions

def usage(exit_code=0):
    print >>sys.stderr, '''Usage: {program} [-v] ADDRESS PORT

Options:

    -h       Show this help message
    -v       Set logging to DEBUG level
'''.format(port=PORT, program=PROGRAM)
    sys.exit(exit_code)

# TCPClient Class

class TCPClient(object):

    def __init__(self, address=ADDRESS, port=PORT):
        ''' Construct TCPClient object with the specified address and port '''
        self.logger  = logging.getLogger()                              # Grab logging instance
        self.socket  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)# Allocate TCP socket
        self.address = address                                          # Store address to listen on
        self.port    = port                                             # Store port to lisen on

    def handle(self):
        ''' Handle connection '''
        self.logger.debug('Handle')
        raise NotImplementedError

    def run(self):
        ''' Run client by connecting to specified address and port and then
        executing the handle method '''
        try:
            # Connect to server with specified address and port, create file object
            self.socket.connect((self.address, self.port))
            self.stream = self.socket.makefile('w+')
        except socket.error as e:
            self.logger.error('Could not connect to {}:{}: {}'.format(self.address, self.port, e))
            sys.exit(1)

        self.logger.debug('Connected to {}:{}...'.format(self.address, self.port))

        # Run handle method and then the finish method
        try:
            self.handle()
        except Exception as e:
            self.logger.exception('Exception: {}', e)
        finally:
            self.finish()

    def finish(self):
        ''' Finish connection '''
        self.logger.debug('Finish')
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
        except socket.error:
            pass    # Ignore socket errors
        finally:
            self.socket.close()

# EchoClient Class

class EchoClient(TCPClient):
    def handle(self):
        ''' Handle connection by reading data and then writing it back until EOF '''
        self.logger.debug('Handle')

        try:
            data = sys.stdin.readline()
            while data:
                # Send STDIN to Server
                self.stream.write(data)
                self.stream.flush()

                # Read from Server to STDOUT
                data = self.stream.readline()
                sys.stdout.write(data)

                # Read from STDIN
                data = sys.stdin.readline()
        except socket.error:
            pass    # Ignore socket errors

# Main Execution

if __name__ == '__main__':
    # Parse command-line arguments
    try:
        options, arguments = getopt.getopt(sys.argv[1:], "hv")
    except getopt.GetoptError as e:
        usage(1)

    for option, value in options:
        if option == '-v':
            LOGLEVEL = logging.DEBUG
        else:
            usage(1)

    if len(arguments) >= 1:
        ADDRESS = arguments[0]
    if len(arguments) >= 2:
        PORT    = int(arguments[1])

    # Set logging level
    logging.basicConfig(
        level   = LOGLEVEL,
        format  = '[%(asctime)s] %(message)s',
        datefmt = '%Y-%m-%d %H:%M:%S',
    )

    # Lookup host address
    try:
        ADDRESS = socket.gethostbyname(ADDRESS)
    except socket.gaierror as e:
        logging.error('Unable to lookup {}: {}'.format(ADDRESS, e))
        sys.exit(1)

    # Instantiate and run client
    client = EchoClient(ADDRESS, PORT)

    try:
        client.run()
    except KeyboardInterrupt:
        sys.exit(0)

# vim: set sts=4 sw=4 ts=8 expandtab ft=python:
