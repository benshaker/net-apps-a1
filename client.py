#!/usr/bin/env python3

import socket
import argparse
import sys

def main(args):

	server_ip = args.sip
	server_port = args.sp
	socket_size = args.z
	s = None

	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((server_ip, server_port))
	except socket.error as message:
		if s:
			s.close()
		print ("Unable to open the socket: " + str(message))
		sys.exit(1)

	s.send(b'Hello, world!')
	data = s.recv(socket_size)
	s.close()

	print ('Received:', data)
	print (args.sip)
	print (args.sp)
	print (args.z)

if __name__ == "__main__":

	parser = argparse.ArgumentParser()
	parser.add_argument('-sip', help="Server IP Address", type=str)
	parser.add_argument('-sp', help="Server Port", type=int, default=0)
	parser.add_argument('-z', help="Socket Size", type=int, default=0)

	if len(sys.argv) != 7 and sys.argv[1] != "-h" and sys.argv[1] != "--help":
		print("Error: Too few arguemnts")
	else: 
		main(parser.parse_args(sys.argv[1:]))
