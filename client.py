#!/usr/bin/env python3

import socket
import argparse
import sys

def main(args):

	server_ip = ''
	server_port = ''
	socket_size = ''

	# -sip, -sp, -z

	s = None

	print (args.sip)
	print (args.sp)
	print (args.z)

if __name__ == "__main__":

	parser = argparse.ArgumentParser()
	parser.add_argument('-sip', help="Server IP Address", type=str)
	parser.add_argument('-sp', help="Server Port", type=str)
	parser.add_argument('-z', help="Socket Size", type=int, default=0)

	if len(sys.argv) != 7 and sys.argv[1] != "-h" and sys.argv[1] != "--help":
		print("Error: Too few arguemnts")
	else: 
		main(parser.parse_args(sys.argv[1:]))
