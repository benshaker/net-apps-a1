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
from watson_developer_cloud import TextToSpeechV1
import os

def main(args):
	# Label the server connection specifications
	server_ip = args.sip
	server_port = args.sp
	socket_size = args.z
	s = None

	# Set up the server connection
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((server_ip, server_port))
	except socket.error as message:
		if s:
			s.close()
		print ("Unable to open the socket: " + str(message))
		# sys.exit(1)

	# If there is no QR Code, then decode will output: []
	# Else there will be data, type, etc
	# Initialize the camera stream
	# cam = cv2.VideoCapture(0)
	question = decode(cv2.imread('Hello_World_QR.png'))

	# print (cam.isOpened())

	# initializing text-to-speech
	text_to_speech = TextToSpeechV1(
		iam_apikey='8tY8kV6y_CR_m3Hp0-CgQdSKldyLKu0vzunGoIg37vEe',
		url='https://gateway-wdc.watsonplatform.net/text-to-speech/api'
	)

	# Continually scan for questions
	while True:
		# Grab a frame from the stream
		# ret, frame = cam.read()
		# Convert the image to grayscale
		# gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		# Decode the QR code
		# question = decode(gray)

		# If there was no readable QR code, then retry
		if len(question) != 1  :
			continue
		else:
			with open('speech.wav', 'wb') as audio_file:
				audio_file.write(
					text_to_speech.synthesize(
						question[0].data,
						'audio/wav',
						'en-GB_KateVoice'
					).get_result().content)
			os.system("omxplayer speech.wav")
			break
			# s.send(question.data)

		# answer = s.recv(socket_size)




	# Messages should be sent in bytes b' '
	s.close()

if __name__ == "__main__":

	parser = argparse.ArgumentParser()
	parser.add_argument('-sip', help="Server IP Address", type=str)
	parser.add_argument('-sp', help="Server Port", type=int, default=0)
	parser.add_argument('-z', help="Socket Size", type=int, default=0)

	if len(sys.argv) != 7 and sys.argv[1] != "-h" and sys.argv[1] != "--help":
		print("Error: Too few arguemnts")
	else: 
		main(parser.parse_args(sys.argv[1:]))
