#!/usr/bin/env python3

import socket
import argparse
import sys
import numpy as np
import cv2
import picamera
import time
from pyzbar.pyzbar import decode
from PIL import Image

def main(args):

	server_ip = args.sip
	server_port = args.sp
	socket_size = args.z
	s = None

	image = cv2.imread('Hello_World_QR.png')

	decodedObject = decode(image)
	print (decodedObject)

	'''
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((server_ip, server_port))
	except socket.error as message:
		if s:
			s.close()
		print ("Unable to open the socket: " + str(message))
		sys.exit(1)
	
	cam = picamera.PiCamera()
	cam.start_preview()
	cam.capture('test.jpg')
	cam.stop_preview()
	
	# Messages should be sent in bytes b' '
	s.send(b'Hello, world!')
	data = s.recv(socket_size)
	s.close()
	'''

if __name__ == "__main__":

	parser = argparse.ArgumentParser()
	parser.add_argument('-sip', help="Server IP Address", type=str)
	parser.add_argument('-sp', help="Server Port", type=int, default=0)
	parser.add_argument('-z', help="Socket Size", type=int, default=0)

	if len(sys.argv) != 7 and sys.argv[1] != "-h" and sys.argv[1] != "--help":
		print("Error: Too few arguemnts")
	else: 
		main(parser.parse_args(sys.argv[1:]))
