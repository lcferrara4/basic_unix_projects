#!/usr/bin/env python2.7

import getopt
import logging
import os
import socket
import time
import sys

# Constants

PROCESSES =1
REQUESTS=1
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

    def __init__(self, address, port):
        ''' Construct TCPClient object with the specified address and port '''
        self.logger  = logging.getLogger()                              # Grab logging instance
        self.socket  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)# Allocate TCP socket
        self.address = socket.gethostbyname(address)                                          # Store address to listen on
        self.port    = port                                             # Store port to lisen on
        self.logger.debug("URL:\t{}".format(self.url))
        self.logger.debug("HOST:\t{}".format(self.host))
        self.logger.debug("PORT:\t{}".format(self.port))
        self.logger.debug("PATH:\t{}".format(self.path))


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
        self.stream.flush()
        self.logger.debug('Finish')
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
        except socket.error:
            pass    # Ignore socket errors
        finally:
            self.socket.close()

# HTTP Class

class HTTPClient(TCPClient):
    def __init__(self, url):
        #parse
        self.url = url.split('://')[-1]

        if '/' not in self.url:
            self.path = '/'
        else:
            self.path = '/' + self.url.split('/',1)[-1]

        if ':' not in self.url:
            self.port = int(80)
            if '/' not in self.url:
                self.host = self.url
            else:
                self.host = self.url.split('/',1)[0]
        else:
            self.port = self.url.split(':',1)[-1]
            self.host = self.url.split(':',1)[0]
            self.port = int(self.port.split('/',1)[0])
        self.address = socket.gethostbyname(self.host)
        TCPClient.__init__(self, self.address, self.port) #Initalize base class


    def handle(self):
        ''' Handle connection by reading data and then writing it back until EOF '''
        self.logger.debug('Handle')

        #SEND REQUEST
        self.logger.debug('Sending request...')
        self.stream.write('GET {} HTTP/1.0\r\n'.format(self.path))
        self.stream.write('Host: {}\r\n'.format(self.host))
        self.stream.write('\r\n')

        #PRINTS TO STDOUT
        self.stream.flush()
        self.logger.debug('Receiving response...')
        data = self.stream.readline()
        while data:
            sys.stdout.write(data)
            data = self.stream.readline()

# Main Execution
count =1
if __name__ == '__main__': #guard code
    # Parse command-line arguments
    try:
        options, arguments = getopt.getopt(sys.argv[1:], "hvr:p:")
    except getopt.GetoptError as e:
        usage(1)

    for option, value in options:
        if option == '-v':
            LOGLEVEL = logging.DEBUG
            count+=1
        elif option == '-r':
            REQUESTS = value
            count+=2
        elif option == '-p':
            PROCESSES = value
            count+=2
        elif option == '-h':
            usage(1)

    try:
        URL = sys.argv[int(count)]
    except IndexError:
        usage(1)
    '''
    if len(arguments) >= 1:
        ADDRESS = arguments[0]
    if len(arguments) >= 2:
        PORT    = int(arguments[1])
    '''
    # Set logging level
    logging.basicConfig(
        level   = LOGLEVEL,
        format  = '[%(asctime)s] %(message)s',
        datefmt = '%Y-%m-%d %H:%M:%S',
    )

    ''' # Lookup host address
    try:
        ADDRESS = socket.gethostbyname(ADDRESS)
    except socket.gaierror as e:
        logging.error('Unable to lookup {}: {}'.format(ADDRESS, e))
        sys.exit(1) '''

    # Instantiate and run client

    for process in range(int(PROCESSES)):
        START = time.time()
        try:
            pid = os.fork()
        except OSError as e:
            print "fork failed: {}".format(e)
        if pid == 0:
            for request in range(int(REQUESTS)):
                client=HTTPClient(URL)
                try:
                    client.run()
                except KeyboardInterrupt:
                    sys.exit(0)
            END = time.time()
            pid = os.getpid()
            average = (END-START) / float(PROCESSES)
            elapsed = END - START
            logging.debug("{0} | Elapsed time: {1:.2f} seconds".format(pid, elapsed))
            logging.debug("{0} | Average elapsed time: {1:.2f} seconds".format(pid, average))
            os._exit(0)


    for process in range(int(PROCESSES)):
        try:
            pid, status = os.wait()
            print "PID: {} return with exit code {}".format(os.getpid(), status)
        except:
            pass

        ''' END = time.time()
        pid = os.getpid()
        average = (END-START) / float(PROCESSES)
        elapsed = END - START
        logging.debug("{0} | Elapsed time: {1:.2f} seconds".format(pid, elapsed))
        logging.debug("{0} | Average elapsed time: {1:.2f} seconds".format(pid, average))
        '''

# vim: set sts=4 sw=4 ts=8 expandtab ft=python:
